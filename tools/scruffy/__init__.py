from .core import db


class Check(dict):
    def __init__(self, collection, id, tagname, severity):
        self['collection'] = collection
        self['id'] = id
        self['tagname'] = tagname
        self['severity'] = severity
