"""
    Schema for disclosure objects.
"""
import copy

from .common import sources, extras, identifiers, contact_details,\
    fuzzy_datetime_blank, documents

from opencivicdata import common

fuzzy_datetime = copy.deepcopy(fuzzy_datetime_blank)
fuzzy_datetime["blank"] = False

reporting_period_schema = {
    "properties": {
        'start_date': fuzzy_datetime_blank,
        'end_date': fuzzy_datetime_blank,
        "timezone": {
            "type": "string"
        },
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


disclosure_schema = {
    "properties": {
        "classification": {
            "type": ["string", "null"],
            "enum": common.DISCLOSURE_CLASSIFICATIONS,
        },
        "identifiers": identifiers,
        "contact_details": contact_details,
        "related_entities": {
            "items": {
                "properties": {
                    "entity_type": {
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
        "submitted_date": {
            "type": "datetime"
        },
        "effective_date": {
            "type": "datetime"
        },
        "timezone": {
            "type": "string"
        },
        "source_identified": {
            "type": "boolean",
        },
        "documents": documents,
        "sources": sources,
        "extras": extras
    },
    "type": "object"
}
