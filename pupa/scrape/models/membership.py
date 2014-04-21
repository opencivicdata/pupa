from .base import BaseModel, ContactDetailMixin, LinkMixin
from .schemas.membership import schema


class Membership(BaseModel, ContactDetailMixin, LinkMixin):
    """
    A popolo-style Membership.
    """

    _type = 'membership'
    _schema = schema

    def __init__(self, person_id, organization_id, **kwargs):
        """
        Constructor for the Membership object.

        We require a person ID and organization ID, as required by the
        popolo spec. Additional arguments may be given, which match those
        defined by popolo.
        """
        super(Membership, self).__init__()
        self.person_id = person_id
        self.organization_id = organization_id
        self.start_date = ''
        self.end_date = ''
        self.role = ''
        self.label = ''
        self.post_id = None
        self.on_behalf_of_id = None
        self._unmatched_legislator = None

        for k, v in kwargs.items():
            setattr(self, k, v)

    def __str__(self):
        if self.person_id:
            return self.person_id + ' membership in ' + self.organization_id
        else:
            return (self._unmatched_legislator['name'] + ' membership in ' + self.organization_id)
    __unicode__ = __str__
