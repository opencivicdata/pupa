from .common import links, contact_details, identifiers, other_names, sources

CLASSIFICATIONS = ['legislature', 'party', 'committee']

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

        # **updated_at** - the time that this object was last updated.
        "updated_at": {"type": ["string", "datetime"], "required": False},
        # **created_at** - the time that this object was first created.
        "created_at": {"type": ["string", "datetime"], "required": False},

        "identifiers": identifiers,
        "other_names": other_names,
        "contact_details": contact_details,
        "links": links,

        "name": {
            "description": "A primary name, e.g. a legally recognized name",
            "type": "string"
        },
        "parent_id": {
            "description": "An organization that contains this organization",
            "type": ["string", "null"],
        },
        "posts": {
            "description": "All posts.",
            "items": {
                "description": "A position that exists independent of the person holding it",
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
    "type": "object"
}
