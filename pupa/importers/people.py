from .base import BaseImporter


class PersonImporter(BaseImporter):
    _type = 'person'

    def get_db_spec(self, person):
        spec = {'$or': [{'name': person['name']},
                        {'other_names': person['name']}],}

        if 'chamber' in person:
            spec['chamber'] = person['chamber']
        if 'district' in person:
            spec['district'] = person['district']
        if 'jurisdiction_id' in person:
            spec['jurisdiction_id'] = person['jurisdiction_id']

        return spec
