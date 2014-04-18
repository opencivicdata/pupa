from pupa.scrape.models import Person
from .base import BaseImporter, db


class PersonImporter(BaseImporter):
    _type = 'person'
    _model_class = Person

    def __init__(self, jurisdiction_id):
        super(PersonImporter, self).__init__(jurisdiction_id)
        # get list of all people w/ memberships in this org
        self.person_ids = db.memberships.find(
            {'jurisdiction_id': jurisdiction_id}).distinct('person_id')

    def prepare_object_from_json(self, obj):
        return obj

    def get_db_spec(self, person):
        spec = {'$or': [{'name': person.name},
                        {'other_names': person.name}],
                '_id': {'$in': self.person_ids}}

        return spec
