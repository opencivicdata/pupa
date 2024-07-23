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


@pytest.fixture
def jurisdiction():
    Division.objects.create(id="ocd-division/country:us", name="USA")
    return Jurisdiction.objects.create(id="jid", division_id="ocd-division/country:us")


@pytest.fixture
def organization(jurisdiction):
    return Organization.objects.create(name="WWE", jurisdiction_id="jid")


@pytest.fixture
def person():
    class PersonFactory:
        def build(self, **kwargs):
            person_info = {
                "name": "George Washington",
                "family_name": "Washington",
            }

            person_info.update(kwargs)

            return Person.objects.create(**person_info)

    return PersonFactory()


@pytest.mark.django_db
def test_get_stale_objects(subparsers, organization, person):
    stale_person = person.build()
    membership = stale_person.memberships.create(organization=organization)

    expected_stale_objects = {stale_person, organization, membership}

    a_week_from_now = datetime.now(tz=timezone.utc) + timedelta(days=7)
    with freeze_time(a_week_from_now):
        fresh_person = person.build(name="Thomas Jefferson", family_name="Jefferson")
        fresh_person.memberships.create(organization=organization)
        assert set(Command(subparsers).get_stale_objects(7)) == expected_stale_objects


@pytest.mark.django_db
def test_remove_stale_objects(subparsers, organization, person):
    stale_person = person.build()
    membership = stale_person.memberships.create(organization=organization)

    expected_stale_objects = {stale_person, organization, membership}

    a_week_from_now = datetime.now(tz=timezone.utc) + timedelta(days=7)
    with freeze_time(a_week_from_now):
        fresh_person = person.build(name="Thomas Jefferson", family_name="Jefferson")
        fresh_person.memberships.create(organization=organization)

        Command(subparsers).remove_stale_objects(7)
        for obj in expected_stale_objects:
            was_deleted = not type(obj).objects.filter(id=obj.id).exists()
            assert was_deleted


@pytest.mark.django_db
def test_clean_command(subparsers, organization, person):
    stale_person = person.build()
    stale_membership = stale_person.memberships.create(organization=organization)

    a_week_from_now = datetime.now(tz=timezone.utc) + timedelta(days=7)
    with freeze_time(a_week_from_now):
        fresh_person = person.build(name="Thomas Jefferson", family_name="Jefferson")
        not_stale_membership = fresh_person.memberships.create(
            organization=organization
        )
        organization.save()  # Update org's last_seen field

        # Call clean command
        Command(subparsers).handle(
            argparse.Namespace(report=False, window=7, yes=True, max=10), []
        )

        expected_stale_objects = {stale_person, stale_membership}
        for obj in expected_stale_objects:
            was_deleted = not type(obj).objects.filter(id=obj.id).exists()
            assert was_deleted

        expected_not_stale_objects = {organization, fresh_person, not_stale_membership}
        for obj in expected_not_stale_objects:
            was_not_deleted = type(obj).objects.filter(id=obj.id).exists()
            assert was_not_deleted


@pytest.mark.django_db
def test_clean_command_failsafe(subparsers, organization, person):
    stale_people = [person.build() for i in range(20)]
    for p in stale_people:
        p.memberships.create(organization=organization)

    a_week_from_now = datetime.now(tz=timezone.utc) + timedelta(days=7)
    with freeze_time(a_week_from_now):
        with pytest.raises(SystemExit):
            # Should trigger failsafe exist when deleting more than 10 objects
            Command(subparsers).handle(
                argparse.Namespace(report=False, window=7, yes=False, max=10), []
            )

        with pytest.raises(SystemExit):
            # Should trigger failsafe exist when deleting more than 10 objects,
            # even when yes is specified
            Command(subparsers).handle(
                argparse.Namespace(report=False, window=7, yes=True, max=10), []
            )

        # Should proceed without error, since max is increased (1 organization,
        # 20 people, 20 memberships)
        Command(subparsers).handle(
            argparse.Namespace(report=False, window=7, max=41, yes=True), []
        )
