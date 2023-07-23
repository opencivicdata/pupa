import pytest
import argparse
from datetime import datetime, timezone, timedelta
from freezegun import freeze_time

from opencivicdata.core.models import Person, Organization, Jurisdiction, Division

from pupa.cli.commands.clean import Command


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


def create_jurisdiction():
    Division.objects.create(id="ocd-division/country:us", name="USA")
    return Jurisdiction.objects.create(id="jid", division_id="ocd-division/country:us")


@pytest.mark.django_db
def test_get_stale_objects(subparsers):
    _ = create_jurisdiction()
    o = Organization.objects.create(name="WWE", jurisdiction_id="jid")
    p = Person.objects.create(name="George Washington", family_name="Washington")
    m = p.memberships.create(organization=o)

    expected_stale_objects = {p, o, m}

    a_week_from_now = datetime.now(tz=timezone.utc) + timedelta(days=7)
    with freeze_time(a_week_from_now):
        p = Person.objects.create(name="Thomas Jefferson", family_name="Jefferson")
        p.memberships.create(organization=o)
        assert set(Command(subparsers).get_stale_objects(7)) == expected_stale_objects


@pytest.mark.django_db
def test_remove_stale_objects(subparsers):
    _ = create_jurisdiction()
    o = Organization.objects.create(name="WWE", jurisdiction_id="jid")
    p = Person.objects.create(name="George Washington", family_name="Washington")
    m = p.memberships.create(organization=o)

    expected_stale_objects = {p, o, m}

    a_week_from_now = datetime.now(tz=timezone.utc) + timedelta(days=7)
    with freeze_time(a_week_from_now):
        p = Person.objects.create(name="Thomas Jefferson", family_name="Jefferson")
        p.memberships.create(organization=o)

        Command(subparsers).remove_stale_objects(7)
        for obj in expected_stale_objects:
            was_deleted = not type(obj).objects.filter(id=obj.id).exists()
            assert was_deleted


@pytest.mark.django_db
def test_clean_command(subparsers):
    _ = create_jurisdiction()
    o = Organization.objects.create(name="WWE", jurisdiction_id="jid")

    stale_person = Person.objects.create(
        name="George Washington", family_name="Washington"
    )
    stale_membership = stale_person.memberships.create(organization=o)

    a_week_from_now = datetime.now(tz=timezone.utc) + timedelta(days=7)
    with freeze_time(a_week_from_now):
        not_stale_person = Person.objects.create(
            name="Thomas Jefferson", family_name="Jefferson"
        )
        not_stale_membership = not_stale_person.memberships.create(organization=o)
        o.save()  # Update org's last_seen field

        # Call clean command
        Command(subparsers).handle(
            argparse.Namespace(noinput=True, report=False, window=7), []
        )

        expected_stale_objects = {stale_person, stale_membership}
        for obj in expected_stale_objects:
            was_deleted = not type(obj).objects.filter(id=obj.id).exists()
            assert was_deleted

        expected_not_stale_objects = {o, not_stale_person, not_stale_membership}
        for obj in expected_not_stale_objects:
            was_not_deleted = type(obj).objects.filter(id=obj.id).exists()
            assert was_not_deleted


@pytest.mark.django_db
def test_clean_command_failsafe(subparsers):
    _ = create_jurisdiction()
    o = Organization.objects.create(name="WWE", jurisdiction_id="jid")

    stale_people = [
        Person.objects.create(name="George Washington", family_name="Washington")
        for i in range(20)
    ]
    stale_memberships = [ # noqa
        p.memberships.create(organization=o) for p in stale_people
    ]

    a_week_from_now = datetime.now(tz=timezone.utc) + timedelta(days=7)
    with freeze_time(a_week_from_now):
        with pytest.raises(SystemExit):
            # Should trigger failsafe exist when deleting more than 10 objects
            Command(subparsers).handle(
                argparse.Namespace(noinput=True, report=False, window=7), []
            )
