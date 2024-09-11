from datetime import datetime, timezone, timedelta
import sys

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
            "--max",
            type=int,
            default=10,
            help="max number of objects to delete without triggering failsafe",
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
            self.report_stale_objects(args.window)
        else:
            stale_objects = list(self.get_stale_objects(args.window))
            num_stale_objects = len(stale_objects)

            print(
                f"{num_stale_objects} objects in your database have not been seen "
                f"in {args.window} days."
            )

            if num_stale_objects > args.max:
                print(
                    f"{num_stale_objects} exceeds the failsafe limit of {args.max}. "
                    "Run this command with a larger --max value to proceed."
                )
                sys.exit()

            if args.yes:
                print("Proceeding to deletion because you specified --yes.")

            else:
                print(f"Permanently delete {num_stale_objects} objects? [Y/n]")
                response = input()

            if args.yes or response == "Y":
                self.remove_stale_objects(args.window)
                print(f"Removed {num_stale_objects} from your database.")
