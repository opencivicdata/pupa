import pytest
from pupa.scrape import Jurisdiction as JurisdictionBase
from pupa.importers import JurisdictionImporter
from opencivicdata.core.models import Jurisdiction, Division
from opencivicdata.legislative.models import LegislativeSession


class FakeJurisdiction(JurisdictionBase):
    division_id = 'ocd-division/country:us'
    name = 'test'
    url = 'http://example.com'
    classification = 'government'

    legislative_sessions = [
        {'identifier': '2015', 'name': '2015 Regular Session'},
        {'identifier': '2016', 'name': '2016 Regular Session'},
    ]


@pytest.mark.django_db
def test_jurisdiction_import():
    Division.objects.create(id='ocd-division/country:us', name='USA')
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
    Division.objects.create(id='ocd-division/country:us', name='USA')
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
    assert Jurisdiction.objects.get().name == 'different name'


@pytest.mark.django_db
def test_jurisdiction_merge_related():
    Division.objects.create(id='ocd-division/country:us', name='USA')
    # need to ensure legislative_sessions don't get deleted
    ji = JurisdictionImporter('jurisdiction-id')
    tj = FakeJurisdiction()
    ji.import_item(tj.as_dict())

    assert LegislativeSession.objects.count() == 2

    # disallow deletion of legislative sessions as it can remove bills
    tj.legislative_sessions.pop()
    ji.import_item(tj.as_dict())

    # should still have two
    assert LegislativeSession.objects.count() == 2

    # now will have three
    tj.legislative_sessions.append({'identifier': '2017', 'name': '2017 Session'})
    ji.import_item(tj.as_dict())
    assert LegislativeSession.objects.count() == 3

    # and test that the non-identifier fields actually update
    tj.legislative_sessions.append({'identifier': '2016', 'name': 'updated'})
    ji.import_item(tj.as_dict())
    assert LegislativeSession.objects.count() == 3
    assert LegislativeSession.objects.get(identifier='2016').name == 'updated'
