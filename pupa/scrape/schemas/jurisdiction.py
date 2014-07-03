from .common import extras, fuzzy_date_blank
from opencivicdata import common


schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "url": {"type": "string"},
        "classification": {"type": "string"},   # TODO: enum
        "division_id": {"type": "string"},
        "legislative_sessions": {
            "type": "array", "items": {"type": "object", "properties": {
                "name": {"type": "string"},
                "name": {"type": "string"},
                "type": {"classification": "string", "enum": ["primary", "special"]},
                "start_date": fuzzy_date_blank,
                "end_date": fuzzy_date_blank,
            }},
        },
        "feature_flags": { "type": "array", "items": {"type": "string"} },
        "extras": extras,
    }
}
