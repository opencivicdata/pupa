from .base import BaseModel
from .bill import Bill
from .schemas.vote import schema


class Vote(BaseModel):
    """
    """
    _type = 'vote'
    _schema = schema
    _collection = 'votes'
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

    def set_bill(self, what, id=None, chamber=None):
        """
        COMPLEX BEHAVIOR AHOY:

            If `what` is a `Bill` object, this will correctly link without
            needing *anything* else.

            If `what` is not a `Bill` object, this will set `bill.name` to this
            value, and apply the rest of the keywords to the `bill` attribute.
        """
        if isinstance(what, Bill):
            if id or chamber:
                raise TypeError("set_bill takes no arguments "
                                "when using a `Bill` object")
            return self._set_bill_obj(what)
        return self._set_bill_raw(name=what, id=id, chamber=chamber)

    def _set_bill_raw(self, name, id=None, chamber=None):
        self.bill = {
            "id": id,
            "name": name,
            "chamber": chamber
        }

    def _set_bill_obj(self, bill):
        self._set_bill_raw(name=bill.name, id=bill._id)
        if hasattr(bill, 'chamber') and bill.chamber:
            self.bill['chamber'] = bill.chamber

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
