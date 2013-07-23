import importlib


MODULE_ROOT = "scruffy.checkers"

ENABLED_CHECKS = [
    "people",
    "orgs",
    "events",
    "votes",
    "bills",
    "memberships",
]


def load_checkers():
    for module in ENABLED_CHECKS:
        mod = importlib.import_module(".".join([MODULE_ROOT, module]))
        yield mod.check
