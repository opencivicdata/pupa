import os
import json
import shutil
import tempfile
import mock
import pytest
from opencivicdata.core.models import Person, Organization, Jurisdiction, Division
from pupa.scrape import Person as ScrapePerson
from pupa.scrape import Organization as ScrapeOrganization
from pupa.importers.base import omnihash, BaseImporter
from pupa.importers import PersonImporter, OrganizationImporter
from pupa.exceptions import UnresolvedIdError, DataImportError


def create_jurisdiction():
    Division.objects.create(id='ocd-division/country:us', name='USA')
    Jurisdiction.objects.create(id='jid', division_id='ocd-division/country:us')


class FakeImporter(BaseImporter):
    _type = 'test'


def test_omnihash_python_types():
    # string
    assert omnihash('test') == omnihash('test')
    # list
    assert omnihash(['this', 'is', 'a', 'list']) == omnihash(['this', 'is', 'a', 'list'])
    # set
    assert omnihash({'and', 'a', 'set'}) == omnihash({'set', 'set', 'and', 'a'})
    # dict w/ set and tuple as well
    assert (omnihash({'a': {('fancy', 'nested'): {'dict'}}}) ==
            omnihash({'a': {('fancy', 'nested'): {'dict'}}}))


def test_import_directory():
    # write out some temp data to filesystem
    datadir = tempfile.mkdtemp()
    dicta = {'test': 'A'}
    dictb = {'test': 'B'}
    open(os.path.join(datadir, 'test_a.json'), 'w').write(json.dumps(dicta))
    open(os.path.join(datadir, 'test_b.json'), 'w').write(json.dumps(dictb))

    # simply ensure that import directory calls import_data with all dicts
    ti = FakeImporter('jurisdiction-id')
    with mock.patch.object(ti, attribute='import_data') as mockobj:
        ti.import_directory(datadir)

    # import_data should be called once
    assert mockobj.call_count == 1
    # kind of hacky, get the total list of args passed in
    arg_objs = list(mockobj.call_args[0][0])

    # 2 args only, make sure a and b are in there
    assert len(arg_objs) == 2
    assert dicta in arg_objs
    assert dictb in arg_objs

    # clean up datadir
    shutil.rmtree(datadir)


def test_apply_transformers():
    transformers = {
        'capitalize': lambda x: x.upper(),
        'cap_and_reverse': [lambda x: x.upper(), lambda y: y[::-1]],
        'never_used': lambda x: 1/0,
        'nested': {'replace': lambda x: 'replaced'},
    }
    data = {
        'capitalize': 'words',
        'cap_and_reverse': 'simple',
        'nested': {'replace': None},
    }
    ti = FakeImporter('jid')
    ti.cached_transformers = transformers
    output = ti.apply_transformers(data)
    assert output['capitalize'] == 'WORDS'
    assert output['cap_and_reverse'] == 'ELPMIS'
    assert output['nested']['replace'] == 'replaced'


# doing these next few tests just on a Person because it is the same code that handles it
# but for completeness maybe it is better to do these on each type?


@pytest.mark.django_db
def test_deduplication_identical_object():
    p1 = ScrapePerson('Dwayne').as_dict()
    p2 = ScrapePerson('Dwayne').as_dict()
    PersonImporter('jid').import_data([p1, p2])

    assert Person.objects.count() == 1


@pytest.mark.django_db
def test_exception_on_identical_objects_in_import_stream():
    create_jurisdiction()
    # these two objects aren't identical, but refer to the same thing
    # at the moment we consider this an error (but there may be a better way to handle this?)
    o1 = ScrapeOrganization('X-Men', classification='unknown').as_dict()
    o2 = ScrapeOrganization('X-Men', founding_date='1970', classification='unknown').as_dict()

    with pytest.raises(Exception):
        OrganizationImporter('jid').import_data([o1, o2])


@pytest.mark.django_db
def test_resolve_json_id():
    p1 = ScrapePerson('Dwayne').as_dict()
    p2 = ScrapePerson('Dwayne').as_dict()
    pi = PersonImporter('jid')

    # do import and get database id
    p1_id = p1['_id']
    p2_id = p2['_id']
    pi.import_data([p1, p2])
    db_id = Person.objects.get().id

    # simplest case
    assert pi.resolve_json_id(p1_id) == db_id
    # duplicate should resolve to same id
    assert pi.resolve_json_id(p2_id) == db_id
    # a null id should map to None
    assert pi.resolve_json_id(None) is None
    # no such id
    with pytest.raises(UnresolvedIdError):
        pi.resolve_json_id('this-is-invalid')


@pytest.mark.django_db
def test_invalid_fields():
    p1 = ScrapePerson('Dwayne').as_dict()
    p1['newfield'] = "shouldn't happen"

    with pytest.raises(DataImportError):
        PersonImporter('jid').import_data([p1])


@pytest.mark.django_db
def test_invalid_fields_related_item():
    p1 = ScrapePerson('Dwayne')
    p1.add_link('http://example.com')
    p1 = p1.as_dict()
    p1['links'][0]['test'] = 3

    with pytest.raises(DataImportError):
        PersonImporter('jid').import_data([p1])


@pytest.mark.django_db
def test_locked_field():
    create_jurisdiction()
    org = ScrapeOrganization('SHIELD').as_dict()
    oi = OrganizationImporter('jid')
    oi.import_data([org])

    # set date and lock field
    o = Organization.objects.get()
    o.dissolution_date = '2015'
    o.locked_fields = ['dissolution_date']
    o.save()

    # reimport
    org = ScrapeOrganization('SHIELD').as_dict()
    oi = OrganizationImporter('jid')
    oi.import_data([org])

    o = Organization.objects.get()
    assert o.dissolution_date == '2015'
    assert o.locked_fields == ['dissolution_date']

    # do it a third time to check for the locked_fields reversion issue
    org = ScrapeOrganization('SHIELD').as_dict()
    oi = OrganizationImporter('jid')
    oi.import_data([org])

    o = Organization.objects.get()
    assert o.dissolution_date == '2015'
    assert o.locked_fields == ['dissolution_date']


@pytest.mark.django_db
def test_locked_field_subitem():
    create_jurisdiction()
    org = ScrapeOrganization('SHIELD')
    org.add_name('S.H.I.E.L.D.')
    oi = OrganizationImporter('jid')
    oi.import_data([org.as_dict()])

    # lock the field
    o = Organization.objects.get()
    o.locked_fields = ['other_names']
    o.save()

    # reimport
    org = ScrapeOrganization('SHIELD').as_dict()
    oi = OrganizationImporter('jid')
    oi.import_data([org])

    o = Organization.objects.get()
    assert o.other_names.get().name == 'S.H.I.E.L.D.'
