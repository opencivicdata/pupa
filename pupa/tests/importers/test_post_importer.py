import pytest
from pupa.scrape import Post as ScrapePost
from pupa.importers import PostImporter, OrganizationImporter
from opencivicdata.core.models import Organization, Post, Division, Jurisdiction
import datetime


def create_jurisdictions():
    Division.objects.create(id='ocd-division/country:us', name='USA')
    Division.objects.create(id='ocd-division/country:us/state:nc', name='NC')
    Jurisdiction.objects.create(id='us', division_id='ocd-division/country:us')
    Jurisdiction.objects.create(id='nc', division_id='ocd-division/country:us/state:nc')


@pytest.mark.django_db
def test_full_post():
    create_jurisdictions()
    org = Organization.objects.create(name="United States Executive Branch",
                                      classification="executive",
                                      jurisdiction_id="us")
    post = ScrapePost(label='executive', role='President',
                      organization_id='~{"classification": "executive"}',
                      start_date=datetime.date(2015, 5, 18),
                      end_date='2015-05-19',
                      maximum_memberships=2
                      )
    post.add_contact_detail(type='phone', value='555-555-1234', note='this is fake')
    post.add_link('http://example.com/link')

    # import post
    oi = OrganizationImporter('us')
    PostImporter('jurisdiction-id', oi).import_data([post.as_dict()])
    print(post.as_dict())

    # get person from db and assert it imported correctly
    p = Post.objects.get()
    assert 'ocd-post' in p.id
    assert p.label == post.label
    assert p.role == post.role
    assert p.organization_id == org.id
    assert p.maximum_memberships == 2

    assert p.contact_details.all()[0].type == 'phone'
    assert p.contact_details.all()[0].value == '555-555-1234'
    assert p.contact_details.all()[0].note == 'this is fake'

    assert p.links.all()[0].url == 'http://example.com/link'

    assert p.start_date == '2015-05-18'
    assert p.end_date == '2015-05-19'


@pytest.mark.django_db
def test_deduplication():
    create_jurisdictions()
    Organization.objects.create(id='us', name="United States Executive Branch",
                                classification="executive", jurisdiction_id="us")
    Organization.objects.create(id='nc', name="North Carolina Executive Branch",
                                classification="executive", jurisdiction_id="nc")
    pres = ScrapePost(label='executive', role='President',
                      organization_id='~{"classification": "executive"}')
    vp = ScrapePost(label='vice-executive', role='Vice President',
                    organization_id='~{"classification": "executive"}')
    gov = ScrapePost(label='executive', role='Governor',
                     organization_id='~{"classification": "executive"}')

    # ensure pres, vp and gov are all imported
    #   pres & gov - same label, different jurisdiction
    #   vp & pres - same jurisdiction, different label
    us_oi = OrganizationImporter('us')
    nc_oi = OrganizationImporter('nc')
    PostImporter('us', us_oi).import_data([pres.as_dict(), vp.as_dict()])
    PostImporter('nc', nc_oi).import_data([gov.as_dict()])
    assert Post.objects.count() == 3


@pytest.mark.django_db
def test_resolve_special_json_id():
    create_jurisdictions()
    Organization.objects.create(id='us', name="United States Executive Branch",
                                classification="executive", jurisdiction_id="us")
    Organization.objects.create(id='nc', name="North Carolina Executive Branch",
                                classification="executive", jurisdiction_id="nc")
    Post.objects.create(id='pres', label='executive', role='President', organization_id='us')
    Post.objects.create(id='vpres', label='vice-executive', role='Vice President',
                        organization_id='us')
    Post.objects.create(id='gov', label='executive', role='Governor', organization_id='nc')

    oi = OrganizationImporter('')
    assert PostImporter('us', oi).resolve_json_id('~{"label": "executive"}') == 'pres'
    assert PostImporter('us', oi).resolve_json_id('~{"label": "vice-executive"}') == 'vpres'
    assert PostImporter('nc', oi).resolve_json_id('~{"label": "executive"}') == 'gov'
