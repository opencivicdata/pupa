from opencivicdata import common

contact_details = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "type": {"type": "string", "enum": common.CONTACT_TYPES},
            "value": {"type": "string"},
            "note": {"type": "string", "blank": True},
            "label": {"type": "string", "blank": True},
        }
    }
}

identifiers = {
    "items": {
        "properties": {
            "identifier": {"type": "string" },
            "scheme": {"type": "string", "blank": True},
        }
    },
    "type": "array",
}

fuzzy_date_string = {"type": "string", 
                     "pattern": "(^[0-9]{4})?(-[0-9]{2}){0,2}$"}
fuzzy_date_string_blank = {"type": "string", 
                           "pattern": "(^[0-9]{4})?(-[0-9]{2}){0,2}$", 
                           "blank": True}
fuzzy_datetime_string_blank = {"type": "string",
                               "pattern": "(^[0-9]{4})?(-[0-9]{2}){0,2}( [0-9]{2}:[0-9]{2}:[0-9]{2})?$",
                               "blank": True}

fuzzy_date = {"type": [fuzzy_date_string, "datetime"]}
fuzzy_date_blank = {"type": [fuzzy_date_string_blank, "datetime"], 
                    "blank": True}
fuzzy_datetime = {"type": [fuzzy_datetime_string_blank, "datetime"]}
fuzzy_datetime_blank = {"type": [fuzzy_datetime_string_blank, "datetime"], 
                        "blank": True}

other_names = {
    "items": {
        "properties": {
            "name": {"type": "string"},
            "start_date": fuzzy_date_blank,
            "end_date": fuzzy_date_blank,
            "note": {"type": "string", "blank": True }
            },
        "type": "object"
    },
    "type": "array"
}


links = {
    "items": {
        "properties": {
            "note": { "type": "string", "blank": True },
            "url": { "format": "uri", "type": "string" }
        },
        "type": "object"
    },
    "type": "array"
}


sources = {
    "items": {
        "properties": {
            "url": { "type": "string" },
            "note": { "type": "string", "blank": True }
        },
        "type": "object"
    },
    "minItems": 1,
    "type": "array"
}

extras = {
    "type": "object",
}
