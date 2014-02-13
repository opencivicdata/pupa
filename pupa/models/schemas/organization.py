from .common import links, contact_details, identifiers, other_names, sources

CLASSIFICATIONS = ['legislature', 'party', 'committee', 'commission']

schema = {
    "properties": {
        "classification": {
            "description": "An organization category, e.g. committee",
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
        "posts": {
            "description": "Posts within the organization",
            "items": {
                "properties": {
                    "contact_details": contact_details,
                    "links": links,
                    "id": {
                        "description": "The post's unique identifier",
                        "type": ["string", "null"],
                    },
                    "label": {
                        "description": "A label describing the post",
                        "type": "string"
                    },
                    "organization_id": {
                        "description": "The ID of the organization in which the post is held",
                        "type": ["string", "null"],
                    },
                    "role": {
                        "description": "The function that the holder of the post fulfills",
                        "type": ["string", "null"],
                    },
                    "start_date": {
                        "description": "The date on which the post was created",
                        "pattern": "^[0-9]{4}(-[0-9]{2}){0,2}$",
                        "type": ["string", "null"],
                    },
                    "end_date": {
                        "description": "The date on which the post was eliminated",
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
