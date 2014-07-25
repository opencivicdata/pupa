import pytest
from pupa.scrape import Person as ScrapePerson
from pupa.importers import PersonImporter
from opencivicdata.models import Person, Organization, Membership
from pupa.exceptions import SameNameError

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


@pytest.mark.django_db
def test_multiple_memberships():
    # there was a bug where two or more memberships to the same jurisdiction
    # would cause an ORM error, this test ensures that it is fixed
    p = Person.objects.create(name='Dwayne Johnson')
    o = Organization.objects.create(name='WWE', jurisdiction_id='jurisdiction-id')
    Membership.objects.create(person=p, organization=o)
    o = Organization.objects.create(name='WWF', jurisdiction_id='jurisdiction-id')
    Membership.objects.create(person=p, organization=o)

    person = ScrapePerson('Dwayne Johnson')
    pd = person.as_dict()
    PersonImporter('jurisdiction-id').import_data([pd])

    # deduplication should still work
    assert Person.objects.all().count() == 1


@pytest.mark.django_db
def test_same_name_people():
    # ensure two people with the same name don't import without birthdays
    o = Organization.objects.create(name='WWE', jurisdiction_id='jurisdiction-id')
    p1 = ScrapePerson('Dwayne Johnson', image='http://example.com/1')
    p2 = ScrapePerson('Dwayne Johnson', image='http://example.com/2')

    # the people have the same name but are apparently different
    with pytest.raises(SameNameError):
        PersonImporter('jurisdiction-id').import_data([p1.as_dict(), p2.as_dict()])

    # when we give them birth dates all is well though
    p1.birth_date = '1970'
    p2.birth_date = '1930'
    resp = PersonImporter('jurisdiction-id').import_data([p1.as_dict(), p2.as_dict()])
    assert resp['person'] == {'insert': 2, 'noop': 0, 'update': 0}
    assert Person.objects.count() == 2

    # fake some memberships so future lookups work on these people
    for p in Person.objects.all():
        Membership.objects.create(person=p, organization=o)

    # and now test that an update works and we can insert a new one with the same name
    p1.image = 'http://example.com/1.jpg'
    p2.birth_date = '1931'  # change birth_date, means a new insert
    resp = PersonImporter('jurisdiction-id').import_data([p1.as_dict(), p2.as_dict()])
    assert Person.objects.count() == 3
    assert resp['person'] == {'insert': 1, 'noop': 0, 'update': 1}

@pytest.mark.django_db
def test_same_name_people_other_name():
    # ensure we're taking other_names into account for the name collision code
    o = Organization.objects.create(name='WWE', jurisdiction_id='jurisdiction-id')
    p1 = ScrapePerson('Dwayne Johnson', image='http://example.com/1')
    p2 = ScrapePerson('Rock', image='http://example.com/2')
    p2.add_name('Dwayne Johnson')

    # the people have the same name but are apparently different
    with pytest.raises(SameNameError):
        PersonImporter('jurisdiction-id').import_data([p1.as_dict(), p2.as_dict()])


@pytest.mark.django_db
def test_same_name_second_import():
    # ensure two people with the same name don't import without birthdays
    o = Organization.objects.create(name='WWE', jurisdiction_id='jurisdiction-id')
    p1 = ScrapePerson('Dwayne Johnson', image='http://example.com/1')
    p2 = ScrapePerson('Dwayne Johnson', image='http://example.com/2')
    p1.birth_date = '1970'
    p2.birth_date = '1930'

    # when we give them birth dates all is well though
    resp = PersonImporter('jurisdiction-id').import_data([p1.as_dict(), p2.as_dict()])

    # fake some memberships so future lookups work on these people
    for p in Person.objects.all():
        Membership.objects.create(person=p, organization=o)

    p3 = ScrapePerson('Dwayne Johnson', image='http://example.com/3')

    with pytest.raises(SameNameError):
        resp = PersonImporter('jurisdiction-id').import_data([p3.as_dict()])
