"""
    Schema for bill objects.
"""

from .common import sources, extras, fuzzy_date_blank, fuzzy_date
from opencivicdata import common

versions_or_documents = {
    "items": {
        "properties": {
            "note": {"type": "string"},
            "date": fuzzy_date_blank,
            "links": {
                "items": {
                    "properties": {
                        "media_type": {"type": "string", "blank": True },
                        "url": {"type": "string", "format": "uri"}
                    },
                    "type": "object"
                },
                "type": "array",
            },
        },
        "type": "object"
    },
    "type": "array",
}

schema = {
    "type": "object",
    "properties": {
        "legislative_session": {"type": "string"},
        "identifier": {"type": "string"},
        "title": {"type": "string"},
        "from_organization": { "type": ["string", "null"] },
        "classification": {"items": {"type": "string", "enum": common.BILL_CLASSIFICATIONS},
                           "type": "array"},
        "subject": { "items": {"type": "string"}, "type": "array"},
        "abstracts": {
            "items": {
                "properties": {
                    "abstract": {"type": "string"},
                    "note": {"type": ["string", "null"]},
                },
                "type": "object"},
            "type": "array",
        },
        "other_titles": {
            "items": {
                "properties": {
                    "title": {"type": "string"},
                    "note": {"type": ["string", "null"]},
                },
                "type": "object"
            },
            "type": "array",
        },
        "other_identifiers": {
            "items": {
                "properties": {
                    "identifier": {"type": "string"},
                    "note": {"type": "string", "blank": True},
                    "scheme": {"type": "string", "blank": True},
                },
                "type": "object"
            },
            "type": "array",
        },
        "actions": {
            "items": {
                "properties": {
                    "organization": { "type": ["string", "null"] },
                    "date": fuzzy_date,
                    "description": { "type": "string" },
                    "classification": {"items": {"type": "string",
                                                  "enum": common.BILL_ACTION_CLASSIFICATIONS },
                                       "type": "array",
                                      },
                    "related_entities": {
                        "items": {
                            "properties": {
                                "name": {"type": "string"},
                                "entity_type": {
                                    "enum": ["organization", "person", ""],
                                    "type": "string", "blank": True,
                                },
                                "id": {"type": ["string", "null"]}
                                # TODO^^should this be person_id or organization_id
                            },
                            "type": "object"
                        },
                        "type": "array",
                    },
                },
                "type": "object"
            },
            "type": "array",
        },

        "sponsorships": {
            "items": {
                "properties": {
                    "primary": { "type": "boolean" },
                    "classification": { "type": "string", },
                    "name": {"type": "string" },
                    "entity_type": {
                        "enum": ["organization", "person", ""],
                        "type": "string", "blank": True,
                    },
                    "id": {"type": ["string", "null"] },
                    # ^^^TODO: check this one too
                },
                "type": "object"
            },
            "type": "array",
        },

        "related_bills": {
            "items": {
                "properties": {
                    "identifier": {"type": "string"},
                    "legislative_session": {"type": "string"},
                    "relation_type": {"enum": common.BILL_RELATION_TYPES, "type": "string"},
                },
                "type": "object"
            },
            "type": "array",
        },

        "versions": versions_or_documents,
        "documents": versions_or_documents,
        "sources": sources,
        "extras": extras,
    }
}
