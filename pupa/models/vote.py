from .base import BaseModel
from .schemas.vote import schema


class Vote(BaseModel):
    """
    """
    _type = "vote"
    _schema = schema
    __slots__ = ("session", "chamber", "date", "motion", "type", "passed",
                 "organization", "organization_id", "bill", "vote_counts",
                 "roll_call", "sources", '_openstates_id', 'jurisdiction_id',
                 'identifiers')

    def __init__(self, organization, session, date, motion, type, passed,
                 yes_count, no_count, other_count=0, organization_id=None,
                 chamber=None, **kwargs):

        super(Vote, self).__init__()

        if not isinstance(type, list):
            type = [type]

        self.organization = organization
        self.organization_id = organization_id
        self.session = session
        self.date = date
        self.motion = motion
        self.type = type
        self.passed = passed
        self.chamber = chamber
        self.roll_call = []

        self.vote_counts = [
            {"vote_type": "yes", "count": yes_count},
            {"vote_type": "no", "count": no_count},
            {"vote_type": "other", "count": other_count},
        ]

        for k, v in kwargs.items():
            setattr(self, k, v)

    def __str__(self):
        return u'{0} - {1} - {2}'.format(self.session, self.date, self.motion)

    __unicode__ = __str__

    def add_bill(self, name, id=None, chamber=None):
        self.bill = {
            "id": id,
            "name": name,
            "chamber": chamber
        }

    def vote(self, name, how, id=None):
        self.roll_call.append({
            "vote_type": how,
            "person": {
                "name": name,
                "id": id,
            }
        })

    def yes(self, name, id=None, **kwargs):
        return self.vote(name, 'yes', id=id, **kwargs)

    def no(self, name, id=None, **kwargs):
        return self.vote(name, 'no', id=id, **kwargs)

    def other(self, name, id=None, **kwargs):
        return self.vote(name, 'other', id=id, **kwargs)
