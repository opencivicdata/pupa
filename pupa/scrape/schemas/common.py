from opencivicdata import common

contact_details = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "type": {"type": "string", "enum": common.CONTACT_TYPES},
            "value": {"type": "string", "minLength": 1},
            "note": {"type": "string"},
            "label": {"type": "string"},
        }
    }
}

identifiers = {
    "items": {
        "properties": {
            "identifier": {"type": "string", "minLength": 1},
            "scheme": {"type": "string"},
        }
    },
    "type": "array",
}

fuzzy_date_string = {"type": "string",
                     "pattern": "^[0-9]{4}(-[0-9]{2}){0,2}$"}
fuzzy_date_string_blank = {"type": "string",
                           "pattern": "^([0-9]{4})?(-[0-9]{2}){0,2}$",
                           }
fuzzy_datetime_string_blank = {"type": "string",
                               "pattern": ("^([0-9]{4}((-[0-9]{2}){0,2}|(-[0-9]{2}){2}T"
                                           "[0-9]{2}(:[0-9]{2}){0,2}"
                                           "(Z|[+-][0-9]{2}(:[0-9]{2})?))?)?$"),
                               }
fuzzy_date = {"type": [fuzzy_date_string, "date"]}
fuzzy_date_blank = {"type": [fuzzy_date_string_blank, "date"]}
fuzzy_datetime = {"type": [fuzzy_datetime_string_blank, "datetime"]}
fuzzy_datetime_blank = {"type": [fuzzy_datetime_string_blank, "datetime"]}

other_names = {
    "items": {
        "properties": {
            "name": {"type": "string", "minLength": 1},
            "start_date": fuzzy_date_blank,
            "end_date": fuzzy_date_blank,
            "note": {"type": "string"}
            },
        "type": "object"
    },
    "type": "array"
}


links = {
    "items": {
        "properties": {
            "note": {"type": "string"},
            "url": {"format": "uri", "type": "string"}
        },
        "type": "object"
    },
    "type": "array"
}


sources = {
    "items": {
        "properties": {
            "url": {"type": "string", "format": "uri"},
            "note": {"type": "string"},
        },
        "type": "object"
    },
    "minItems": 1,
    "type": "array"
}

extras = {
    "type": "object",
}
