from .base import BaseModel
from .schemas.statutes import (
    structure_schema,
    content_schema,
    edge_schema)


class StructureNode(BaseModel):
    """
    Details for a statute structural node.
    """

    _type = 'statute_node'
    _schema = structure_schema
    _collection = 'statute_nodes'

    __slots__ = ('division', 'enum', 'heading', 'order', 'status')
    _other_name_slots = ('start_date', 'end_date', 'notes')

    def __init__(self, order, division=None, enum=None, heading=None, **kwargs):
        super(StructureNode, self).__init__()
        self.division = division
        self.enum = enum
        self.heading = heading
        self.order = order
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __repr__(self):
        as_dict = self.as_dict()
        list(map(as_dict.pop, ('_type', '_id',)))
        args = (self.__class__.__name__, as_dict)
        return '%s(**%r)' % args


class ContentNode(StructureNode):
    """
    Details for a statute structural node.

    Also need optional info about states (for relealed/omitted but
    still displayed statutes).
    """
    _schema = content_schema
    __slots__ = (
        'division', 'enum', 'heading', 'order', 'children', 'status',
        'notes', 'history')

    def __repr__(self):
        as_dict = self.as_dict()
        list(map(as_dict.pop, ('_type', '_id',)))
        args = (self.__class__.__name__, as_dict)
        return '%s(**%r)' % args


class Edge(BaseModel):
    """
    Details for a statute ende.
    """
    _type = 'statute_edge'
    _schema = edge_schema
    _collection = 'statute_edges'

    __slots__ = ('out_id', 'in_id',)

    def __init__(self, in_obj, out_obj):
        super(Edge, self).__init__()
        if isinstance(in_obj, (StructureNode,)):
            self.in_id = in_obj._id
        if isinstance(out_obj, (StructureNode,)):
            self.out_id = out_obj._id

    def __repr__(self):
        as_dict = self.as_dict()
        list(map(as_dict.pop, ('_type', '_id',)))
        args = (self.__class__.__name__, as_dict)
        return '%s(**%r)' % args
