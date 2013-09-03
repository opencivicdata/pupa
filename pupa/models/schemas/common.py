contact_details = {
    "description": "Contact information for this entity.",
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "type": {"type": "string",
                     "description": "type of contact (e.g. phone, email, address)"},
            "value": {"type": "string",
                      "description": "actual phone number/email address/etc.",
                     },
            "note": {"type": ["string", "null"],
                     "description": "for grouping data by location/etc."
                    },
            "label": {"type": ["string", "null"],
                      "description": "human readable label",
                     },
        }
    }
}

identifiers = {
    "items": {
        "properties": {
            "identifier": {"type": "string"},
            "scheme": {"type": ["string", "null"]},
        }
    },
    "type": "array"
}

other_names = {
    "description": "Alternate or former names for this object.",
    "items": {
        "properties": {
            "name": {"type": "string"},
            "start_date": {
                "type": ["string", "null"],
                "pattern": "^[0-9]{4}(-[0-9]{2}){0,2}$"
            },
            "end_date": {
                "type": ["string", "null"],
                "pattern": "^[0-9]{4}(-[0-9]{2}){0,2}$"
            },
            "note": {"type": ["string", "null"]}
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
                "type": ["string", "null"],
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
                "type": ["null", "string"],
                "description": "note about what information this URL was used for",
            }
        },
        "type": "object"
    },
    "minItems": 1,
    "type": "array"
}
