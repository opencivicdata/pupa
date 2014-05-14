import pytest
from pupa.scrape import Post as ScrapePost
from pupa.importers import PostImporter, OrganizationImporter
from opencivicdata.models import Organization, Post


@pytest.mark.django_db
def test_full_post():
    org = Organization.objects.create(name="United States Executive Branch",
                                      classification="executive",
                                      jurisdiction_id="jurisdiction-id")
    post = ScrapePost('executive', 'President', '~{"classification": "executive"}')
    post.add_contact_detail('phone', '555-555-1234', 'this is fake')
    post.add_link('http://example.com/link')

    # import post
    oi = OrganizationImporter('jurisdiction-id')
    PostImporter('jurisdiction-id', oi).import_data([post.as_dict()])

    # get person from db and assert it imported correctly
    p = Post.objects.get()
    assert 'ocd-post' in p.id
    assert p.label == post.label
    assert p.role == post.role
    assert p.organization_id == org.id

    assert p.contact_details.all()[0].type == 'phone'
    assert p.contact_details.all()[0].value == '555-555-1234'
    assert p.contact_details.all()[0].note == 'this is fake'

    assert p.links.all()[0].url == 'http://example.com/link'


@pytest.mark.django_db
def test_deduplication():
    Organization.objects.create(id='us', name="United States Executive Branch",
                                classification="executive", jurisdiction_id="us")
    Organization.objects.create(id='nc', name="North Carolina Executive Branch",
                                classification="executive", jurisdiction_id="nc")
    pres = ScrapePost('executive', 'President', '~{"classification": "executive"}')
    vp = ScrapePost('vice-executive', 'Vice President', '~{"classification": "executive"}')
    gov = ScrapePost('executive', 'Governor', '~{"classification": "executive"}')

    # ensure pres, vp and gov are all imported
    #   pres & gov - same label, different jurisdiction
    #   vp & pres - same jurisdiction, different label
    us_oi = OrganizationImporter('us')
    nc_oi = OrganizationImporter('nc')
    PostImporter('us', us_oi).import_data([pres.as_dict(), vp.as_dict()])
    PostImporter('nc', nc_oi).import_data([gov.as_dict()])
    assert Post.objects.count() == 3

    # ensure changing the role is allowed
    pres = ScrapePost(label='executive', role='King',
                      organization_id='~{"classification": "executive"}')
    PostImporter('us', us_oi).import_data([pres.as_dict()])

    # no new object, just an update for role
    assert Post.objects.count() == 3
    assert Post.objects.get(organization_id='us', label='executive').role == 'King'


@pytest.mark.django_db
def test_resolve_special_json_id():
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
