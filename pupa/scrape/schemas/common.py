from opencivicdata import common

contact_details = {
    "description": "Contact information for this entity.",
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "type": {"type": "string",
                     "enum": common.CONTACT_TYPES,
                     "description": "type of contact (e.g. phone, email, address)"},
            "value": {"type": "string",
                      "description": "actual phone number/email address/etc.", },
            "note": {"type": "string", "blank": True,
                     "description": "for grouping data by location/etc.", },
            "label": {"type": "string", "blank": True,
                      "description": "human readable label", },
        }
    }
}

identifiers = {
    "items": {
        "properties": {
            "identifier": {"type": "string",
                           "description": "The 3rd-party identifier, such as OKL0001000."},
            "scheme": {"type": "string", "blank": True,
                       "description": "What service this identifier is used by."},
        }
    },
    "type": "array",
    "description": "IDs other than the primary ID that the object may be known by."
}

other_names = {
    "description": "Alternate or former names for this object.",
    "items": {
        "properties": {
            "name": {"type": "string",
                     "description": "An alternate name this object is sometimes known by."},
            "start_date": {
                "type": "string",
                "pattern": "(^[0-9]{4})?(-[0-9]{2}){0,2}$",
                "description": ("The date at which this name became valid."
                                "(null if unknown/valid indefinitely)"),
            },
            "end_date": {
                "type": "string",
                "pattern": "(^[0-9]{4})?(-[0-9]{2}){0,2}$",
                "description": ("The date at which this name was no longer valid. "
                                "(null if still valid/valid indefinitely)"),
            },
            "note": {"type": "string", "blank": True,
                     "description": ("An optional note describing where this alternate name came "
                                     "from or its relationship to the entity."), }
        },
        "type": "object",
    },
    "type": "array"
}


links = {
    "description": "URLs for documents about the person",
    "items": {
        "properties": {
            "note": {
                "description": "A note, e.g. 'Wikipedia page'",
                "type": "string", "blank": True,
            },
            "url": {
                "description": "A URL for a document about the person",
                "format": "uri",
                "type": "string"
            }
        },
        "type": "object"
    },
    "type": "array"
}


sources = {
    "description": "URLs for sources relating to the object",
    "items": {
        "properties": {
            "url": {
                "type": "string",
                "description": "URL of resource used to collect information",
            },
            "note": {
                "type": "string", "blank": True,
                "description": "note about what information this URL was used for",
            }
        },
        "type": "object"
    },
    "minItems": 1,
    "type": "array"
}

extras = {
    "description": "extra data outside the core schema",
    "type": "object",
}
