from .base import BaseImporter, db, update_object, insert_object


class PersonImporter(BaseImporter):
    _type = 'person'

    def __init__(self, jurisdiction_id):
        super(PersonImporter, self).__init__(jurisdiction_id)
        # get list of all people w/ memberships in this org
        self.person_ids = db.memberships.find(
            {'jurisdiction_id': jurisdiction_id}).distinct('person_id')

    def prepare_object_from_json(self, obj):
        if 'party' in obj:
            obj.pop('party')
        return obj

    def get_db_spec(self, person):
        spec = {'$or': [{'name': person['name']},
                        {'other_names': person['name']}],
                '_id': {'$in': self.person_ids}
               }

        if 'chamber' in person:
            spec['chamber'] = person['chamber']
        if 'district' in person:
            spec['district'] = person['district']

        return spec

    def preimport_hook(self, db_obj, obj):
        """
        This pre-import hook runs on a person to ensure that the other_name
        field is merged, since it may have entries in the database already.

        Currently we only merge other_names.
        """

        MERGE_FIELDS = ["other_names"]

        if db_obj:
            for field in MERGE_FIELDS:
                if field in db_obj and field in obj:
                    for entry in db_obj[field]:
                        if entry not in obj[field]:
                            obj[field].append(entry)
