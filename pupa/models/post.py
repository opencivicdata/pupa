from .base import BaseModel
from .schemas.post import schema


class Post(BaseModel):
    """
    A popolo-style Post
    """

    _type = 'post'
    _schema = schema
    _collection = 'posts'
    __slots__ = ('label', 'role', 'organization_id', 'start_date', 'end_date',
                 'contact_details', 'links')

    def __init__(self, label, role, **kwargs):
        super(Post, self).__init__()
        self.label = label
        self.role = role
        self.organization_id = None
        self.start_date = None
        self.end_date = None
        self.contact_details = []
        self.links = []
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __str__(self):
        return self.label
