contact_details = {
    "description": "Details regarding how to contact this person.",
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "type": {"type": "string"},
            "value": {"type": "string"},
            # note for grouping contact details by location, etc.
            "note": {"type": ["string", "null"], },
            # human readable label
            "label": {"type": ["string", "null"], },
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
    "description": "Alternate or former names",
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


# **sources** - like all objects, sources is an array of one
# or more source object.  Each source object has the following
# properties:
#
# * **url** - URL to resource used to collect
# * **note** - Note about what this URL was used to collect.
sources = {
    "description": "URLs for sources relating to the object",
    "items": {
        "properties": {
            "url": {
                "type": "string"
            },
            "note": {
                "type": ["null", "string"],
            }
        },
        "type": "object"
    },
    "minItems": 1,
    "type": "array"
}
