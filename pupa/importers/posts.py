from opencivicdata.models import Post, PostContactDetail, PostLinks
from .base import BaseImporter


class PostImporter(BaseImporter):
    _type = 'post'
    model_class = Post
    related_models = {'contact_details': PostContactDetail, 'links': PostLinks}

    def __init__(self, jurisdiction_id, org_importer):
        super(PostImporter, self).__init__(jurisdiction_id)
        self.org_importer = org_importer

    def prepare_for_db(self, data):
        data['organization_id'] = self.org_importer.resolve_json_id(data['organization_id'])
        return data

    def get_object(self, data):
        return self.model_class.objects.get(organization_id=data['organization_id'],
                                            label=data['label'])

    def resolve_json_id(self, json_id):
        if json_id.startswith('district:'):
            _, chamber, id_piece = json_id.split(':', 2)
            return Post.objects.get(organization__chamber=chamber, label=id_piece).id

        return super(PostImporter, self).resolve_json_id(json_id)
