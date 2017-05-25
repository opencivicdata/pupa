from opencivicdata.core.models import Post, PostContactDetail, PostLink
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

    def get_object(self, post):
        spec = {
            'organization_id': post['organization_id'],
            'label': post['label'],
        }

        if post['role']:
            spec['role'] = post['role']

        return self.model_class.objects.get(**spec)

    def limit_spec(self, spec):
        spec['organization__jurisdiction_id'] = self.jurisdiction_id
        return spec
