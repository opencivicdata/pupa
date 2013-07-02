from .base import BaseImporter, db


class PersonImporter(BaseImporter):
    _type = 'person'

    def __init__(self, jurisdiction_id):
        super(PersonImporter, self).__init__(jurisdiction_id)
        # get list of all people w/ memberships in this org
        self.person_ids = db.memberships.find(
            {'jurisdiction_id': jurisdiction_id}).distinct('person_id')

    def prepare_object_from_json(self, obj):
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
