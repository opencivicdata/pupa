from .base import BaseImporter, update_object, insert_object
from pupa.core import db


def people_by_jurisdiction(jurisdiction_id):
    """ Find all people by a jurisdiction """
    people_ids = db.memberships.find({
        "jurisdiction_id": jurisdiction_id,
    }).distinct('person_id')

    if None in people_ids:
        people_ids.remove(None)
    return people_ids


def people_by_name(name, people_ids=None):
    """ Find all people by their name. Optional people_ids _id constraint """
    spec = {"$or": [{ "name": name }, { "other_names": name }]}
    if people_ids is not None:
        # This isn't a raw if conditional, since you could pass
        # an empty list.
        spec["_id"] = {"$in": people_ids}
    return db.people.find(spec)


def people_by_jurisdiction_and_name(jurisdiction_id, name):
    people_ids = people_by_jurisdiction(jurisdiction_id)
    people = people_by_name(name, people_ids=people_ids)
    return people


def match_membership(membership, people=None):
    if ('unmatched_legislator' in membership
            and membership['unmatched_legislator']):

        if people is None:
            unmatched_name = membership['unmatched_legislator']['name']
            people = people_by_jurisdiction_and_name(
                unmatched_name,
                membership['jurisdiction_id'],
            )

        if people.count() == 1:
            person = people[0]
            #   + update membership with this person's details (if it's
            #     not there already)
            membership['person_id'] = person['_id']
            membership.pop('unmatched_legislator')
            return (True, membership)
    return (False, membership)


class MembershipImporter(BaseImporter):
    _type = 'membership'

    def __init__(self, jurisdiction_id, person_importer, org_importer):
        super(MembershipImporter, self).__init__(jurisdiction_id)
        self.person_importer = person_importer
        self.org_importer = org_importer

    def get_db_spec(self, membership):
        spec = {'organization_id': membership['organization_id'],
                'person_id': membership['person_id'],
                'role': membership['role'],
                # if this is a historical role, only update historical roles
                'end_date': membership.get('end_date')}

        if 'post_id' in membership and membership['post_id']:
            spec['post_id'] = membership['post_id']

        if ('unmatched_legislator' in membership and
                membership['unmatched_legislator']):

            spec['unmatched_legislator'] = membership['unmatched_legislator']
            unmatched_name = membership['unmatched_legislator']['name']

            people = people_by_jurisdiction_and_name(
                membership['jurisdiction_id'],
                unmatched_name,
            )

            matched, membership = match_membership(membership, people=people)

            if matched:
                # We were able to simply match. Let's roll with this.
                spec = self.get_db_spec(membership)

                # OK. Since we matched, let's also update existing
                # copies of this guy.

                #### This will find anyone who has our ID *OR* has a None.
                pspec = spec.copy()
                pspec['person_id'] = membership['person_id']

                uspec = spec.copy()
                uspec['person_id'] = None
                spec = {"$or": [pspec, uspec]}
                return spec

            #### This will find anyone who has our name *OR* has a None.
            # (not the same code as above)
            pspec = spec.copy()
            pspec['person_id'] = {"$in": people.distinct("_id")}
            pspec.pop('unmatched_legislator')
            # Either we have this person, who's already matched (e.g.
            # everything already matches)

            uspec = spec.copy()
            uspec['person_id'] = None
            # Or we don't, and we need to find a membership with an
            # unmatched ID
            spec = {"$or": [pspec, uspec]}
        return spec

    def prepare_object_from_json(self, obj):
        org_json_id = obj['organization_id']
        obj['organization_id'] = self.org_importer.resolve_json_id(org_json_id)
        person_json_id = obj['person_id']
        obj['person_id'] = self.person_importer.resolve_json_id(person_json_id)
        return obj
