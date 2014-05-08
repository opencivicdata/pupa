import pytest
from pupa.scrape import Bill as ScrapeBill
from pupa.importers import BillImporter, OrganizationImporter
from opencivicdata.models import Bill, Jurisdiction, JurisdictionSession


@pytest.mark.django_db
def test_full_bill():
    j = Jurisdiction.objects.create(id='jid', division_id='did')
    j.sessions.create(name='1900')

    bill = ScrapeBill('HB 1', '1900', 'Axe & Tack Tax Act', classification='tax bill')
    #bill.add_name('SB 9')
    #bill.add_title('Tack & Axe Tax Act')
    bill.add_version_link('Fiscal Note', 'http://example.com/v/1', mimetype='text/html')
    bill.add_document_link('Fiscal Note', 'http://example.com/fn.pdf', mimetype='application/pdf')
    bill.add_document_link('Fiscal Note', 'http://example.com/fn.html', mimetype='text/html')
    bill.add_source('http://example.com/source')
    bill.add_subject('taxes')
    bill.add_subject('axes')

    # import bill
    oi = OrganizationImporter('jid')
    BillImporter('jid', oi).import_data([bill.as_dict()])

    # get bill from db and assert it imported correctly
    b = Bill.objects.get()
    assert b.name == bill.name
    assert b.title == bill.title
    assert b.classification == bill.classification
    #assert b.subjects == ['taxes', 'axes']
    versions = b.versions.all()
    assert len(versions) == 1
    assert versions[0].links.count() == 1
    documents = b.documents.all()
    assert len(documents) == 1
    assert documents[0].links.count() == 2
    assert b.sources.count() == 1
