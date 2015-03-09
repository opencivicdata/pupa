import pytest
from pupa.scrape import Bill as ScrapeBill
from pupa.scrape import Organization as ScrapeOrganization
from pupa.importers import BillImporter, OrganizationImporter
from opencivicdata.models import Bill, Jurisdiction, Person, Organization


def create_jurisdiction():
    j = Jurisdiction.objects.create(id='jid', division_id='did')
    j.legislative_sessions.create(identifier='1899', name='1899')
    j.legislative_sessions.create(identifier='1900', name='1900')


def create_org():
    return Organization.objects.create(id='org-id', name='House', classification='lower',
                                       jurisdiction_id='jid')


@pytest.mark.django_db
def test_full_bill():
    create_jurisdiction()
    person = Person.objects.create(id='person-id', name='Adam Smith')
    person2 = Person.objects.create(id='person-id-2', name='Kdawg Smith')
    PersonIdentifier.objects.create(person=person2, scheme='thomas_id', identifier='01791')
    org = ScrapeOrganization(name='House', classification='lower')
    com = ScrapeOrganization(name='Arbitrary Committee', classification='committee',
                             parent_id=org._id)

    oldbill = ScrapeBill('HB 99', '1899', 'Axe & Tack Tax Act',
                         classification='tax bill', from_organization=org._id)

    bill = ScrapeBill('HB 1', '1900', 'Axe & Tack Tax Act',
                      classification='tax bill', from_organization=org._id)
    bill.subject = ['taxes', 'axes']
    bill.add_identifier('SB 9')
    bill.add_title('Tack & Axe Tax Act')
    bill.add_action('introduced in house', '1900-04-01', chamber='lower')
    act = bill.add_action('sent to arbitrary committee', '1900-04-04', chamber='lower')
    act.add_related_entity('arbitrary committee', 'organization', com._id)
    bill.add_related_bill("HB 99", legislative_session="1899", relation_type="prior-session")
    bill.add_sponsorship('Adam Smith', classification='extra sponsor', entity_type='person',
                         primary=False, entity_id=person.id)
    bill.add_sponsorship('Jane Smith', classification='lead sponsor', entity_type='person',
                         primary=True)
    bill.add_sponsorship_by_identifier('Kdawg Smith', classification='writer', entity_type='person',
                                       primary=False, scheme='thomas_id', identifier='01791')
    bill.add_abstract('This is an act about axes and taxes and tacks.', note="official")
    bill.add_document_link('Fiscal Note', 'http://example.com/fn.pdf',
                           media_type='application/pdf')
    bill.add_document_link('Fiscal Note', 'http://example.com/fn.html', media_type='text/html')
    bill.add_version_link('Fiscal Note', 'http://example.com/v/1', media_type='text/html')
    bill.add_source('http://example.com/source')

    # import bill
    oi = OrganizationImporter('jid')
    oi.import_data([org.as_dict(), com.as_dict()])
    BillImporter('jid', oi).import_data([oldbill.as_dict(), bill.as_dict()])

    # get bill from db and assert it imported correctly
    b = Bill.objects.get(identifier='HB 1')
    assert b.from_organization.classification == 'lower'
    assert b.identifier == bill.identifier
    assert b.title == bill.title
    assert b.classification == bill.classification
    assert b.subject == ['taxes', 'axes']
    assert b.abstracts.get().note == 'official'

    # other_title, other_identifier added
    assert b.other_titles.get().title == 'Tack & Axe Tax Act'
    assert b.other_identifiers.get().identifier == 'SB 9'

    # actions
    actions = list(b.actions.all())
    assert len(actions) == 2
    # ensure order was preserved (if this breaks it'll be intermittent)
    assert actions[0].organization == Organization.objects.get(classification='lower')
    assert actions[0].description == "introduced in house"
    assert actions[1].description == "sent to arbitrary committee"
    assert (actions[1].related_entities.get().organization ==
            Organization.objects.get(classification='committee'))

    # related_bills were added
    rb = b.related_bills.get()
    assert rb.identifier == 'HB 99'

    # and bill got resolved
    assert rb.related_bill.identifier == 'HB 99'

    # sponsors added, linked & unlinked
    sponsorships = b.sponsorships.all()
    assert len(sponsorships) == 3
    for ss in sponsorships:
        if ss.primary:
            assert ss.person is None
            assert ss.organization is None
        elif ss.classification == 'extra sponsor':
            assert ss.person == person
        else:
            assert ss.person == person2

    # versions & documents with their links
    versions = b.versions.all()
    assert len(versions) == 1
    assert versions[0].links.count() == 1
    documents = b.documents.all()
    assert len(documents) == 1
    assert documents[0].links.count() == 2

    # sources
    assert b.sources.count() == 1


@pytest.mark.django_db
def test_bill_chamber_param():
    create_jurisdiction()
    org = create_org()

    bill = ScrapeBill('HB 1', '1900', 'Axe & Tack Tax Act',
                      classification='tax bill', chamber='lower')

    oi = OrganizationImporter('jid')
    BillImporter('jid', oi).import_data([bill.as_dict()])

    assert Bill.objects.get().from_organization_id == org.id


@pytest.mark.django_db
def test_bill_update():
    create_jurisdiction()
    create_org()

    bill = ScrapeBill('HB 1', '1900', 'First Bill', chamber='lower')

    oi = OrganizationImporter('jid')
    _, what = BillImporter('jid', oi).import_item(bill.as_dict())
    assert what == 'insert'
    _, what = BillImporter('jid', oi).import_item(bill.as_dict())
    assert what == 'noop'

    # ensure no new object was created
    assert Bill.objects.count() == 1

    # test basic update
    bill = ScrapeBill('HB 1', '1900', '1st Bill', chamber='lower')
    _, what = BillImporter('jid', oi).import_item(bill.as_dict())
    assert what == 'update'
    assert Bill.objects.get().title == '1st Bill'


@pytest.mark.django_db
def test_bill_update_because_of_subitem():
    create_jurisdiction()
    create_org()
    oi = OrganizationImporter('jid')

    # initial bill
    bill = ScrapeBill('HB 1', '1900', 'First Bill', chamber='lower')
    bill.add_action('this is an action', chamber='lower', date='1900-01-01')
    result = BillImporter('jid', oi).import_data([bill.as_dict()])
    assert result['bill']['insert'] == 1
    obj = Bill.objects.get()
    assert obj.actions.count() == 1

    # now let's make sure we get updated when there are second actions
    bill = ScrapeBill('HB 1', '1900', 'First Bill', chamber='lower')
    bill.add_action('this is an action', chamber='lower', date='1900-01-01')
    bill.add_action('this is a second action', chamber='lower', date='1900-01-02')
    result = BillImporter('jid', oi).import_data([bill.as_dict()])
    assert result['bill']['update'] == 1
    obj = Bill.objects.get()
    assert obj.actions.count() == 2

    # same 2 actions, noop
    bill = ScrapeBill('HB 1', '1900', 'First Bill', chamber='lower')
    bill.add_action('this is an action', chamber='lower', date='1900-01-01')
    bill.add_action('this is a second action', chamber='lower', date='1900-01-02')
    result = BillImporter('jid', oi).import_data([bill.as_dict()])
    assert result['bill']['noop'] == 1
    obj = Bill.objects.get()
    assert obj.actions.count() == 2

    # different 2 actions, update
    bill = ScrapeBill('HB 1', '1900', 'First Bill', chamber='lower')
    bill.add_action('this is an action', chamber='lower', date='1900-01-01')
    bill.add_action('this is a different second action', chamber='lower', date='1900-01-02')
    result = BillImporter('jid', oi).import_data([bill.as_dict()])
    assert result['bill']['update'] == 1
    obj = Bill.objects.get()
    assert obj.actions.count() == 2

    # delete an action, update
    bill = ScrapeBill('HB 1', '1900', 'First Bill', chamber='lower')
    bill.add_action('this is a second action', chamber='lower', date='1900-01-02')
    result = BillImporter('jid', oi).import_data([bill.as_dict()])
    assert result['bill']['update'] == 1
    obj = Bill.objects.get()
    assert obj.actions.count() == 1

    # delete all actions, update
    bill = ScrapeBill('HB 1', '1900', 'First Bill', chamber='lower')
    result = BillImporter('jid', oi).import_data([bill.as_dict()])
    assert result['bill']['update'] == 1
    obj = Bill.objects.get()
    assert obj.actions.count() == 0

    # and back to initial status, update
    bill = ScrapeBill('HB 1', '1900', 'First Bill', chamber='lower')
    bill.add_action('this is an action', chamber='lower', date='1900-01-01')
    result = BillImporter('jid', oi).import_data([bill.as_dict()])
    assert result['bill']['update'] == 1
    obj = Bill.objects.get()
    assert obj.actions.count() == 1


@pytest.mark.django_db
def test_bill_update_subsubitem():
    create_jurisdiction()
    create_org()
    oi = OrganizationImporter('jid')

    # initial sub-subitem
    bill = ScrapeBill('HB 1', '1900', 'First Bill', chamber='lower')
    bill.add_version_link('printing', 'http://example.com/test.pdf', media_type='application/pdf')
    result = BillImporter('jid', oi).import_data([bill.as_dict()])
    assert result['bill']['insert'] == 1
    obj = Bill.objects.get()
    assert obj.versions.count() == 1
    assert obj.versions.get().links.count() == 1

    # a second subsubitem, update
    bill = ScrapeBill('HB 1', '1900', 'First Bill', chamber='lower')
    bill.add_version_link('printing', 'http://example.com/test.pdf', media_type='application/pdf')
    bill.add_version_link('printing', 'http://example.com/test.text', media_type='text/plain')
    result = BillImporter('jid', oi).import_data([bill.as_dict()])
    assert result['bill']['update'] == 1
    obj = Bill.objects.get()
    assert obj.versions.count() == 1
    assert obj.versions.get().links.count() == 2

    # same thing, noop
    bill = ScrapeBill('HB 1', '1900', 'First Bill', chamber='lower')
    bill.add_version_link('printing', 'http://example.com/test.pdf', media_type='application/pdf')
    bill.add_version_link('printing', 'http://example.com/test.text', media_type='text/plain')
    result = BillImporter('jid', oi).import_data([bill.as_dict()])
    assert result['bill']['noop'] == 1
    obj = Bill.objects.get()
    assert obj.versions.count() == 1
    assert obj.versions.get().links.count() == 2

    # different link for second one, update
    bill = ScrapeBill('HB 1', '1900', 'First Bill', chamber='lower')
    bill.add_version_link('printing', 'http://example.com/test.pdf', media_type='application/pdf')
    bill.add_version_link('printing', 'http://example.com/diff-link.txt', media_type='text/plain')
    result = BillImporter('jid', oi).import_data([bill.as_dict()])
    assert result['bill']['update'] == 1
    obj = Bill.objects.get()
    assert obj.versions.count() == 1
    assert obj.versions.get().links.count() == 2

    # delete one, update
    bill = ScrapeBill('HB 1', '1900', 'First Bill', chamber='lower')
    bill.add_version_link('printing', 'http://example.com/test.pdf', media_type='application/pdf')
    result = BillImporter('jid', oi).import_data([bill.as_dict()])
    assert result['bill']['update'] == 1
    obj = Bill.objects.get()
    assert obj.versions.count() == 1
    assert obj.versions.get().links.count() == 1
