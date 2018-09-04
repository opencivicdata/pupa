from datetime import datetime

import pytest

from pupa.utils.generic import format_datetime
from pupa.cli.commands.update import override_settings


class _Settings:
    pass


@pytest.fixture
def settings():
    ret = _Settings()
    ret.foo = 'bar'
    ret.baz = 'bob'
    return ret


def test_override_settings(settings):
    with override_settings(settings, {'baz': 'fez'}):
        assert settings.foo == 'bar'
        assert settings.baz == 'fez'
    assert settings.foo == 'bar'
    assert settings.baz == 'bob'


def test_override_settings_unset(settings):
    with override_settings(settings, {'qux': 'fez'}):
        assert settings.qux == 'fez'
    assert not hasattr(settings, 'qux')


def test_format_datetime():
    utc_datetime_obj = datetime.strptime('Sep 04 2018 09:03AM', '%b %d %Y %I:%M%p')
    iso_format = "2018-09-04T09:03:00-05:00"
    assert format_datetime(utc_datetime_obj, "US/Central") == iso_format
