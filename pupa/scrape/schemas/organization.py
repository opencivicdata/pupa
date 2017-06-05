from .common import (links, contact_details, identifiers, other_names, sources, extras,
                     fuzzy_date_blank)
from opencivicdata import common

schema = {
    "properties": {
        "name": {"type": "string"},
        "other_names": other_names,
        "identifiers": identifiers,
        "classification": {
            "type": ["string", "null"],
            "enum": common.ORGANIZATION_CLASSIFICATIONS,
        },
        "parent_id": {"type": ["string", "null"]},
        "founding_date": fuzzy_date_blank,
        "dissolution_date": fuzzy_date_blank,
        "image": {"type": "string", "blank": True, "format": "uri"},
        "contact_details": contact_details,
        "links": links,
        "sources": sources,

        # added to popolo
        "jurisdiction_id": {"type": "string"},
        "division_id": {"type": ["string", "null"]},
        "extras": extras,
    },
    "type": "object",
}
