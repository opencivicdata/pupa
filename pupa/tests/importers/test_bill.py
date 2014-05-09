import pytest
from pupa.scrape import Bill as ScrapeBill
from pupa.importers import BillImporter, OrganizationImporter
from opencivicdata.models import Bill, Jurisdiction, JurisdictionSession, Person


@pytest.mark.django_db
def test_full_bill():
    j = Jurisdiction.objects.create(id='jid', division_id='did')
    j.sessions.create(name='1899')
    j.sessions.create(name='1900')
    person = Person.objects.create(id='person-id', name='Adam Smith')

    oldbill = ScrapeBill('HB 99', '1899', 'Axe & Tack Tax Act', classification='tax bill')

    bill = ScrapeBill('HB 1', '1900', 'Axe & Tack Tax Act', classification='tax bill')
    bill.subject = ['taxes', 'axes']
    bill.add_name('SB 9')
    bill.add_title('Tack & Axe Tax Act')
    bill.add_related_bill("HB 99", session="1899", relation_type="prior-session")
    bill.add_sponsor('Adam Smith', classification='extra sponsor', entity_type='person',
                     primary=False, entity_id=person.id)
    bill.add_sponsor('Jane Smith', classification='lead sponsor', entity_type='person',
                     primary=True)
    bill.add_summary('This is an act about axes and taxes and tacks.', note="official")
    bill.add_document_link('Fiscal Note', 'http://example.com/fn.pdf', mimetype='application/pdf')
    bill.add_document_link('Fiscal Note', 'http://example.com/fn.html', mimetype='text/html')
    bill.add_version_link('Fiscal Note', 'http://example.com/v/1', mimetype='text/html')
    bill.add_source('http://example.com/source')

    # import bill
    oi = OrganizationImporter('jid')
    BillImporter('jid', oi).import_data([oldbill.as_dict(), bill.as_dict()])

    # get bill from db and assert it imported correctly
    b = Bill.objects.get(name='HB 1')
    assert b.name == bill.name
    assert b.title == bill.title
    assert b.classification == bill.classification
    assert b.subject == ['taxes', 'axes']
    assert b.summaries.get().note == 'official'

    # other_title, other_name added
    assert b.other_titles.get().text == 'Tack & Axe Tax Act'
    assert b.other_names.get().name == 'SB 9'

    # related_bills were added
    assert b.related_bills.all()[0].related_bill.name == 'HB 99'

    # sponsors added, linked & unlinked
    sponsors = b.sponsors.all()
    assert len(sponsors) == 2
    for sponsor in sponsors:
        if sponsor.primary:
            assert sponsor.person == None
            assert sponsor.organization == None
        else:
            assert sponsor.person == person

    # versions & documents with their links
    versions = b.versions.all()
    assert len(versions) == 1
    assert versions[0].links.count() == 1
    documents = b.documents.all()
    assert len(documents) == 1
    assert documents[0].links.count() == 2

    # sources
    assert b.sources.count() == 1
