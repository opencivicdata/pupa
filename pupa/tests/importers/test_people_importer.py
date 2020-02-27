import pytest
from pupa.scrape import Person as ScrapePerson
from pupa.importers import PersonImporter
from opencivicdata.core.models import Person, Organization, Membership, Division, Jurisdiction
from pupa.exceptions import UnresolvedIdError, SameNameError


def create_jurisdiction():
    Division.objects.create(id='ocd-division/country:us', name='USA')
    Jurisdiction.objects.create(id='jid', division_id='ocd-division/country:us')


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
    PersonImporter('jid').import_data([pd])

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
    o = Organization.objects.create(name='WWE', jurisdiction_id='jid')
    Membership.objects.create(person=p, organization=o)


@pytest.mark.django_db
def test_deduplication_same_name():
    create_jurisdiction()
    create_person()
    # simplest case- just the same name
    person = ScrapePerson('Dwayne Johnson')
    pd = person.as_dict()
    PersonImporter('jid').import_data([pd])
    assert Person.objects.all().count() == 1


@pytest.mark.django_db
def test_deduplication_other_name_exists():
    create_jurisdiction()
    create_person()
    # Rocky is already saved in other_names
    person = ScrapePerson('Rocky')
    pd = person.as_dict()
    PersonImporter('jid').import_data([pd])
    assert Person.objects.all().count() == 1


@pytest.mark.django_db
def test_deduplication_other_name_overlaps():
    create_jurisdiction()
    create_person()
    # Person has other_name that overlaps w/ existing name
    person = ScrapePerson('The Rock')
    person.add_name('Dwayne Johnson')
    pd = person.as_dict()
    PersonImporter('jid').import_data([pd])
    assert Person.objects.all().count() == 1


@pytest.mark.django_db
def test_deduplication_no_name_overlap():
    create_jurisdiction()
    create_person()
    # make sure we're not just being ridiculous and avoiding importing anything in the same org
    person = ScrapePerson('CM Punk')
    pd = person.as_dict()
    PersonImporter('jid').import_data([pd])
    assert Person.objects.all().count() == 2


@pytest.mark.django_db
def test_deduplication_no_jurisdiction_overlap():
    create_jurisdiction()
    create_person()
    # make sure we get a new person if we're in a different org
    person = ScrapePerson('Dwayne Johnson')
    pd = person.as_dict()
    PersonImporter('new-jurisdiction-id').import_data([pd])
    assert Person.objects.all().count() == 2


@pytest.mark.django_db
def test_multiple_memberships():
    create_jurisdiction()
    # there was a bug where two or more memberships to the same jurisdiction
    # would cause an ORM error, this test ensures that it is fixed
    p = Person.objects.create(name='Dwayne Johnson')
    o = Organization.objects.create(name='WWE', jurisdiction_id='jid')
    Membership.objects.create(person=p, organization=o)
    o = Organization.objects.create(name='WWF', jurisdiction_id='jid')
    Membership.objects.create(person=p, organization=o)

    person = ScrapePerson('Dwayne Johnson')
    pd = person.as_dict()
    PersonImporter('jid').import_data([pd])

    # deduplication should still work
    assert Person.objects.all().count() == 1


@pytest.mark.django_db
def test_same_name_people():
    create_jurisdiction()
    o = Organization.objects.create(name='WWE', jurisdiction_id='jid')

    # importing two people with the same name to a pristine database should error
    p1 = ScrapePerson('Dwayne Johnson', image='http://example.com/1')
    p2 = ScrapePerson('Dwayne Johnson', image='http://example.com/2')
    with pytest.raises(SameNameError):
        PersonImporter('jid').import_data([p1.as_dict(), p2.as_dict()])

    # importing one person should pass
    PersonImporter('jid').import_data([p1.as_dict()])
    # create fake memberships so that future lookups work on the imported people
    for p in Person.objects.all():
        Membership.objects.create(person=p, organization=o)

    # importing another person with the same name should fail
    with pytest.raises(SameNameError):
        PersonImporter('jid').import_data([p1.as_dict(), p2.as_dict()])

    # adding birth dates should pass
    p1.birth_date = '1970'
    p2.birth_date = '1930'
    resp = PersonImporter('jid').import_data([p1.as_dict(), p2.as_dict()])
    assert resp['person']['insert'] == 1
    assert resp['person']['noop'] == 0
    assert resp['person']['update'] == 1
    assert Person.objects.count() == 2
    # create fake memberships so that future lookups work on the imported people
    for p in Person.objects.all():
        Membership.objects.create(person=p, organization=o)

    # adding a third person with the same name but without a birthday should error
    p3 = ScrapePerson('Dwayne Johnson', image='http://example.com/3')

    with pytest.raises(SameNameError):
        PersonImporter('jid').import_data([p3.as_dict()])

    # and now test that an update works and we can insert a new one with the same name
    p1.image = 'http://example.com/1.jpg'
    p2.birth_date = '1931'  # change birth_date, means a new insert
    resp = PersonImporter('jid').import_data([p1.as_dict(), p2.as_dict()])
    assert Person.objects.count() == 3
    assert resp['person']['insert'] == 1
    assert resp['person']['noop'] == 0
    assert resp['person']['update'] == 1


@pytest.mark.django_db
def test_same_name_people_other_name():
    create_jurisdiction()
    # ensure we're taking other_names into account for the name collision code
    Organization.objects.create(name='WWE', jurisdiction_id='jid')
    p1 = ScrapePerson('Dwayne Johnson', image='http://example.com/1')
    p2 = ScrapePerson('Rock', image='http://example.com/2')
    p2.add_name('Dwayne Johnson')

    # the people have the same name but are apparently different
    with pytest.raises(SameNameError):
        PersonImporter('jid').import_data([p1.as_dict(), p2.as_dict()])


@pytest.mark.django_db
def test_same_name_second_import():
    create_jurisdiction()
    # ensure two people with the same name don't import without birthdays
    o = Organization.objects.create(name='WWE', jurisdiction_id='jid')
    p1 = ScrapePerson('Dwayne Johnson', image='http://example.com/1')
    p2 = ScrapePerson('Dwayne Johnson', image='http://example.com/2')
    p1.birth_date = '1970'
    p2.birth_date = '1930'

    # when we give them birth dates all is well though
    PersonImporter('jid').import_data([p1.as_dict(), p2.as_dict()])

    # fake some memberships so future lookups work on these people
    for p in Person.objects.all():
        Membership.objects.create(person=p, organization=o)

    p3 = ScrapePerson('Dwayne Johnson', image='http://example.com/3')

    with pytest.raises(SameNameError):
        PersonImporter('jid').import_data([p3.as_dict()])


@pytest.mark.django_db
def test_resolve_json_id():
    create_jurisdiction()
    o = Organization.objects.create(name='WWE', jurisdiction_id='jid')
    p = Person.objects.create(name='Dwayne Johnson', family_name='Johnson')
    p.other_names.create(name='Rock')
    p.memberships.create(organization=o)

    pi = PersonImporter('jid')
    assert pi.resolve_json_id('~{"name": "Dwayne Johnson"}') == p.id
    assert pi.resolve_json_id('~{"name": "Rock"}') == p.id
    assert pi.resolve_json_id('~{"name": "Johnson"}') == p.id


@pytest.mark.django_db
def test_resolve_json_id_multiple_family_name():
    create_jurisdiction()
    o = Organization.objects.create(name='WWE', jurisdiction_id='jid')
    p1 = Person.objects.create(name='Dwayne Johnson', family_name='Johnson')
    p1.other_names.create(name='Rock')
    p2 = Person.objects.create(name='Adam Johnson', family_name='Johnson')
    for p in Person.objects.all():
        Membership.objects.create(person=p, organization=o)

    # If there are multiple people with a family name, full name/other name
    # lookups should work but family name lookups should fail.
    pi = PersonImporter('jid')
    assert pi.resolve_json_id('~{"name": "Dwayne Johnson"}') == p1.id
    assert pi.resolve_json_id('~{"name": "Adam Johnson"}') == p2.id
    with pytest.raises(UnresolvedIdError):
        pi.resolve_json_id('~{"name": "Johnson"}')
