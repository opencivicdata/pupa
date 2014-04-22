from .common import links, contact_details, identifiers, other_names, sources, extras

schema = {
    "$schema": "http://json-schema.org/draft-03/schema#",
    "description": "A real person, alive or dead",
    "id": "http://popoloproject.com/schemas/person.json#",
    "_order": (
        ('Basics', ('name', 'image', 'contact_details', 'links')),
        ('Extended Details', ('gender', 'summary', 'biography', 'birth_date', 'death_date')),
        ('Alternate Names/Identifiers', ('identifiers', 'other_names')),
        ('Common Fields', ('updated_at', 'created_at', 'sources', 'extras')),
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
            "type": "string",
            "blank": True,
        },
        "birth_date": {
            "description": "A date of birth",
            "pattern": "^([0-9]{4})?(-[0-9]{2}){0,2}$",
            "type": "string",
            "blank": True,
        },
        "death_date": {
            "description": "A date of death",
            "pattern": "^([0-9]{4})?(-[0-9]{2}){0,2}$",
            "type": "string",
            "blank": True,
        },
        "gender": {
            "description": "A gender",
            "type": "string",
            "blank": True,
        },
        "image": {
            "description": "A URL of a head shot",
            "format": "uri",
            "type": "string",
            "blank": True,
        },
        "name": {
            "description": "A person's preferred full name",
            "type": "string",
        },
        "contact_details": contact_details,
        "other_names": other_names,
        "links": links,
        "identifiers": identifiers,
        "summary": {
            "description": "A one-line account of a person's life",
            "type": "string",
            "blank": True,
        },
        "national_identity": {
            "description": "A national identity",
            "type": "string",
            "blank": True,
        },
        "sources": sources,
        "extras": extras,
    },
    "title": "Person",
    "type": "object"
}
