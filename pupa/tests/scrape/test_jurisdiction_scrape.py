from collections import defaultdict
from pupa.scrape import Jurisdiction, Organization, JurisdictionScraper


class FakeJurisdiction(Jurisdiction):
    jurisdiction_id = 'test'
    name = 'Test'
    url = 'http://example.com'
    division_id = 'division'

    organizations = [Organization('House', chamber='lower'),
                     Organization('Senate', chamber='upper')]

    parties = [{'name': 'Republican'}, {'name': 'Democratic'}]


def test_basics():
    # id property and string
    j = FakeJurisdiction()

    j.jurisdiction_id = 'test'
    assert j._id == 'test'
    j._id = 'new'
    assert j.jurisdiction_id == 'new'

    assert j.name in str(j)


def test_as_dict():
    j = FakeJurisdiction()
    d = j.as_dict()

    assert d['_id'] == j._id
    assert d['name'] == j.name
    assert d['url'] == j.url
    assert d['sessions'] == []
    assert d['feature_flags'] == []


#def test_get_organization_by_chamber():
#    j = TestJurisdiction()

#    assert j.get_organization(chamber='lower').name == 'House'

#    with pytest.raises(ValueError):
#        j.get_organization(chamber='joint')

#    assert j.get_organization(party='Republican').name == 'Republican'

#    with pytest.raises(ValueError):
#        j.get_organization(party='Green')


def test_jurisdiction_unicam_scrape():
    class UnicameralJurisdiction(Jurisdiction):
        jurisdiction_id = 'unicam'
        name = 'Unicameral'
        url = 'http://example.com'

    j = UnicameralJurisdiction()
    js = JurisdictionScraper(j, '/tmp/')
    objects = list(js.scrape())

    # two objects, first is the Jurisdiction
    assert len(objects) == 2
    assert objects[0] == j

    # ensure we made a single legislature org as well
    assert isinstance(objects[1], Organization)
    assert objects[1].classification == 'legislature'
    assert objects[1].sources[0]['url'] == j.url


def test_jurisdiction_bicameral_scrape():
    j = FakeJurisdiction()
    js = JurisdictionScraper(j, '/tmp/')
    objects = list(js.scrape())
    obj_names = set()
    obj_types = defaultdict(int)

    for o in objects:
        obj_names.add(o.name)
        obj_types[type(o)] += 1

    # ensure Jurisdiction and 4 organizations were found
    assert obj_names == {'Test', 'House', 'Senate', 'Democratic', 'Republican'}
    assert obj_types[FakeJurisdiction] == 1
    assert obj_types[Organization] == 4
