import pytest

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
