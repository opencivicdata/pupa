from .base import BaseModel, LinkMixin
from .schemas.post import schema


class Post(BaseModel, LinkMixin):
    """
    A popolo-style Post
    """

    _type = 'post'
    _schema = schema
    _collection = 'posts'

    def __init__(self, label, role, **kwargs):
        super(Post, self).__init__()
        self.label = label
        self.role = role
        self.organization_id = None
        self.start_date = None
        self.end_date = None
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __str__(self):
        return self.label
