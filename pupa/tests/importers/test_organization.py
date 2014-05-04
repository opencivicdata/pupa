import pytest
from pupa.scrape import Organization as ScrapeOrganization
from pupa.importers import OrganizationImporter
from opencivicdata.models import Organization


@pytest.mark.django_db
def test_full_organization():
    org = ScrapeOrganization('United Nations', classification='international')
    org.add_identifier('un')
    org.add_name('UN', start_date='1945')
    org.add_contact_detail('phone', '555-555-1234', 'this is fake')
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
    OrganizationImporter('jurisdiction-id').import_data([party])
    assert Organization.objects.count() == 1

    # parties shouldn't get jurisdiction id attached, so don't differ on import
    party = ScrapeOrganization('Wild', classification='party')
    OrganizationImporter('new-jurisdiction-id').import_data([party])
    assert Organization.objects.count() == 1
