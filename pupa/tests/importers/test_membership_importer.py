import pytest
from pupa.scrape import Membership as ScrapeMembership
from pupa.scrape import Person as ScrapePerson
from pupa.scrape import Organization as ScrapeOrganization
from pupa.importers import MembershipImporter, PersonImporter, OrganizationImporter
from pupa.exceptions import NoMembershipsError
from opencivicdata.models import Organization, Post, Person


class DumbMockImporter(object):
    """ this is a mock importer that implements a resolve_json_id that is just a pass-through """
    json_to_db_id = {}

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

    o = ScrapeOrganization(org.name)

    org_imp = OrganizationImporter('fnd')
    org_imp.import_data([o.as_dict()])

    dumb_imp = DumbMockImporter()
    memimp = MembershipImporter('fnd-jid', dumb_imp, org_imp, dumb_imp)
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
    Organization.objects.create(id="fnd", name="Foundation", classification="foundation",
                                jurisdiction_id="fnd-jid")

    # import a person with no memberships
    p = ScrapePerson('a man without a country')
    person_imp = PersonImporter('fnd-jid')
    person_imp.import_data([p.as_dict()])

    # try to import a membership
    dumb_imp = DumbMockImporter()
    org_imp = OrganizationImporter('fnd')
    memimp = MembershipImporter('fnd-jid', person_imp, org_imp, dumb_imp)

    with pytest.raises(NoMembershipsError):
        memimp.import_data([])


@pytest.mark.django_db
def test_no_membership_for_person_including_party():
    """
    even though party is specified we should still get a no memberships error because it doesn't
    bind the person to a jurisdiction, thus causing duplication
    """
    Organization.objects.create(id="fnd", name="Foundation", classification="foundation",
                                jurisdiction_id="fnd-jid")
    Organization.objects.create(id="dem", name="Democratic", classification="party")

    # import a person with no memberships
    p = ScrapePerson('a man without a country', party='Democratic')
    person_imp = PersonImporter('fnd-jid')
    person_imp.import_data([p.as_dict()])

    # try to import a membership
    dumb_imp = DumbMockImporter()
    org_imp = OrganizationImporter('fnd')
    memimp = MembershipImporter('fnd-jid', person_imp, org_imp, dumb_imp)

    with pytest.raises(NoMembershipsError):
        memimp.import_data([p._related[0].as_dict()])


@pytest.mark.django_db
def test_multiple_orgs_of_same_class():
    """
    We should be able to set memberships on organizations with the
    same classification within the same jurisdictions
    """
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
    dumb_imp = DumbMockImporter()
    org_imp = OrganizationImporter('fnd')
    memimp = MembershipImporter('fnd-jid', person_imp, org_imp, dumb_imp)

    memimp.import_data([hari._related[0].as_dict(), picard._related[0].as_dict()])

    assert Person.objects.get(name='Hari Seldon').memberships.get().organization.name == 'Foundation'
    assert Person.objects.get(name='Jean Luc Picard').memberships.get().organization.name == 'Federation'
