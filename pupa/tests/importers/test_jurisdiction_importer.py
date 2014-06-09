import pytest
from pupa.scrape import Jurisdiction as JurisdictionBase
from pupa.importers import JurisdictionImporter
from opencivicdata.models import Jurisdiction


class FakeJurisdiction(JurisdictionBase):
    division_id = 'division-id'
    name = 'test'
    url = 'http://example.com'
    classification = 'government'


@pytest.mark.django_db
def test_jurisdiction_import():
    tj = FakeJurisdiction()
    juris_dict = tj.as_dict()
    JurisdictionImporter('jurisdiction-id').import_data([juris_dict])

    dbj = Jurisdiction.objects.get()
    assert dbj.id == tj.jurisdiction_id
    assert dbj.division_id == tj.division_id
    assert dbj.name == tj.name
    assert dbj.url == tj.url


@pytest.mark.django_db
def test_jurisdiction_update():
    tj = FakeJurisdiction()
    ji = JurisdictionImporter('jurisdiction-id')
    _, what = ji.import_item(tj.as_dict())
    assert what == 'insert'

    _, what = ji.import_item(tj.as_dict())
    assert what == 'noop'
    assert Jurisdiction.objects.count() == 1

    tj.name = 'different name'
    obj, what = ji.import_item(tj.as_dict())
    assert what == 'update'
    assert Jurisdiction.objects.count() == 1
    assert obj.name == 'different name'
