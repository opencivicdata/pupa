from .common import links, contact_details, identifiers, other_names, sources

CLASSIFICATIONS = ['legislature', 'party', 'committee', 'commission']

schema = {
    "properties": {
        "classification": {
            "description": "The type of organization represented by this entity.",
            "type": ["string", "null"],
            "enum": CLASSIFICATIONS,
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

        'updated_at': {"type": ["string", "datetime"], "required": False,
                    "description": "the time that the object was last updated",
                   },
        'created_at': {"type": ["string", "datetime"], "required": False,
                    "description": "the time that this object was first created" },

        "identifiers": identifiers,
        "other_names": other_names,
        "contact_details": contact_details,
        "links": links,

        "name": {
            "description": "A primary name, e.g. a legally recognized name",
            "type": "string"
        },
        "parent_id": {
            "description": "Open Civic Data ID of organization that contains this organization.",
            "type": ["string", "null"],
        },
        "posts": {
            "description": ("Positions that exist independently of the person holding them. "
                            "(such as chairman or minority whip)"),
            "items": {
                "properties": {
                    "contact_details": contact_details,
                    "links": links,
                    "id": {
                        "description": "The post's unique identifier",
                        "type": ["string", "null"],
                    },
                    "label": {
                        "description": "A label describing the post.",
                        "type": "string"
                    },
                    "organization_id": {
                        "description": "The ID of the organization in which the post is held",
                        "type": ["string", "null"],
                    },
                    "role": {
                        "description": "The role that the holder of the post fulfills",
                        "type": ["string", "null"],
                    },
                    "start_date": {
                        "description": "Startting date of the post.",
                        "pattern": "^[0-9]{4}(-[0-9]{2}){0,2}$",
                        "type": ["string", "null"],
                    },
                    "end_date": {
                        "description": "Ending date of the post.",
                        "pattern": "^[0-9]{4}(-[0-9]{2}){0,2}$",
                        "type": ["string", "null"],
                    },
                },
                "title": "Post",
                "type": "object"
            },
            "type": "array"
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
