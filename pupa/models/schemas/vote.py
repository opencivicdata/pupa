"""
    Schema for vote objects.
"""

from .common import sources


VOTE_TYPES = ['passage', 'amendment', 'reading:2', 'reading:3',
              'veto_override', 'other']
ROLLCALL_TYPES = ['yes', 'no', 'abstain', 'not-voting', 'other']


schema = {
    "description": "schema for vote data",
    "type": "object",
    "_order": (
        ('Basic Fields', ["organization", "organization_id", "_type", "session",
                          "chamber", "date", "motion", "type", "passed"]),
        ('Common Fields', ['updated_at', 'created_at', 'sources']),
        ('Relationship to Bill', ["bill"]),
        ('Vote Counts', ["vote_counts", "roll_call"])
    ),
    "properties": {

        'organization': {"type": ["string", "null"],
                      "description": "name of the voting organization"},

        'organization_id': {"type": ["string", "null"],
                         "description": "name of the voting organization"},

        '_type': {"enum": ["vote"], "type": "string",
               "description": "All vote objects must have a _type field set to vote." },

        'session': {"type": "string",
                 "description": "Associated with one of the jurisdiction's sessions"},

        'updated_at': {"type": ["string", "datetime"], "required": False,
                    "description": "the time that the object was last updated",
                   },

        'created_at': {"type": ["string", "datetime"], "required": False,
                    "description": "the time that this object was first created" },

        'chamber': {
            "enum": ["upper", "lower", "joint"], "type": ["string", "null"],
            "description": "chamber vote took place in (if legislature is bicameral, otherwise null)",
        },

        'date': {"pattern": "^[0-9]{4}(-[0-9]{2}){0,2}$", "type": "string",
              "description": "date of the action" },

        'motion': {"type": "string", "description": "description of motion (from upstream source)"},

        'type': {"items": {"type": "string", "enum": VOTE_TYPES}, "type": "array",
                 "description": "array of types" },

        'passed': {"type": "boolean", "description": "boolean indicating if vote passed"},

        'bill': {
            "type": ["object", "null"],
            "properties": {
                "id": {"type": ["string", "null"],
                       "description": ("bill's internal id if bill was matched with an object in "
                                       "the database")

                      },
                "name": {"type": "string", "description": "bill name (e.g. HB 21)"},
                "chamber": {
                    "enum": ["upper", "lower"], "type": ["string", "null"],
                    "description": "bill's chamber if vote was on a bill (and legislature is bicameral, otherwise null)"
                },
            },
            "description": ("Related bill, votes will have a non-null bill object if"
                            "they are related to a bill. Bills will have the following fields:"),
        },

        'vote_counts': {
            "items": {
                "properties": {
                    "vote_type": {"type": "string", "enum": ROLLCALL_TYPES,
                                  "description": "(e.g. yes, no, not-voting)"
                                 },
                    "count": {"type": "integer", "minimum": 0,
                              "description": "number of people voting this way",
                             }
                },
                "type": "object"
            },
            "description": ("list of objects with vote_type and count properties"),
        },

        'roll_call': {
            "items": {
                "type": "object",
                "properties": {
                    "vote_type": {"type": "string", "enum": ROLLCALL_TYPES,
                                  "description": "(e.g. yes, no, not-voting)"
                                 },

                    #     * **name** - person's name as provided by source
                    #     * **id** - person's internal id if they've been
                    #       matched to an entity in the database
                    "person": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "person's name as provided by the source"},
                            "id": {"type": ["string", "null"], "description": "person's internal id if they've been matched to an entity in the database"},
                        },
                        "description": "person object representing the voter",
                    }
                },
            },
            "description": "list of individual legislator votes",
        },

        'sources': sources,
    }
}
