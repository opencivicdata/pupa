from .base import BaseImporter, update_object, insert_object
from pupa.core import db


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
                'end_date': membership.get('end_date')
               }

        if 'unmatched_legislator' in membership:
            spec['unmatched_legislator'] = membership['unmatched_legislator']

        return spec

    def prepare_object_from_json(self, obj):
        org_json_id = obj['organization_id']
        obj['organization_id'] = self.org_importer.resolve_json_id(org_json_id)
        person_json_id = obj['person_id']
        obj['person_id'] = self.person_importer.resolve_json_id(person_json_id)
        return obj

    def import_object(self, obj):
        spec = self.get_db_spec(obj)

        if 'unmatched_legislator' in obj and obj['unmatched_legislator']:
            # Let's get all the people in our jurisdiction, firstly.
            people = db.memberships.find({
                "jurisdiction_id": obj['jurisdiction_id']
            }).distinct('person_id')  # Everyone in the Jurisdiction
            if None in people:
                people.remove(None)
            # Right, now we have a list of all known people in the
            # jurisdiction.

            unmatched_name = obj['unmatched_legislator']['name']
            people = db.people.find({
                "_id": {"$in": people},
                "$or": [
                    { "name": unmatched_name },
                    { "other_names": unmatched_name },
                ]
            })
            # Now we've got all the people that have this name in the
            # jurisdiction

            # - if one result:
            if people.count() == 1:
                person = people[0]
                #   + update membership with this person's details (if it's
                #     not there already)
                obj['person_id'] = person['_id']
                obj.pop('unmatched_legislator')
                spec = self.get_db_spec(obj)
            else:
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


        db_obj = self.collection.find_one(spec)
        if db_obj:
            _id, updated = update_object(db_obj, obj)
            self.results['update' if updated else 'noop'] += 1
        else:
            _id = insert_object(obj)
            self.results['insert'] += 1

        return _id
