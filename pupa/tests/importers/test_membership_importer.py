import pytest
from pupa.scrape import Membership as ScrapeMembership
from pupa.scrape import Person as ScrapePerson
from pupa.importers import MembershipImporter, PersonImporter, OrganizationImporter
from pupa.exceptions import NoMembershipsError
from opencivicdata.core.models import Organization, Post, Person, Division, Jurisdiction


class DumbMockImporter(object):
    """ this is a mock importer that implements a resolve_json_id that is just a pass-through """
    json_to_db_id = {}

    def resolve_json_id(self, json_id, allow_no_match=False):
        return json_id


def create_jurisdiction():
    Division.objects.create(id='ocd-division/country:us', name='USA')
    Jurisdiction.objects.create(id='fnd-jid', division_id='ocd-division/country:us')


@pytest.mark.django_db
def test_full_membership():
    create_jurisdiction()
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


@pytest.mark.django_db
def test_no_membership_for_person():
    create_jurisdiction()
    Organization.objects.create(id="fnd", name="Foundation", classification="foundation",
                                jurisdiction_id="fnd-jid")

    # import a person with no memberships
    p = ScrapePerson('a man without a country')
    person_imp = PersonImporter('fnd-jid')
    person_imp.import_data([p.as_dict()])

    # try to import a membership
    dumb_imp = DumbMockImporter()
    memimp = MembershipImporter('fnd-jid', person_imp, dumb_imp, dumb_imp)

    with pytest.raises(NoMembershipsError):
        memimp.import_data([])


@pytest.mark.django_db
def test_no_membership_for_person_including_party():
    """
    even though party is specified we should still get a no memberships error because it doesn't
    bind the person to a jurisdiction, thus causing duplication
    """
    create_jurisdiction()
    Organization.objects.create(id="fnd", name="Foundation", classification="foundation",
                                jurisdiction_id="fnd-jid")
    Organization.objects.create(id="dem", name="Democratic", classification="party")

    # import a person with no memberships
    p = ScrapePerson('a man without a country', party='Democratic')
    person_imp = PersonImporter('fnd-jid')
    org_imp = OrganizationImporter('fnd-jid')
    person_imp.import_data([p.as_dict()])

    # try to import a membership
    dumb_imp = DumbMockImporter()
    memimp = MembershipImporter('fnd-jid', person_imp, org_imp, dumb_imp)

    with pytest.raises(NoMembershipsError):
        memimp.import_data([p._related[0].as_dict()])


@pytest.mark.django_db
def test_multiple_orgs_of_same_class():
    """
    We should be able to set memberships on organizations with the
    same classification within the same jurisdictions
    """
    create_jurisdiction()
    Organization.objects.create(id="fnd", name="Foundation", classification="foundation",
                                jurisdiction_id="fnd-jid")
    Organization.objects.create(id="fdr", name="Federation", classification="foundation",
                                jurisdiction_id="fnd-jid")

    hari = ScrapePerson('Hari Seldon',
                        primary_org='foundation',
                        role='founder',
                        primary_org_name='Foundation')

    picard = ScrapePerson('Jean Luc Picard',
                          primary_org='foundation',
                          role='founder',
                          primary_org_name='Federation')

    person_imp = PersonImporter('fnd-jid')
    person_imp.import_data([hari.as_dict()])
    person_imp.import_data([picard.as_dict()])

    # try to import a membership
    org_imp = OrganizationImporter('fnd-jid')
    dumb_imp = DumbMockImporter()
    memimp = MembershipImporter('fnd-jid', person_imp, org_imp, dumb_imp)

    memimp.import_data([hari._related[0].as_dict(), picard._related[0].as_dict()])

    assert Person.objects.get(name='Hari Seldon'
                              ).memberships.get().organization.name == 'Foundation'
    assert Person.objects.get(name='Jean Luc Picard'
                              ).memberships.get().organization.name == 'Federation'


@pytest.mark.django_db
def test_multiple_posts_class():
    create_jurisdiction()

    org = Organization.objects.create(id="fnd", name="Foundation", classification="foundation",
                                      jurisdiction_id="fnd-jid")
    hari = Person.objects.create(id="hs", name="Hari Seldon")
    founder = Post.objects.create(id='f', label="founder", role="Founder", organization=org)
    chair = Post.objects.create(id='c', label="chair", role="Chair", organization=org)

    m1 = ScrapeMembership(person_id=hari.id, organization_id=org.id, post_id=founder.id)
    m2 = ScrapeMembership(person_id=hari.id, organization_id=org.id, post_id=chair.id)

    dumb_imp = DumbMockImporter()
    memimp = MembershipImporter('fnd-jid', dumb_imp, dumb_imp, dumb_imp)
    memimp.import_data([m1.as_dict(), m2.as_dict()])

    # ensure that the memberships attached in the right places
    assert org.memberships.count() == 2
    assert hari.memberships.count() == 2
    assert founder.memberships.count() == 1
    assert chair.memberships.count() == 1


@pytest.mark.django_db
def test_unmatched_person():
    create_jurisdiction()

    org = Organization.objects.create(id="fnd", name="Foundation", classification="foundation",
                                      jurisdiction_id="fnd-jid")
    # not a real person, won't have a person_id after import
    m1 = ScrapeMembership(person_name='Harry Seldom', organization_id=org.id,
                          person_id=None
                          )

    dumb_imp = DumbMockImporter()
    memimp = MembershipImporter('fnd-jid', dumb_imp, dumb_imp, dumb_imp)
    memimp.import_data([m1.as_dict()])

    # ensure that the memberships attached in the right places
    assert org.memberships.count() == 1

    membership = org.memberships.get()
    assert membership.person_id is None
    assert membership.person_name == 'Harry Seldom'
