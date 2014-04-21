from .base import BaseModel, LinkMixin, ContactDetailMixin
from .schemas.post import schema


class Post(BaseModel, LinkMixin, ContactDetailMixin):
    """
    A popolo-style Post
    """

    _type = 'post'
    _schema = schema

    def __init__(self, label, role, organization_id, **kwargs):
        super(Post, self).__init__()
        self.label = label
        self.role = role
        self.organization_id = organization_id
        self.start_date = ''
        self.end_date = ''
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __str__(self):
        return self.label
