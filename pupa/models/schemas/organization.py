from .common import links, contact_details, identifiers, other_names, sources
from pupa.core import settings

schema = {
    "properties": {
        "classification": {
            "description": "An organization category, e.g. committee",
            "type": ["string", "null"],
            "enum": settings.ORGANIZATION_CLASSIFICATIONS,
        },
        "dissolution_date": {
            "description": "A date of dissolution",
            "pattern": "^[0-9]{4}(-[0-9]{2}){0,2}$",
            "type": ["string", "null"],
        },
        "founding_date": {
            "description": "A date of founding",
            "pattern": "^[0-9]{4}(-[0-9]{2}){0,2}$",
            "type": ["string", "null"],
        },

        "updated_at": {
            "description": "The time at which the resource was last modified",
            "type": ["string", "datetime", "null"],
        },
        "created_at": {
            "description": "The time at which the resource was created",
            "type": ["string", "datetime", "null"],
        },

        "identifiers": identifiers,
        "other_names": other_names,
        "contact_details": contact_details,
        "links": links,

        "name": {
            "description": "A primary name, e.g. a legally recognized name",
            "type": "string"
        },
        "parent_id": {
            "description": "The ID of the organization that contains this organization",
            "type": ["string", "null"],
        },
        "image": {
            "description": "A URL of an image",
            "type": ["string", "null"],
        },
        "sources": sources,
    },
    "title": "Organization",
    "type": "object",
    "_order": (
        ('Basics', ('name', 'classification', 'parent_id', 'contact_details', 'links')),
        ('Posts', ('posts',)),
        ('Extended Details', ('founding_date', 'dissolution_date',)),
        ('Alternate Names/Identifiers', ('identifiers', 'other_names')),
        ('Common Fields', ('updated_at', 'created_at', 'sources')),
    ),
}
