"""
    Schema for disclosure objects.
"""
import copy

from .common import sources, extras, identifiers, contact_details,\
    fuzzy_datetime_blank, documents

fuzzy_datetime = copy.deepcopy(fuzzy_datetime_blank)
fuzzy_datetime["blank"] = False

reporting_period_schema = {
    "properties": {
        'start_date': fuzzy_datetime_blank,
        'end_date': fuzzy_datetime_blank,
        'period_type': {
            'type': 'string'
        },
        'description': {
            'type': 'string'
        },
        'authorities': {
            'type': 'array',
            "items": {
                "properties": {
                    "entity_type": {
                        "type": "string"
                    },
                    "jurisdiction": {
                        "type": "string"
                    },
                    "id": {
                        "type": "string"
                    },
                    "name": {
                        "type": "string"
                    }
                },
                "type": "object",
            }
        }
    },
    "type": "object"
}

disclosed_event_schema = {
    "properties": {
        "entity_type": {
            "type": "string"
        },
        "id": {
            "type": "string"
        },
        "name": {
            "type": "string"
        },
        "note": {
            "type": ["string", "null"],
            "blank": True
        }
    },
    "type": "object"
}


disclosure_schema = {
    "properties": {
        "identifiers": identifiers,
        "contact_details": contact_details,
        "registrant": {
            "type": "string"
        },
        "registrant_id": {
            "type": "string"
        },
        "authority": {
            "type": "string"
        },
        "authority_id": {
            "type": "string"
        },
        "related_entities": {
            "items": {
                "properties": {
                    "entity_type": {
                        "type": "string"
                    },
                    "id": {
                        "type": "string"
                    },
                    "name": {
                        "type": "string"
                    },
                    "note": {
                        "type": ["string", "null"],
                    },
                },
                "type": "object"
            },
            "type": "array"
        },
        "disclosed_events": {
            "items": disclosed_event_schema,
            "type": "array"
        },
        "submitted_date": {
            "type": fuzzy_datetime
        },
        "effective_date": {
            "type": fuzzy_datetime
        },
        "documents": documents, 
        "sources": sources,
        "extras": extras
    },
    "type": "object"
}
