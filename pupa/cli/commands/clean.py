import itertools
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


def get_stale_objects(window):
    """
    Find all database objects that haven't seen been in {window} days.
    """

    from opencivicdata.core.models.base import OCDBase

    ocd_apps = ["core", "legislative"]
    # Check all subclasses of OCDBase
    models = get_subclasses(ocd_apps, OCDBase)

    results = []
    for model in models:
        # Jurisdictions are protected from deletion
        if "Jurisdiction" not in model.__name__:
            cutoff_date = datetime.now(tz=timezone.utc) - timedelta(days=window)
            results.append(model.objects.filter(last_seen__lte=cutoff_date))

    return itertools.chain(*results)


def remove_stale_objects(window):
    """
    Remove all database objects that haven't seen been in {window} days.
    """
    for obj in get_stale_objects(window):
        print(f"Deleting {obj}...")
        obj.delete()


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

    def handle(self, args, other):
        django.setup()

        if args.report:
            print(
                "These objects have not been seen in a scrape within the last"
                f" {args.window} days:"
            )
            for obj in get_stale_objects(args.window):
                print(obj)
        else:
            if not args.noinput:
                print(
                    "This will permanently delete all objects from your database"
                    f" that have not been scraped within the last {args.window}"
                    " days. Are you sure? (Y/N)"
                )
                resp = input()
                if resp != "Y":
                    return

            print(
                "Removing objects that haven't been seen in a scrape within"
                f" the last {args.window} days..."
            )
            remove_stale_objects(args.window)
