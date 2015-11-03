import pytest
from pupa.scrape.schemas.person import schema
from pupa.scrape.base import (BaseModel, SourceMixin, ContactDetailMixin, LinkMixin,
                              AssociatedLinkMixin, OtherNameMixin, IdentifierMixin)


class GenericModel(BaseModel, SourceMixin, ContactDetailMixin, LinkMixin, AssociatedLinkMixin,
                   OtherNameMixin, IdentifierMixin):
    """ a generic model used for testing the base and mixins """

    _type = "generic"
    _schema = schema

    def __init__(self):
        super(GenericModel, self).__init__()
        self._associated = []


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
    m.add_source('http://example.com/2', note='xyz')
    assert m.sources == [{'url': 'http://example.com/1', 'note': ''},
                         {'url': 'http://example.com/2', 'note': 'xyz'}]


def test_add_contact_detail():
    m = GenericModel()
    m.add_contact_detail(type='fax', value='111-222-3333', note='office')
    assert m.contact_details == [{'type': 'fax', 'value': '111-222-3333', 'note': 'office'}]


def test_add_link():
    m = GenericModel()
    m.add_link('http://example.com/1')
    m.add_link('http://example.com/2', note='xyz')
    assert m.links == [{'url': 'http://example.com/1', 'note': ''},
                       {'url': 'http://example.com/2', 'note': 'xyz'}]


def test_add_associated_link_match():
    m = GenericModel()
    m._add_associated_link('_associated', 'something', 'http://example.com/1.txt',
                           text='', media_type='text/plain', on_duplicate='error')
    m._add_associated_link('_associated', 'something', 'http://example.com/1.pdf',
                           text='', media_type='application/pdf', on_duplicate='error')
    # one 'document' added, multiple links for it
    assert len(m._associated) == 1
    assert len(m._associated[0]['links']) == 2


def test_add_associated_link_on_duplicate_bad():
    m = GenericModel()

    with pytest.raises(ValueError):
        m._add_associated_link('_associated', 'something', 'http://example.com',
                               text='', media_type='text/html', on_duplicate='idk')


def test_add_associated_link_on_duplicate_error():
    m = GenericModel()
    m._add_associated_link('_associated', 'something', 'http://example.com',
                           text='', media_type='text/html', on_duplicate='error')

    with pytest.raises(ValueError):
        m._add_associated_link('_associated', 'something else', 'http://example.com',
                               text='', media_type='text/html', on_duplicate='error')


def test_add_associated_link_on_duplicate_ignore():
    m = GenericModel()
    m._add_associated_link('_associated', 'something', 'http://example.com',
                           text='', media_type='text/html', on_duplicate='ignore')
    m._add_associated_link('_associated', 'something else', 'http://example.com',
                           text='', media_type='text/html', on_duplicate='ignore')
    # one 'document' added, single link for it, keeps first name
    assert len(m._associated) == 1
    assert len(m._associated[0]['links']) == 1
    assert m._associated[0]['note'] == 'something'


def test_add_name():
    m = GenericModel()

    m.add_name("Thiston", note="What my friends call me")

    assert m.other_names == [{"name": "Thiston", "note": "What my friends call me"}]

    m.add_name("Johnseph Q. Publico", note="Birth name", start_date="1920-01",
               end_date="1949-12-31")

    assert m.other_names == [
        {"name": "Thiston", "note": "What my friends call me"},
        {"name": "Johnseph Q. Publico", "note": "Birth name", "start_date": "1920-01",
         "end_date": "1949-12-31"}
    ]


def test_add_identifier():
    g = GenericModel()

    with pytest.raises(TypeError):
        g.add_identifier("id10t", foo="bar")

    g.add_identifier("id10t")
    g.add_identifier("l0l", scheme="kruft")

    assert g.identifiers[-1]['scheme'] == "kruft"
    assert g.identifiers[0]['identifier'] == "id10t"
