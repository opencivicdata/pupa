from ..utils import _make_pseudo_id
from .base import BaseModel, cleanup_list, SourceMixin
from .bill import Bill
from .popolo import pseudo_organization
from .schemas.vote_event import schema
from pupa.exceptions import ScrapeValueError
import re


class VoteEvent(BaseModel, SourceMixin):
    _type = 'vote_event'
    _schema = schema

    def __init__(self, *, motion_text, start_date, classification, result,
                 legislative_session=None, identifier='',
                 bill=None, bill_chamber=None, bill_action=None,
                 organization=None, chamber=None
                 ):
        super(VoteEvent, self).__init__()

        self.legislative_session = legislative_session
        self.motion_text = motion_text
        self.motion_classification = cleanup_list(classification, [])
        self.start_date = start_date
        self.result = result
        self.identifier = identifier
        self.bill_action = bill_action

        self.set_bill(bill, chamber=bill_chamber)

        if isinstance(bill, Bill) and not self.legislative_session:
            self.legislative_session = bill.legislative_session

        if not self.legislative_session:
            raise ScrapeValueError('must set legislative_session or bill')

        self.organization = pseudo_organization(organization, chamber, 'legislature')
        self.votes = []
        self.counts = []

    def __str__(self):
        return '{0} - {1} - {2}'.format(self.legislative_session, self.start_date,
                                        self.motion_text)

    def set_bill(self, bill_or_identifier, *, chamber=None):
        if not bill_or_identifier:
            self.bill = None
        elif isinstance(bill_or_identifier, Bill):
            if chamber:
                raise ScrapeValueError("set_bill takes no arguments when using a `Bill` object")
            self.bill = bill_or_identifier._id
        else:
            if chamber is None:
                chamber = 'legislature'
            kwargs = {'identifier': bill_or_identifier,
                      'from_organization__classification': chamber,
                      'legislative_session__identifier': self.legislative_session
                      }
            self.bill = _make_pseudo_id(**kwargs)

    def vote(self, option, voter, *, note=''):
        self.votes.append({"option": option, "voter_name": voter,
                           "voter_id": _make_pseudo_id(name=voter), 'note': note})

    def yes(self, name, *, id=None, note=''):
        return self.vote('yes', name, note=note)

    def no(self, name, *, id=None, note=''):
        return self.vote('no', name, note=note)

    def set_count(self, option, value):
        for co in self.counts:
            if co['option'] == option:
                co['value'] = value
                break
        else:
            self.counts.append({'option': option, 'value': value})


class OrderVoteEvent:
    """ A functor for applying order to voteEvents.
        A single OrderVoteEvent instance should be used for all bills in a scrape.
        The vote events of each bill must be processed in chronological order,
            but the processing of bills may be interleaved (needed in e.g. NH).
        Currently, it only fudges midnight dates (start_date and end_date)
            by adding the event sequence number in seconds
            to the start_date and end_date (if they are well-formed string dates)
        In the future, when there is an 'order' field on voteEvents,
            it should fill that as well.
        This fails softly and silently;
            if a valid string date is not found in start_date or end_date, the date is not touched.
        This assumes that times are reported as local time, not UTC.
            A UTC time that is local midnight will not be touched.
        Sometimes one chamber reports the time of a vote,
            but the other chamber reports only the date.  This is handled.
        See the unit tests for examples and more behavior.
    """
    _midnight = r'\d\d\d\d-\d\d-\d\dT00:00:00.*'
    _timeless = r'\d\d\d\d-\d\d-\d\d'

    class OrderBillVoteEvent:
        """ Order VoteEvents for a single bill
        """

        def __init__(self):
            self.order = 0      # voteEvent sequence number. 1st voteEvent is 1.

        def __call__(self, voteEvent):

            self.order += 1
            voteEvent.start_date = self._adjust_date(voteEvent.start_date)
            if hasattr(voteEvent, 'end_date'):
                voteEvent.end_date = self._adjust_date(voteEvent.end_date)

        def _adjust_date(self, date):

            if not isinstance(date, str):
                return date

            if re.fullmatch(OrderVoteEvent._timeless, date):
                d2 = date + 'T00:00:00'
            elif re.fullmatch(OrderVoteEvent._midnight, date):
                d2 = date
            else:
                return date

            assert self.order <= 60*60
            mins = '{:02d}'.format(self.order // 60)
            secs = '{:02d}'.format(self.order % 60)

            # yyyy-mm-ddThh:mm:dd+05:00
            # 0123456789012345678
            return d2[:14] + mins + ':' + secs + d2[19:]

    def __init__(self):
        self.orderers = {}

    def __call__(self, session_id, bill_id, voteEvent):
        """
        Record order of voteEvent within bill.

        The "order" field is not yet implemented; this fudges voteEvent start_date and end_date.
        See OrderVoteEvent docstring for details.

        :param session_id: session id
        :param bill_id: an identifier for the vote's bill
            that is at least unique within the session.
        :param voteEvent:
        :return: None
        """
        bill_orderer = self.orderers.get((session_id, bill_id))

        if not bill_orderer:
            bill_orderer = self.OrderBillVoteEvent()
            self.orderers[(session_id, bill_id)] = bill_orderer

        bill_orderer(voteEvent)
