from .. import Check
from .common import common_checks


def check(db):
    for meta in db.jurisdictions.find():
        if (meta['_id'] ==
                "ocd-jurisdiction/country:us/state:ex/place:example"):

            yield Check(collection='jurisdictions',
                        id=meta['_id'],
                        tagname='template-data-in-jurisdiction',
                        severity='grave')

        for check in common_checks(meta, 'jurisdiction', 'jurisdictions'):
            yield check

        blacklist = [
            "latest_json_url",
            "latest_json_date",
            "latest_csv_url",
            "latest_csv_date",
        ]

        for entry in blacklist:
            if entry in meta:
                yield Check(collection='jurisdictions',
                            id=meta['_id'],
                            tagname='meta-has-%s' % (entry),
                            severity='important')
