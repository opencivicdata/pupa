import os
import json
import datetime
from pupa.core import db
from pupa.models import Organization
from pupa.models.utils import DatetimeValidator
from pupa.models.schemas.jurisdiction import schema as jurisdiction_schema


def import_jurisdiction(org_importer, jurisdiction):
    obj = jurisdiction.get_db_object()

    obj['_type'] = 'jurisdiction'
    obj['_id'] = jurisdiction.jurisdiction_id
    obj['latest_update'] = datetime.datetime.utcnow()

    # validate jurisdiction
    validator = DatetimeValidator()
    try:
        validator.validate(obj, jurisdiction_schema)
    except ValueError as ve:
        raise ve

    db.jurisdictions.save(obj)

    # create organization(s)
    org = Organization(name=jurisdiction.name, classification='legislature',
                       jurisdiction_id=jurisdiction.jurisdiction_id)
    if jurisdiction.other_names:
        org.other_names = jurisdiction.other_names
    if jurisdiction.parent_id:
        org.parent_id = jurisdiction.parent_id

    parent_id = org_importer.import_object(org)

    if jurisdiction.chambers:
        for chamber, properties in jurisdiction.chambers.items():
            org = Organization(name=properties['name'], classification='legislature',
                               chamber=chamber, parent_id=parent_id,
                               jurisdiction_id=jurisdiction.jurisdiction_id)
            org_importer.import_object(org)

    # create parties
    for party in jurisdiction.parties:
        org = Organization(**{'classification': 'party',
                              'name': party['name'],
                              'parent_id': None})
        org_importer.import_object(org)
