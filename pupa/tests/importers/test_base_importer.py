import os
import json
import shutil
import tempfile
import mock
import pytest
from pupa.scrape import Person as ScrapePerson
from pupa.importers.base import omnihash, BaseImporter
from pupa.importers import PersonImporter
from opencivicdata.models import Person


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
    arg_objs = mockobj.call_args[0][0]

    # 2 args only, make sure a and b are in there
    assert len(arg_objs) == 2
    assert dicta in mockobj.call_args[0][0]
    assert dictb in mockobj.call_args[0][0]

    # clean up datadir
    shutil.rmtree(datadir)


# doing these next few tests just on a Person because it is the same code that handles it
# but for completeness maybe it is better to do these on each type?


@pytest.mark.django_db
def test_deduplication_identical_object():
    p1 = ScrapePerson('Dwayne').as_dict()
    p2 = ScrapePerson('Dwayne').as_dict()
    PersonImporter('jid').import_data([p1, p2])

    assert Person.objects.count() == 1


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
    with pytest.raises(ValueError):
        pi.resolve_json_id('this-is-invalid')


@pytest.mark.django_db
def test_invalid_fields():
    p1 = ScrapePerson('Dwayne').as_dict()
    p1['newfield'] = "shouldn't happen"

    with pytest.raises(TypeError):
        PersonImporter('jid').import_data([p1])


@pytest.mark.django_db
def test_invalid_fields_related_item():
    p1 = ScrapePerson('Dwayne')
    p1.add_link('http://example.com')
    p1 = p1.as_dict()
    p1['links'][0]['test'] = 3

    with pytest.raises(TypeError):
        PersonImporter('jid').import_data([p1])
