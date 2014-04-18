""" these are helper classes for object creation during the scrape """
from pupa.models import Person, Organization, Membership


class Legislator(Person):
    _is_legislator = True

    def __init__(self, name, district, party=None, chamber=None, role='member', **kwargs):
        super(Legislator, self).__init__(name, **kwargs)
        self._district = district
        self._party = party
        self._chamber = chamber
        self._contact_details = []
        self._role = role

    def add_membership_contact(self, type, value, note):
        self._contact_details.append({'type': type, 'value': value, 'note': note})

    def add_committee_membership(self, com_name, role='member'):
        org = Organization(com_name, classification='committee')
        self.add_membership(org, role=role)
        org.sources = self.sources
        self._related.append(org)


class Committee(Organization):

    def __init__(self, *args, **kwargs):
        super(Committee, self).__init__(*args, **kwargs)

    def add_member(self, name, role='member', **kwargs):
        membership = Membership(None, self._id, role=role, _unmatched_legislator={'name': name},
                                **kwargs)
        self._related.append(membership)
