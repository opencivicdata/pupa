from pupa.models import Bill
from nose.tools import raises
from validictory import ValidationError


def toy_bill():
    b = Bill(name="HB 2017",
             session="2012A",
             title="A bill for an act to raise the cookie budget by 200%",
             organization="Foo Senate",
             type="bill")
    b.add_source("http://uri.example.com/", note="foo")
    b.validate()
    return b


@raises(ValidationError)
def test_basic_invalid_bill():
    """ Test that we can create an invalid bill, and validation will fail """
    b = toy_bill()
    b.name = None
    b.validate()


def test_verify_actions():
    """ Make sure actions work """
    b = toy_bill()
    b.add_action("Some dude liked it.", "some dude", "2013-04-29")
    b.validate()
    # XXX: Check output


def test_verify_related_bill():
    """ Make sure related bills work """
    b = toy_bill()
    b.add_related_bill(name="HB 2020",
                       session="2011A",
                       chamber="upper",
                       relation="companion")  # continuation?
    b.validate()


def test_verify_documents():
    """ Make sure we can add documents """
    b = toy_bill()
    b.add_document_link(name="Fiscal Impact",
                        date="2013-04",
                        url='http://foo.bar.baz')

    b.add_document_link(name="Fiscal Impact",
                        date="2013-04",
                        url="http://hi.example.com/foo#bar",
                        mimetype="text/html")

    b.add_document_link(name="Fiscal Impact",
                        date="2013-04",
                        url='http://foobar.baz')

    b.validate()

    b.add_document_link(name="Fiscal Impact",
                        date="2013-04",
                        url=None,
                        mimetype='foo')

    @raises(ValidationError)
    def bval():
        b.validate()
    bval()


def test_verify_sponsors():
    """ Make sure sponsors work """
    b = toy_bill()
    b.add_sponsor(name="Joe Bleu",
                  sponsorship_type="Author",
                  entity_type="person",
                  primary=True,
                  chamber="upper")
    b.validate()


def test_subjects():
    """ Test we can add subjects """
    b = toy_bill()
    b.add_subject("Foo")
    b.add_subject("Bar")
    b.validate()


def test_versions():
    """ Test that versions work right """
    b = toy_bill()

    b.add_version_link(
        url="http://pault.ag/",
        name="Final Version",
        date="2013-04",
    )

    b.add_version_link(
        url="http://pault.ag/foo",
        name="Final Version",
        date="2013-04",
    )
    b.validate()

    assert len(b.versions) == 1
    assert len(b.versions[0]['links']) == 2

    try:
        b.add_version_link(
            url="http://pault.ag/foo",
            name="Final Version",
            date="2013-04",
        )
        assert True is False, "We didn't break."
    except ValueError:
        pass

    b.add_version_link(
        url="http://pault.ag/foo",
        name="Final Version",
        date="2013-04",
        on_duplicate='ignore'
    )

    assert len(b.versions) == 1
    assert len(b.versions[0]['links']) == 2

    try:
        b.add_version_link(
            url="http://pault.ag/foo",
            name="Finals Versions",
            date="2013-04",
        )
        assert True is False, "We didn't break."
    except ValueError:
        pass

    assert len(b.versions) == 1
    assert len(b.versions[0]['links']) == 2

    b.add_version_link(
        url="http://pault.ag/foovbar",
        name="Finals Versions",
        date="2013-04",
    )

    assert len(b.versions) == 2
    assert len(b.versions[1]['links']) == 1

    b.validate()
