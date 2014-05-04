import pytest
from pupa.scrape import Jurisdiction as JurisdictionBase
from pupa.importers import JurisdictionImporter
from opencivicdata.models import Jurisdiction


class TestJurisdiction(JurisdictionBase):
    jurisdiction_id = 'jurisdiction-id'
    division_id = 'division-id'
    name = 'test'
    url = 'http://example.com'


@pytest.mark.django_db
def test_jurisdiction_data():
    tj = TestJurisdiction()
    juris_dict = tj.as_dict()
    JurisdictionImporter('jurisdiction-id').import_data([juris_dict])

    dbj = Jurisdiction.objects.get()
    assert dbj.id == tj.jurisdiction_id
    assert dbj.division_id == tj.division_id
    assert dbj.name == tj.name
    assert dbj.url == tj.url
