from opencivicdata.models import Post, PostContactDetail, PostLink
from .base import BaseImporter


class PostImporter(BaseImporter):
    _type = 'post'
    model_class = Post
    related_models = {'contact_details': (PostContactDetail, 'post_id', {}),
                      'links': (PostLink, 'post_id', {})
                     }

    def __init__(self, jurisdiction_id, org_importer):
        super(PostImporter, self).__init__(jurisdiction_id)
        self.org_importer = org_importer

    def prepare_for_db(self, data):
        data['organization_id'] = self.org_importer.resolve_json_id(data['organization_id'])
        return data

    def get_object(self, data):
        return self.model_class.objects.get(organization_id=data['organization_id'],
                                            label=data['label'])

    def limit_spec(self, spec):
        spec['organization__jurisdiction_id'] = self.jurisdiction_id
        return spec
