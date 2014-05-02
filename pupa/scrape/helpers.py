""" these are helper classes for object creation during the scrape """
from .popolo import Person, Organization, Membership


class Legislator(Person):
    def __init__(self, name, district, party=None, chamber=None, role='member', **kwargs):
        super(Legislator, self).__init__(name, **kwargs)
        self._district = district
        self._party = party
        self._chamber = chamber
        self.contact_details = []
        self._role = role

    def add_membership_contact(self, type, value, note):
        self.contact_details.append({'type': type, 'value': value, 'note': note})

    def add_committee_membership(self, com_name, role='member'):
        org = Organization(com_name, classification='committee')
        self.add_membership(org, role=role)
        org.sources = self.sources
        self._related.append(org)

    def prepare(self, jurisdiction_id):
        membership = Membership(
            self._id,
            # placeholder id is jurisdiction:chamber:id
            'jurisdiction:' + (self._chamber or '') + ':' + jurisdiction_id,
            # post placeholder id is district:chamber:name
            post_id='district:' + (self._chamber or '') + ':' + self._district,
            # contact_details=self._contact_details,
            # XXX: Removed since we're moving contact_details to the top
            #      level.
            role=self._role)
        # remove placeholder _contact_details
        # del self._contact_details
        del self._role
        self._related.append(membership)

        # create a party membership
        if self._party:
            membership = Membership(self._id, 'party:' + self.party, role='member')
            self._related.append(membership)


class Committee(Organization):

    def __init__(self, *args, **kwargs):
        super(Committee, self).__init__(*args, **kwargs)

    def add_member(self, name, role='member', **kwargs):
        membership = Membership(None, self._id, role=role, _unmatched_legislator={'name': name},
                                **kwargs)
        self._related.append(membership)
