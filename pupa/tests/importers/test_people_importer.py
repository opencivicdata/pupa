import pytest
from pupa.scrape import Person as ScrapePerson
from pupa.importers import PersonImporter
from opencivicdata.models import Person, Organization, Membership


@pytest.mark.django_db
def test_full_person():
    person = ScrapePerson('Tom Sawyer')
    person.add_identifier('1')
    person.add_name('Tommy', start_date='1880')
    person.add_contact_detail(type='phone', value='555-555-1234', note='this is fake')
    person.add_link('http://example.com/link')
    person.add_source('http://example.com/source')

    # import person
    pd = person.as_dict()
    PersonImporter('jurisdiction-id').import_data([pd])

    # get person from db and assert it imported correctly
    p = Person.objects.get()
    assert 'ocd-person' in p.id
    assert p.name == person.name

    assert p.identifiers.all()[0].identifier == '1'
    assert p.identifiers.all()[0].scheme == ''

    assert p.other_names.all()[0].name == 'Tommy'
    assert p.other_names.all()[0].start_date == '1880'

    assert p.contact_details.all()[0].type == 'phone'
    assert p.contact_details.all()[0].value == '555-555-1234'
    assert p.contact_details.all()[0].note == 'this is fake'

    assert p.links.all()[0].url == 'http://example.com/link'
    assert p.sources.all()[0].url == 'http://example.com/source'


def create_person():
    # deduplication for people is fairly complicated, it requires a person to have a membership
    # in the jurisdiction's organization and have a matching name.  let's set that up first for
    # the deduplication tests
    p = Person.objects.create(name='Dwayne Johnson')
    p.other_names.create(name='Rocky')
    o = Organization.objects.create(name='WWE', jurisdiction_id='jurisdiction-id')
    Membership.objects.create(person=p, organization=o)


@pytest.mark.django_db
def test_deduplication_same_name():
    create_person()
    # simplest case- just the same name
    person = ScrapePerson('Dwayne Johnson')
    pd = person.as_dict()
    PersonImporter('jurisdiction-id').import_data([pd])
    assert Person.objects.all().count() == 1


@pytest.mark.django_db
def test_deduplication_other_name_exists():
    create_person()
    # Rocky is already saved in other_names
    person = ScrapePerson('Rocky')
    pd = person.as_dict()
    PersonImporter('jurisdiction-id').import_data([pd])
    assert Person.objects.all().count() == 1


@pytest.mark.django_db
def test_deduplication_other_name_overlaps():
    create_person()
    # Person has other_name that overlaps w/ existing name
    person = ScrapePerson('The Rock')
    person.add_name('Dwayne Johnson')
    pd = person.as_dict()
    PersonImporter('jurisdiction-id').import_data([pd])
    assert Person.objects.all().count() == 1


@pytest.mark.django_db
def test_deduplication_no_name_overlap():
    create_person()
    # make sure we're not just being ridiculous and avoiding importing anything in the same org
    person = ScrapePerson('CM Punk')
    pd = person.as_dict()
    PersonImporter('jurisdiction-id').import_data([pd])
    assert Person.objects.all().count() == 2


@pytest.mark.django_db
def test_deduplication_no_jurisdiction_overlap():
    create_person()
    # make sure we get a new person if we're in a different org
    person = ScrapePerson('Dwayne Johnson')
    pd = person.as_dict()
    PersonImporter('new-jurisdiction-id').import_data([pd])
    assert Person.objects.all().count() == 2
