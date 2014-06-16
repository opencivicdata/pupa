import pytest
from validictory import ValidationError
from pupa.scrape import Bill
from pupa.utils.generic import get_psuedo_id


def toy_bill():
    b = Bill(name="HB 2017", session="2012A",
             title="A bill for an act to raise the cookie budget by 200%",
             from_organization="Foo Senate", classification="bill")
    b.add_source("http://uri.example.com/", note="foo")
    return b


def test_basic_valid_bill():
    b = toy_bill()
    b.validate()
    assert 'we got here'


def test_bill_type_setting():
    # default
    b = Bill(name="some bill", session="session", title="the title")
    assert b.classification == ["bill"]

    # string -> list
    b = Bill(name="some bill", session="session", title="the title", classification="string")
    assert b.classification == ["string"]

    # list unmodified
    b = Bill(name="some bill", session="session", title="the title",
             classification=["two", "items"])
    assert b.classification == ["two", "items"]

    # tuple -> list
    b = Bill(name="some bill", session="session", title="the title",
             classification=("two", "items"))
    assert b.classification == ["two", "items"]


def test_basic_invalid_bill():
    """ Test that we can create an invalid bill, and validation will fail """
    b = toy_bill()
    b.name = None
    with pytest.raises(ValueError):
        b.validate()


def test_from_organization():
    # none set
    assert ((get_psuedo_id(Bill('HB 1', '2014', 'Some Bill').from_organization) ==
             {'classification': 'legislature'}))

    # chamber set
    assert (get_psuedo_id(Bill('HB 1', '2014', 'Some Bill', chamber='upper').from_organization) ==
            {'chamber': 'upper', 'classification': 'legislature'})
    # org direct set
    assert Bill('HB 1', '2014', 'Some Bill', from_organization='test').from_organization == 'test'

    # can't set both
    with pytest.raises(ValueError):
        Bill('HB 1', '2014', 'Some Bill', from_organization='upper', chamber='upper')


def test_add_action():
    """ Make sure actions work """
    b = toy_bill()
    b.add_action("Some dude liked it.", "2013-04-29", chamber='lower')
    assert len(b.actions) == 1
    assert b.actions[0]['text'] == 'Some dude liked it.'
    assert get_psuedo_id(b.actions[0]['organization_id']) == {'classification': 'legislature',
                                                              'chamber': 'lower'}
    assert b.actions[0]['date'] == '2013-04-29'
    b.validate()


def test_add_related_bill():
    """ Make sure related bills work """
    b = toy_bill()
    b.add_related_bill(name="HB 2020", session="2011A", relation_type="companion")
    assert len(b.related_bills) == 1
    assert b.related_bills[0] == {'name': 'HB 2020', 'session': '2011A',
                                  'relation_type': 'companion'}
    b.validate()


def test_add_sponsor():
    b = toy_bill()
    b.add_sponsor(name="Joe Bleu", classification="Author", entity_type="person", primary=True,
                  chamber="upper")
    assert len(b.sponsors) == 1
    assert b.sponsors[0] == {'person_id': None, 'name': 'Joe Bleu', 'classification': 'Author',
                             'entity_type': 'person', 'primary': True}
    b.validate()


def test_subjects():
    b = toy_bill()
    b.add_subject("Foo")
    b.add_subject("Bar")
    assert b.subject == ['Foo', 'Bar']
    b.validate()


def test_summaries():
    b = toy_bill()
    b.add_summary('this bill is stupid', 'K-5')
    b.add_summary('this legislative document is ignorant', '6-12')
    assert b.summaries == [{'note': 'K-5', 'text': 'this bill is stupid'},
                           {'note': '6-12', 'text': 'this legislative document is ignorant'}]


def test_add_documents():
    b = toy_bill()

    # should only add one document since they all have same name
    b.add_document_link(name="Fiscal Impact", date="2013-04", url="http://hi.example.com/foo#bar",
                        mimetype="text/html")
    b.add_document_link(name="Fiscal Impact", date="2013-04", url='http://foobar.baz')
    assert len(b.documents) == 1

    # should now be two documents
    b.add_document_link(name="Other Document", date="2013-04", url='http://foobar.baz/other')
    assert len(b.documents) == 2

    # valid documents so far
    b.validate()

    # an invalid document
    b.add_document_link(name="Fiscal Impact", date="2013-04", url=None, mimetype='foo')
    with pytest.raises(ValidationError):
        b.validate()


def test_versions():
    b = toy_bill()

    # only one document, multiple links
    b.add_version_link(url="http://pault.ag/", name="Final Version", date="2013-04")
    b.add_version_link(url="http://pault.ag/foo", name="Final Version", date="2013-04")
    b.validate()
    assert len(b.versions) == 1
    assert len(b.versions[0]['links']) == 2

    # duplicate!
    with pytest.raises(ValueError):
        b.add_version_link(url="http://pault.ag/foo", name="Final Version", date="2013-04")

    # ignore duplicate - nothing should change
    b.add_version_link(url="http://pault.ag/foo", name="Final Version", date="2013-04",
                       on_duplicate='ignore')
    assert len(b.versions) == 1
    assert len(b.versions[0]['links']) == 2

    # duplicate URL
    with pytest.raises(ValueError):
        b.add_version_link(url="http://pault.ag/foo", name="Finals Versions", date="2013-04")
    assert len(b.versions) == 1
    assert len(b.versions[0]['links']) == 2

    # a new doc, numbers go up
    b.add_version_link(url="http://pault.ag/foovbar", name="Finals Versions", date="2013-04")
    assert len(b.versions) == 2
    assert len(b.versions[1]['links']) == 1

    # still validates
    b.validate()


def test_str():
    b = toy_bill()
    assert b.name in str(b)
