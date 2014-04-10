import pytest
from pupa.models import Person
from validictory import ValidationError


def test_basic_invalid_person():
    """ Test that we can create an invalid person, and validation will fail """
    bob = Person("Bob B. Johnson")
    bob.add_source(url='foo')
    bob.validate()

    bob.name = None

    with pytest.raises(ValidationError):
        bob.validate()


def test_str():
    """ test __str__ method """
    assert str(Person("Bob B. Johnson")) == "Bob B. Johnson"


def test_magic_methods():
    """ Test the magic methods work """
    bob = Person("John Q. Public, Esq.",
                 gender="male", image="http://example.com/john.jpg",
                 summary="Some person")
    bob.add_source(url='foo')
    bob.validate()

    bob.add_link("http://twitter.com/ev", "Twitter Account")

    assert bob.links == [
        {"note": "Twitter Account",
         "url": "http://twitter.com/ev"}
    ]

    bob.add_name("Thiston", note="What my friends call me")

    assert bob.other_names == [
        {"name": "Thiston",
         "note": "What my friends call me"}
    ]

    bob.add_name("Johnseph Q. Publico",
                 note="Birth name",
                 start_date="1920-01",
                 end_date="1949-12-31")

    assert bob.other_names == [
        {"name": "Thiston",
         "note": "What my friends call me"},
        {"name": "Johnseph Q. Publico",
         "note": "Birth name",
         "start_date": "1920-01",
         "end_date": "1949-12-31"}
    ]


def test_add_contact_information():
    """ Test that we can add contact information """
    bob = Person("John Q. Public, Esq.",
                 gender="male", image="http://example.com/john.jpg",
                 summary="Some person")
    bob.add_source(url='foo')
    bob.validate()

    bob.add_contact_detail(type='voice',
                           value='876-5309',
                           note='Jenny Cell')

    bob.validate()
