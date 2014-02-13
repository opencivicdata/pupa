from .common import links, contact_details, identifiers, other_names, sources

schema = {
    "$schema": "http://json-schema.org/draft-03/schema#",
    "description": "A real person, alive or dead",
    "id": "http://popoloproject.com/schemas/person.json#",
    "_order": (
        ('Basics', ('name', 'image', 'contact_details', 'links')),
        ('Extended Details', ('gender', 'summary', 'biography', 'birth_date', 'death_date', 'sort_name')),
        ('Alternate Names/Identifiers', ('identifiers', 'other_names')),
        ('Common Fields', ('updated_at', 'created_at', 'sources')),
    ),
    "properties": {
        "updated_at": {
            "description": "The time at which the resource was last modified",
            "type": ["string", "datetime", "null"],
        },
        "created_at": {
            "description": "The time at which the resource was created",
            "type": ["string", "datetime", "null"],
        },
        "biography": {
            "description": "An extended account of a person's life",
            "type": ["string", "null"],
        },
        "birth_date": {
            "description": "A date of birth",
            "pattern": "^[0-9]{4}(-[0-9]{2}){0,2}$",
            "type": ["string", "null"],
        },
        "death_date": {
            "description": "A date of death",
            "pattern": "^[0-9]{4}(-[0-9]{2}){0,2}$",
            "type": ["string", "null"],
        },
        "gender": {
            "description": "A gender",
            "type": ["string", "null"],
        },
        "image": {
            "description": "A URL of a head shot",
            "format": "uri",
            "type": ["string", "null"],
        },
        "name": {
            "description": "A person's preferred full name",
            "type": "string",
        },
        "sort_name": {
            "description": "A name to use in a lexicographically ordered list",
            "type": "string",
        },
        "contact_details": contact_details,
        "other_names": other_names,
        "links": links,
        "identifiers": identifiers,
        "summary": {
            "description": "A one-line account of a person's life",
            "type": ["string", "null"],
        },
        "national_identity": {
            "description": "A national identity",
            "type": ["string", "null"],
        },
        "sources": sources,
    },
    "title": "Person",
    "type": "object"
}
