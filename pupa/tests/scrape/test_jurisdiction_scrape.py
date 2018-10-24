from collections import defaultdict
from pupa.scrape import Jurisdiction, Organization, JurisdictionScraper


class FakeJurisdiction(Jurisdiction):
    division_id = 'ocd-division/test'
    classification = 'government'
    name = 'Test'
    url = 'http://example.com'

    def get_organizations(self):
        parent = Organization('Congress', classification='legislature')
        yield parent
        yield Organization('House', classification='lower', parent_id=parent)
        yield Organization('Senate', classification='upper', parent_id=parent)


def test_basics():
    # id property and string
    j = FakeJurisdiction()
    assert j.jurisdiction_id == 'ocd-jurisdiction/test/government'
    assert j.name in str(j)


def test_as_dict():
    j = FakeJurisdiction()
    d = j.as_dict()

    assert d['_id'] == j.jurisdiction_id
    assert d['name'] == j.name
    assert d['url'] == j.url
    assert d['legislative_sessions'] == []
    assert d['feature_flags'] == []


def test_jurisdiction_unicam_scrape():
    class UnicameralJurisdiction(Jurisdiction):
        jurisdiction_id = 'unicam'
        name = 'Unicameral'
        url = 'http://example.com'

        def get_organizations(self):
            yield Organization('Unicameral Legislature', classification='legislature')

    j = UnicameralJurisdiction()
    js = JurisdictionScraper(j, '/tmp/')
    objects = list(js.scrape())

    # two objects, first is the Jurisdiction
    assert len(objects) == 2
    assert objects[0] == j

    # ensure we made a single legislature org
    assert isinstance(objects[1], Organization)
    assert objects[1].classification == 'legislature'


def test_jurisdiction_bicameral_scrape():
    j = FakeJurisdiction()
    js = JurisdictionScraper(j, '/tmp/')
    objects = list(js.scrape())
    obj_names = set()
    obj_types = defaultdict(int)

    for o in objects:
        obj_names.add(o.name)
        obj_types[type(o)] += 1

    # ensure Jurisdiction and 5 organizations were found
    assert obj_names == {'Test', 'Congress', 'House', 'Senate'}
    assert obj_types[FakeJurisdiction] == 1
    assert obj_types[Organization] == 3
