import datetime
from pupa.core import db
from pupa.models import Organization
from pupa.models.utils import DatetimeValidator
from pupa.models.schemas.jurisdiction import schema as jurisdiction_schema


def import_jurisdiction(org_importer, jurisdiction):
    obj['_type'] = 'jurisdiction'
    obj['_id'] = jurisdiction.jurisdiction_id

    if not obj['_id'].startswith("ocd-jurisdiction/"):
        raise ValueError("Jurisdiction ids must start with 'ocd-jurisdiction'. (%s)" % (
            jurisdiction.jurisdiction_id))
