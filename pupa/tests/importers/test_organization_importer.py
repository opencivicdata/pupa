import pytest
from opencivicdata.models import Organization
from pupa.scrape import Organization as ScrapeOrganization
from pupa.importers import OrganizationImporter
from pupa.exceptions import UnresolvedIdError


@pytest.mark.django_db
def test_full_organization():
    org = ScrapeOrganization('United Nations', classification='international')
    org.add_identifier('un')
    org.add_name('UN', start_date='1945')
    org.add_contact_detail(type='phone', value='555-555-1234', note='this is fake')
    org.add_link('http://example.com/link')
    org.add_source('http://example.com/source')

    # import org
    od = org.as_dict()
    OrganizationImporter('jurisdiction-id').import_data([od])

    # get person from db and assert it imported correctly
    o = Organization.objects.get()
    assert 'ocd-organization' in o.id
    assert o.name == org.name

    assert o.identifiers.all()[0].identifier == 'un'
    assert o.identifiers.all()[0].scheme == ''

    assert o.other_names.all()[0].name == 'UN'
    assert o.other_names.all()[0].start_date == '1945'

    assert o.contact_details.all()[0].type == 'phone'
    assert o.contact_details.all()[0].value == '555-555-1234'
    assert o.contact_details.all()[0].note == 'this is fake'

    assert o.links.all()[0].url == 'http://example.com/link'
    assert o.sources.all()[0].url == 'http://example.com/source'


@pytest.mark.django_db
def test_deduplication_similar_but_different():
    o1 = ScrapeOrganization('United Nations', classification='international')
    # different classification
    o2 = ScrapeOrganization('United Nations', classification='global')
    # different name
    o3 = ScrapeOrganization('United Nations of Earth', classification='international')
    # has a parent
    o4 = ScrapeOrganization('United Nations', classification='international', parent_id=o1._id)

    # similar, but no duplicates
    orgs = [o1.as_dict(), o2.as_dict(), o3.as_dict(), o4.as_dict()]
    OrganizationImporter('jurisdiction-id').import_data(orgs)
    assert Organization.objects.count() == 4

    # should get a new one  when jurisdiction_id changes
    o5 = ScrapeOrganization('United Nations', classification='international')
    OrganizationImporter('new-jurisdiction-id').import_data([o5.as_dict()])
    assert Organization.objects.count() == 5


@pytest.mark.django_db
def test_deduplication_parties():
    party = ScrapeOrganization('Wild', classification='party')
    OrganizationImporter('jurisdiction-id').import_data([party.as_dict()])
    assert Organization.objects.count() == 1

    # parties shouldn't get jurisdiction id attached, so don't differ on import
    party = ScrapeOrganization('Wild', classification='party')
    OrganizationImporter('new-jurisdiction-id').import_data([party.as_dict()])
    assert Organization.objects.count() == 1


@pytest.mark.django_db
def test_deduplication_prevents_identical():
    org1 = ScrapeOrganization('United Nations', classification='international')
    org2 = ScrapeOrganization('United Nations', classification='international',
                              founding_date='1945')
    OrganizationImporter('jurisdiction-id').import_data([org1.as_dict()])
    assert Organization.objects.count() == 1

    OrganizationImporter('jurisdiction-id').import_data([org2.as_dict()])
    assert Organization.objects.count() == 1


@pytest.mark.django_db
def test_pseudo_ids():
    wild = Organization.objects.create(id='1', name='Wild', classification='party')
    senate = Organization.objects.create(id='2', name='Senate', classification='upper',
                                         jurisdiction_id='jid1')
    house = Organization.objects.create(id='3', name='House', classification='lower',
                                        jurisdiction_id='jid1')
    un = Organization.objects.create(id='4', name='United Nations', classification='international',
                                     jurisdiction_id='jid2')

    oi1 = OrganizationImporter('jid1')
    assert oi1.resolve_json_id('~{"classification":"upper"}') == senate.id
    assert oi1.resolve_json_id('~{"classification":"lower"}') == house.id
    assert oi1.resolve_json_id('~{"classification":"party", "name":"Wild"}') == wild.id

    with pytest.raises(UnresolvedIdError):
        oi1.resolve_json_id('~{"classification":"international", "name":"United Nations"}')

    oi2 = OrganizationImporter('jid2')
    assert (oi2.resolve_json_id('~{"classification":"international", "name":"United Nations"}') ==
            un.id)


@pytest.mark.django_db
def test_parent_id_resolution():
    parent = ScrapeOrganization('UN', classification='international')
    child = ScrapeOrganization('UNESCO', classification='unknown', parent_id=parent._id)
    OrganizationImporter('jurisdiction-id').import_data([parent.as_dict(), child.as_dict()])
    assert Organization.objects.count() == 2
    assert Organization.objects.get(name='UN').children.count() == 1
    assert Organization.objects.get(name='UNESCO').parent.name == 'UN'


@pytest.mark.django_db
def test_pseudo_parent_id_resolution():
    parent = ScrapeOrganization('UN', classification='international')
    child = ScrapeOrganization('UNESCO', classification='unknown',
                               parent_id='~{"classification": "international"}')
    OrganizationImporter('jurisdiction-id').import_data([parent.as_dict(), child.as_dict()])
    assert Organization.objects.count() == 2
    assert Organization.objects.get(name='UN').children.count() == 1
    assert Organization.objects.get(name='UNESCO').parent.name == 'UN'


@pytest.mark.django_db
def test_extras_organization():
    org = ScrapeOrganization('United Nations', classification='international')
    org.extras = {"hello": "world",
                  "foo": {"bar": "baz"}}
    od = org.as_dict()
    OrganizationImporter('jurisdiction-id').import_data([od])
    o = Organization.objects.get()
    assert o.extras['foo']['bar'] == 'baz'
