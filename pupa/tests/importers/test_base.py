import os
import json
import shutil
import tempfile
import mock
import pytest
from pupa.importers.base import omnihash, BaseImporter
from opencivicdata.models import Person


class TestImporter(BaseImporter):
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
    ti = TestImporter('jurisdiction-id')
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
