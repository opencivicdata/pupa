import sys
from datetime import datetime, timezone, timedelta

import django
from django.apps import apps
from .base import BaseCommand


def get_subclasses(app_list, abstract_class):
    """
    Finds and returns all subclasses of an abstract class.
    """
    result = []
    for app in app_list:
        for model in apps.get_app_config(app).get_models():
            if issubclass(model, abstract_class) and model is not abstract_class:
                result.append(model)
        return result


class Command(BaseCommand):
    name = "clean"
    help = "Removes database objects that haven't been seen in recent scrapes"

    def add_args(self):
        self.add_argument(
            "--window",
            type=int,
            default=7,
            help=(
                "objects not seen in this many days will be deleted from the database"
            ),
        )
        self.add_argument(
            "--report",
            action="store_true",
            help=(
                "generate a report of what objects this command"
                " would delete without making any changes to the database"
            ),
        )
        self.add_argument(
            "--noinput",
            action="store_true",
            help="delete objects without getting user confirmation",
        )
        self.add_argument(
            "--yes",
            action="store_true",
            help="assumes an answer of 'yes' to all interactive prompts",
            default=False,
        )

    def get_stale_objects(self, window):
        """
        Find all database objects that haven't seen been in {window} days.
        """

        from opencivicdata.core.models.base import OCDBase

        ocd_apps = ["core", "legislative"]
        # Check all subclasses of OCDBase
        models = get_subclasses(ocd_apps, OCDBase)

        for model in models:
            # Jurisdictions are protected from deletion
            if "Jurisdiction" not in model.__name__:
                cutoff_date = datetime.now(tz=timezone.utc) - timedelta(days=window)
                yield from model.objects.filter(last_seen__lte=cutoff_date).iterator()

    def remove_stale_objects(self, window):
        """
        Remove all database objects that haven't seen been in {window} days.
        """

        for obj in self.get_stale_objects(window):
            print(f"Deleting {obj}...")
            obj.delete()

    def report_stale_objects(self, window):
        """
        Print all database objects that haven't seen been in {window} days.
        """
        for obj in self.get_stale_objects(window):
            print(obj)

    def handle(self, args, other):
        django.setup()

        if args.report:
            print(
                "These objects have not been seen in a scrape within the last"
                f" {args.window} days:"
            )
            self.report_stale_objects()
        else:
            stale_objects = list(self.get_stale_objects(args.window))
            num_stale_objects = len(stale_objects)

            if args.noinput and args.yes:
                self.remove_stale_objects(args.window)
                sys.exit()

            if args.noinput:
                # Fail-safe to avoid deleting a large amount of objects
                # without explicit confimation
                if num_stale_objects > 10:
                    print(
                        f"This command would delete {num_stale_objects} objects: "
                        f"\n{stale_objects}"
                        "\nIf you're sure, re-run without --noinput to provide confirmation."
                        "\nOr re-run with --yes to assume a yes answer to all prompts."
                    )
                    sys.exit(1)
            else:
                print(
                    f"This will permanently delete"
                    f" {num_stale_objects} objects from your database"
                    f" that have not been scraped within the last {args.window}"
                    " days. Are you sure? (Y/N)"
                )
                resp = input()
                if resp != "Y":
                    sys.exit()

            print(
                "Removing objects that haven't been seen in a scrape within"
                f" the last {args.window} days..."
            )
            self.remove_stale_objects(args.window)
