import pytest
from pupa.scrape.schemas.person import schema
from pupa.scrape.base import (BaseModel, SourceMixin, ContactDetailMixin, LinkMixin,
                              AssociatedLinkMixin)

class GenericModel(BaseModel, SourceMixin, ContactDetailMixin, LinkMixin, AssociatedLinkMixin):
    """ a generic model used for testing the base and mixins """

    _type = "generic"
    _schema = schema


def test_init_id():
    m = GenericModel()
    assert len(m._id) == 36


def test_as_dict():
    m = GenericModel()
    assert m.as_dict()['_id'] == m._id


def test_setattr():
    m = GenericModel()

    with pytest.raises(ValueError):
        m.some_random_key = 3

    # and no error raised since this is a valid key
    m._id = 'new id'


def test_add_source():
    m = GenericModel()
    m.add_source('http://example.com/1')
    m.add_source('http://example.com/2', 'xyz')
    assert m.sources == [{'url': 'http://example.com/1', 'note': ''},
                         {'url': 'http://example.com/2', 'note': 'xyz'}]


def test_add_contact_detail():
    m = GenericModel()
    m.add_contact_detail('fax', '111-222-3333', 'office')
    assert m.contact_details == [{'type': 'fax', 'value': '111-222-3333', 'note': 'office'}]


def test_add_link():
    m = GenericModel()
    m.add_link('http://example.com/1')
    m.add_link('http://example.com/2', 'xyz')
    assert m.links == [{'url': 'http://example.com/1', 'note': ''},
                       {'url': 'http://example.com/2', 'note': 'xyz'}]
