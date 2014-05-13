""" these are helper classes for object creation during the scrape """
import json
from .popolo import Person, Organization, Membership


def make_psuedo_id(**kwargs):
    """ psuedo ids are just JSON """
    return '~' + json.dumps(kwargs)


def get_psuedo_id(pid):
    if pid[0] != '~':
        raise ValueError("psuedo id doesn't start with ~")
    return json.loads(pid[1:])


class Legislator(Person):
    """
    Legislator is a special case of Person that has a district, party, and perhaps a chamber
    """
    def __init__(self, name, district, party=None, chamber='', role='member', **kwargs):
        super(Legislator, self).__init__(name, **kwargs)
        self._district = district
        self._party = party
        self._chamber = chamber
        self._role = role

    def pre_save(self, jurisdiction_id):
        # before saving create a membership to the current jurisdiction

        #post_id='district:' + (self._chamber or '') + ':' + self._district,
        post_kwargs = {
            "label": self._district,
        }
        if self._chamber:
            post_kwargs['chamber'] = self._chamber

        membership = Membership(
            person_id=self._id,
            organization_id=make_psuedo_id(classification="legislature", chamber=self._chamber),
            # post placeholder id is district:chamber:name
            #post_id='district:' + (self._chamber or '') + ':' + self._district,
            post_id=make_psuedo_id(**post_kwargs),
            role=self._role)
        self._related.append(membership)

        # create a party membership
        if self._party:
            membership = Membership(self._id,
                                    make_psuedo_id(classification="party", name=self._party),
                                    role='member')
            self._related.append(membership)


class Committee(Organization):
    """
    Committee is a special Organization that makes it easy to add members
    """

    def __init__(self, name, chamber='', **kwargs):
        super(Committee, self).__init__(name=name, classification='committee', chamber=chamber,
                                        **kwargs)

    def pre_save(self, jurisdiction_id):
        # before saving set parent to the chamber
        if not self.parent_id:
            self.parent_id = make_psuedo_id(classification='legislature', chamber=self.chamber)

    def add_member(self, name_or_person, role='member', **kwargs):
        if isinstance(name_or_person, Person):
            membership = Membership(person_id=name_or_person._id, organization_id=self._id,
                                    role=role, **kwargs)
        else:
            membership = Membership(person_id=make_psuedo_id(name=name_or_person),
                                    organization_id=self._id, role=role, **kwargs)
        self._related.append(membership)
