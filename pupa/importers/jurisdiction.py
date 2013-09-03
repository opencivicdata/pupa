import os
import json
import datetime
from pupa.core import db
from pupa.models import Organization
from pupa.models.utils import DatetimeValidator
from pupa.models.schemas.metadata import schema as metadata_schema


def import_jurisdiction(org_importer, jurisdiction):
    metadata = jurisdiction.get_metadata()

    metadata['_type'] = 'metadata'
    metadata['_id'] = jurisdiction.jurisdiction_id
    metadata['latest_update'] = datetime.datetime.utcnow()

    # validate metadata
    validator = DatetimeValidator()
    try:
        validator.validate(metadata, metadata_schema)
    except ValueError as ve:
        raise ve

    db.metadata.save(metadata)

    # create organization
    org = Organization(name=metadata['name'], classification='legislature',
                       jurisdiction_id=jurisdiction.jurisdiction_id)
    if 'other_names' in metadata:
        org.other_names = metadata['other_names']
    if 'parent_id' in metadata:
        org.parent_id = metadata['parent_id']

    org_importer.import_object(org)

    # create parties
    for party in metadata['parties']:
        org = Organization(**{#'_type': 'organization',
                              'classification': 'party',
                              'name': party['name'],
                              'parent_id': None})
        org_importer.import_object(org)
