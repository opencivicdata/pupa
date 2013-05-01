""" these are helper classes for object creation during the scrape """
from larvae.person import Person
from larvae.organization import Organization


class Legislator(Person):
    _type = 'person'
    _is_legislator = True
    __slots__ = ('district', 'party', 'chamber', '_contact_details')

    def __init__(self, name, district, party=None, chamber=None, **kwargs):
        super(Legislator, self).__init__(name, **kwargs)
        self.district = district
        self.party = party
        self.chamber = chamber
        self._contact_details = []

    def add_contact(self, type, value, group):
        self._contact_details.append({'type': type, 'value': value,
                                      'group': group})

    def add_committee_membership(self, com_name, role='member'):
        org = Organization(com_name, classification='committee')
        self.add_membership(org, role=role)
        self._related.append(org)
