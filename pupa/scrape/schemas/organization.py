from .common import links, contact_details, identifiers, other_names, sources, extras
from pupa import settings

schema = {
    "properties": {
        "jurisdiction_id": {
            "description": "The ID of the Jurisdiction to which this org belongs",
            "type": ["string"],
        },
        "classification": {
            "description": "An organization category, e.g. committee",
            "type": ["string", "null"],
            "enum": settings.ORGANIZATION_CLASSIFICATIONS,
        },
        "division_id": {
            "description": "Linked geospatial ID in OCD division ID format",
            "type": ["string", "null"],
        },
        "dissolution_date": {
            "description": "A date of dissolution",
            "pattern": "^([0-9]{4})?(-[0-9]{2}){0,2}$",
            "type": ["string"],
            "blank": True,
        },
        "founding_date": {
            "description": "A date of founding",
            "pattern": "^([0-9]{4})?(-[0-9]{2}){0,2}$",
            "type": ["string"],
            "blank": True,
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
            "type": "string",
            "blank": True,
        },
        'chamber': {
            "enum": ["upper", "lower", ""], "type": ["string"], "blank": True,
            "description": ("chamber (if legislature is bicameral, otherwise null)"),
        },
        "sources": sources,
        "extras": extras,
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
