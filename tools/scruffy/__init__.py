from .core import db


class Check(dict):
    def __init__(self, collection, id, tagname, severity, data=None):
        self['collection'] = collection
        self['id'] = id
        self['tagname'] = tagname
        self['severity'] = severity
        if data:
            self['data'] = data
