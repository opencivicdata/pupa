from .common import sources, extras, fuzzy_datetime_blank
from opencivicdata import common


schema = {
    "type": "object",
    "properties": {
        'identifier': {"type": "string", "blank": True,},
        'motion_text': {"type": "string" },
        'motion_classification': {"items": {"type": "string", "enum": common.VOTE_CLASSIFICATIONS},
                                  "type": "array"},
        'start_date': fuzzy_datetime_blank,
        'end_date': fuzzy_datetime_blank,
        'result': {"type": "string", "enum": common.VOTE_RESULTS},
        'organization': {"type": ["string", "null"]},
        'legislative_session': {"type": "string"},
        'bill': {"type": ["string", "null"]},
        'votes': {
            "items": {
                "type": "object",
                "properties": {
                    "option": {"type": "string", "enum": common.VOTE_OPTIONS },
                    "voter": {"type": "string"},
                    "note": {"type": "string", "blank": True},
                },
            },
        },
        'counts': {
            "items": {
                "properties": {
                    "option": {"type": "string", "enum": common.VOTE_OPTIONS },
                    "value": {"type": "integer", "minimum": 0},
                },
                "type": "object"
            },
        },

        'sources': sources,
        'extras': extras,
    }
}
