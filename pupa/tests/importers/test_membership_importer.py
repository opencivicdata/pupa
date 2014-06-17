import pytest
from pupa.scrape import Membership as ScrapeMembership
from pupa.importers import MembershipImporter
from opencivicdata.models import Organization, Post, Person


class DumbMockImporter(object):
    """ this is a mock importer that implements a resolve_json_id that is just a pass-through """

    def resolve_json_id(self, json_id):
        return json_id


@pytest.mark.django_db
def test_full_membership():
    org = Organization.objects.create(id="fnd", name="Foundation", classification="foundation",
                                      jurisdiction_id="fnd-jid")
    hari = Person.objects.create(id="hs", name="Hari Seldon")
    robot = Person.objects.create(id="robot", name="R. Daneel Olivaw")
    post = Post.objects.create(id='f', label="founder", role="Founder", organization=org)

    # add a membership through a post
    m1 = ScrapeMembership(person_id=hari.id, organization_id=org.id, post_id=post.id)
    m1.add_contact_detail(type='phone', value='555-555-1234', note='this is fake')
    m1.add_link('http://example.com/link')

    # add a membership direct to an organization
    m2 = ScrapeMembership(person_id=robot.id, organization_id=org.id, label='member',
                          role='member')

    dumb_imp = DumbMockImporter()
    memimp = MembershipImporter('fnd-jid', dumb_imp, dumb_imp, dumb_imp)
    memimp.import_data([m1.as_dict(), m2.as_dict()])

    # ensure that the memberships attached in the right places
    assert org.memberships.count() == 2
    assert hari.memberships.count() == 1
    assert robot.memberships.count() == 1
    assert post.memberships.count() == 1

    # ensure that the first membership has contact details and links
    m = hari.memberships.get()
    cd = m.contact_details.get()
    assert cd.type == 'phone'
    assert cd.value == '555-555-1234'
    assert cd.note == 'this is fake'
    assert m.links.all()[0].url == 'http://example.com/link'
