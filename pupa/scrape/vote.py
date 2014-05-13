from .base import BaseModel, make_psuedo_id, cleanup_list, SourceMixin
from .bill import Bill
from .popolo import Organization
from .schemas.vote import schema


class Vote(BaseModel, SourceMixin):
    _type = 'vote'
    _schema = schema

    def __init__(self, session, motion, start_date, classification, outcome, bill=None,
                 organization=None, chamber=None, **kwargs):
        super(Vote, self).__init__()

        self.session = session
        self.motion = motion
        self.start_date = start_date
        self.classification = cleanup_list(classification, [])
        self.outcome = outcome
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
        return u'{0} - {1} - {2}'.format(self.session, self.start_date, self.motion)

    __unicode__ = __str__

    def set_bill(self, bill_or_name, chamber=None):
        # either set to bill's id or use a psuedo-id
        if isinstance(bill_or_name, Bill):
            if chamber:
                raise ValueError("set_bill takes no arguments when using a `Bill` object")
            self.bill = bill_or_name._id
        else:
            self.bill = make_psuedo_id(name=bill_or_name,
                                       bill__from_organization_classification='legislature',
                                       bill__from_organization_chamber=chamber)

    def vote(self, option, voter):
        self.votes.append({"option": option, "voter": voter})

    def yes(self, name, id=None):
        return self.vote('yes', name)

    def no(self, name, id=None):
        return self.vote('no', name)

    def set_count(self, option, count):
        print(self.counts)
        for co in self.counts:
            if co['option'] == option:
                co['count'] = count
                break
        else:
            self.counts.append({'option': option, 'count': count})
