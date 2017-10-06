from .common import extras, fuzzy_date_blank

schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string", "minLength": 1},
        "url": {"type": "string", "minLength": 1},
        "classification": {"type": "string", "minLength": 1},   # TODO: enum
        "division_id": {"type": "string", "minLength": 1},
        "legislative_sessions": {
            "type": "array", "items": {"type": "object", "properties": {
                "name": {"type": "string", "minLength": 1},
                "type": {"type": "string", "enum": ["primary", "special"]},
                "start_date": fuzzy_date_blank,
                "end_date": fuzzy_date_blank,
            }},
        },
        "feature_flags": {"type": "array", "items": {"type": "string", "minLength": 1}},
        "extras": extras,
    }
}
