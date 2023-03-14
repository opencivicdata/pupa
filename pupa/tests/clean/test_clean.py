import pytest
import argparse

from datetime import datetime, timezone, timedelta
from freezegun import freeze_time

from opencivicdata.core.models import Person, Organization, Jurisdiction, Division

from pupa.cli.commands.clean import Command


def create_jurisdiction():
    Division.objects.create(id="ocd-division/country:us", name="USA")
    return Jurisdiction.objects.create(id="jid", division_id="ocd-division/country:us")


@pytest.fixture
def subparsers():
    parser = argparse.ArgumentParser("pupa", description="pupa CLI")
    parser.add_argument("--debug", action="store_true", help="open debugger on error")
    parser.add_argument(
        "--loglevel",
        default="INFO",
        help=(
            "set log level. options are: "
            "DEBUG|INFO|WARNING|ERROR|CRITICAL "
            "(default is INFO)"
        ),
    )
    return parser.add_subparsers(dest="subcommand")


@pytest.mark.django_db
def test_get_stale_objects(subparsers):
    j = create_jurisdiction()
    o = Organization.objects.create(name="WWE", jurisdiction_id="jid")
    p = Person.objects.create(name="George Washington", family_name="Washington")
    m = p.memberships.create(organization=o)

    expected_stale_objects = {p, o, m}

    a_week_from_now = datetime.now(tz=timezone.utc) + timedelta(days=7)
    with freeze_time(a_week_from_now):
        p = Person.objects.create(name="Thomas Jefferson", family_name="Jefferson")
        j.save()
        p.memberships.create(organization=o)
        assert set(Command(subparsers).get_stale_objects(7)) == expected_stale_objects


@pytest.mark.django_db
def test_remove_stale_objects(subparsers):
    j = create_jurisdiction()
    o = Organization.objects.create(name="WWE", jurisdiction_id="jid")
    p = Person.objects.create(name="George Washington", family_name="Washington")
    m = p.memberships.create(organization=o)

    expected_stale_objects = {p, o, m}

    a_week_from_now = datetime.now(tz=timezone.utc) + timedelta(days=7)
    with freeze_time(a_week_from_now):
        p = Person.objects.create(name="Thomas Jefferson", family_name="Jefferson")
        p.memberships.create(organization=o)

        j.save()

        Command(subparsers).remove_stale_objects(7)
        for obj in expected_stale_objects:
            was_deleted = not type(obj).objects.filter(id=obj.id).exists()
            assert was_deleted
