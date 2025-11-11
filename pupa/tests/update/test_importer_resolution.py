import sys
import types
import pytest

from django.utils.module_loading import import_string

from pupa.cli.commands import update
from pupa.exceptions import CommandError


@pytest.fixture(params=[
    "JurisdictionImporter",
    "OrganizationImporter",
    "PersonImporter",
    "PostImporter",
    "MembershipImporter",
    "BillImporter",
    "VoteEventImporter",
    "EventImporter",
])
def importer_test_case(request):
    return request.param


@pytest.fixture
def custom_importer():
    """
    Create a module object at runtime with a single class inside, and insert it
    into sys.modules so import_string() can load it by dotted path.
    """
    module_name, class_name = ["tests.fixtures.custom_importers", "MyCustomImporter"]

    module = types.ModuleType("tests.fixtures.custom_importers")
    cls = type(class_name, (), {})
    setattr(module, class_name, cls)
    sys.modules[module_name] = module

    return cls, module_name


def test_resolve_custom_importer(custom_importer, settings, importer_test_case):
    cls, module_name = custom_importer
    settings.IMPORTER_CLASSES = {importer_test_case: f"{module_name}.{cls.__name__}"}
    resolved = update.resolve_importer(importer_test_case)
    assert resolved is cls


def test_resolve_default_importer(importer_test_case):
    expected_importer = import_string(f"pupa.importers.{importer_test_case}")
    resolved_importer = update.resolve_importer(importer_test_case)
    assert resolved_importer is expected_importer


def test_resolve_bad_path_raises_error(settings):
    settings.IMPORTER_CLASSES = {"PersonImporter": "non.existent.Path"}
    with pytest.raises(CommandError):
        update.resolve_importer("PersonImporter")
