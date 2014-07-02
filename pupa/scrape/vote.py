from ..utils import make_psuedo_id
from .base import BaseModel, cleanup_list, SourceMixin
from .bill import Bill
from .popolo import Organization
from .schemas.vote import schema


class Vote(BaseModel, SourceMixin):
    _type = 'vote'
    _schema = schema

    def __init__(self, *, legislative_session, motion_text, start_date, classification, result,
                 identifier='', bill=None, organization=None, chamber=None, **kwargs):
        super(Vote, self).__init__()

        self.legislative_session = legislative_session
        self.motion_text = motion_text
        self.motion_classification = cleanup_list(classification, [])
        self.start_date = start_date
        self.result = result
        self.identifier = identifier
        self.organization = organization

        self.set_bill(bill)
        self.votes = []
        self.counts = []

        if organization and chamber:
            raise ValueError('cannot specify both chamber and organization')
        elif chamber:
            self.organization = make_psuedo_id(classification='legislature', chamber=chamber)
        elif organization:
            if isinstance(organization, Organization):
                self.organization = organization._id
            else:
                self.organization = make_psuedo_id(**organization)
        else:
            # neither specified
            self.organization = make_psuedo_id(classification='legislature')

    def __str__(self):
        return u'{0} - {1} - {2}'.format(self.legislative_session, self.start_date,
                                         self.motion_text)

    __unicode__ = __str__

    def set_bill(self, bill_or_identifier, *, chamber=None):
        if not bill_or_identifier:
            self.bill = None
        elif isinstance(bill_or_identifier, Bill):
            if chamber:
                raise ValueError("set_bill takes no arguments when using a `Bill` object")
            self.bill = bill_or_identifier._id
        else:
            kwargs = {'identifier': bill_or_identifier,
                      'from_organization__classification': 'legislature'}
            if chamber:
                kwargs['from_organization__chamber'] = chamber
            self.bill = make_psuedo_id(**kwargs)

    def vote(self, option, voter):
        self.votes.append({"option": option, "voter_name": voter})

    def yes(self, name, *, id=None):
        return self.vote('yes', name)

    def no(self, name, *, id=None):
        return self.vote('no', name)

    def set_count(self, option, value):
        for co in self.counts:
            if co['option'] == option:
                co['value'] = value
                break
        else:
            self.counts.append({'option': option, 'value': value})
