from ..utils import make_pseudo_id
from .base import BaseModel, cleanup_list, SourceMixin
from .bill import Bill
from .popolo import pseudo_organization
from .schemas.vote_event import schema


class VoteEvent(BaseModel, SourceMixin):
    _type = 'vote_event'
    _schema = schema

    def __init__(self, *, motion_text, start_date, classification, result,
                 legislative_session=None,
                 identifier='', bill=None, bill_chamber=None, organization=None, chamber=None):
        super(VoteEvent, self).__init__()

        self.legislative_session = legislative_session
        self.motion_text = motion_text
        self.motion_classification = cleanup_list(classification, [])
        self.start_date = start_date
        self.result = result
        self.identifier = identifier

        self.set_bill(bill, chamber=bill_chamber)

        if isinstance(bill, Bill) and not self.legislative_session:
            self.legislative_session = bill.legislative_session

        if not self.legislative_session:
            raise ValueError('must set legislative_session or bill')

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
                raise ValueError("set_bill takes no arguments when using a `Bill` object")
            self.bill = bill_or_identifier._id
        else:
            if chamber is None:
                chamber = 'legislature'
            kwargs = {'identifier': bill_or_identifier,
                      'from_organization__classification': chamber}
            self.bill = make_pseudo_id(**kwargs)

    def vote(self, option, voter, *, note=''):
        self.votes.append({"option": option, "voter_name": voter,
                           "voter_id": make_pseudo_id(name=voter), 'note': note})

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
