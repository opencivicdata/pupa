"""
    Schema for vote objects.
"""

from .common import sources, extras
from opencivicdata import common


schema = {
    "description": "schema for vote data (based on Popolo VoteEvent)",
    "type": "object",
    "_order": (
        ('Basic Fields', ["organization", "organization_id", "_type", "session",
                          "chamber", "date", "motion", "type", "passed"]),
        ('Common Fields', ['updated_at', 'created_at', 'sources', 'extras']),
        ('Relationship to Bill', ["bill"]),
        ('Vote Counts', ["vote_counts", "roll_call"])
    ),
    "properties": {
        'identifier': {"type": "string", "blank": True, "description": "An issued identifier"},

        'motion': {"type": "string",
                   "description": "description of motion (from upstream source)"},


        'start_date': {"pattern": "^[0-9]{4}(-[0-9]{2}){0,2}$", "type": "string",
                       "description": "date of the action"},
        'end_date': {"pattern": "^[0-9]{4}(-[0-9]{2}){0,2}$", "type": "string",
                     "description": "date of the action"},

        'counts': {
            "items": {
                "properties": {
                    "option": {"type": "string", "enum": common.VOTE_OPTIONS,
                               "description": "(e.g. yes, no, not-voting)"},
                    "value": {"type": "integer", "minimum": 0,
                              "description": "number of people voting this way"}
                },
                "type": "object"
            },
            "description": ("list of objects with vote_type and count properties"),
        },

        'votes': {
            "items": {
                "type": "object",
                "properties": {
                    "option": {"type": "string", "enum": common.VOTE_OPTIONS,
                               "description": "(e.g. yes, no, not-voting)"},
                    "voter": {"type": "string", "description": "name of voter"},
                    # TODO: can add the party, role, weight, pairing info
                },
            },
            "description": "list of individual legislator votes",
        },

        # added fields
        'classification': {"items": {"type": "string", "enum": common.VOTE_CLASSIFICATIONS},
                           "type": "array", "description": "array of types"},
        'outcome': {"type": "string", "enum": common.VOTE_OUTCOMES,
                    "description": "outcome of vote (e.g. pass, fail)"},
        'organization': {"type": ["string", "null"],
                         "description": "name of the voting organization"},
        'bill': {"type": ["string", "null"],
                 "description": "related bill (optional)"},
        'session': {"type": "string",
                    "description": "Associated with one of the jurisdiction's sessions"},


        # common fields
        'updated_at': {"type": ["string", "datetime"], "required": False,
                       "description": "the time that the object was last updated"},

        'created_at': {"type": ["string", "datetime"], "required": False,
                       "description": "the time that this object was first created"},

        'sources': sources,
        'extras': extras,
    }
}
