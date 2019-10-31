"""
    Schema for event objects.
"""

from .common import sources, extras, fuzzy_date_blank, fuzzy_datetime, fuzzy_datetime_blank

media_schema = {
    "items": {
        "properties": {
            "name": {"type": "string", "minLength": 1},
            "type": {"type": "string", "minLength": 1},
            "date": fuzzy_date_blank,
            "offset": {"type": ["number", "null"]},
            "links": {
                "items": {
                    "properties": {
                        "media_type": {"type": "string"},
                        "url": {"type": "string", "format": "uri"},
                    },
                    "type": "object"
                },
                "type": "array"
            },
        },
        "type": "object"
    },
    "type": "array"
}

schema = {
    "properties": {
        "name": {"type": "string", "minLength": 1},
        "all_day": {"type": "boolean"},
        'start_date': fuzzy_datetime,
        'end_date': fuzzy_datetime_blank,
        "status": {
            "type": "string",
            "enum": ["cancelled", "tentative", "confirmed", "passed"],
        },
        "classification": {"type": "string", "minLength": 1},    # TODO: enum
        "description": {"type": "string"},

        "location": {
            "type": "object",
            "properties": {

                "name": {"type": "string", "minLength": 1},

                "note": {
                    "type": "string",
                },

                "url": {
                    "type": ["string", "null"],
                    "format": "uri",
                },

                "coordinates": {
                    "type": ["object", "null"],
                    "properties": {
                        "latitude": {
                            "type": "string",
                            "minLength": 1,
                        },
                        "longitude": {
                            "type": "string",
                            "minLength": 1,
                        }
                    }
                },
            },
        },

        "media": media_schema,

        "documents": {
            "items": {
                "properties": {
                    "note": {"type": "string", "minLength": 1},
                    "url": {"type": "string", "minLength": 1},
                    "media_type": {"type": "string", "minLength": 1},
                    "date": fuzzy_date_blank,
                },
                "type": "object"
            },
            "type": "array"
        },

        "links": {
            "items": {
                "properties": {
                    "note": {
                        "type": "string",
                    },
                    "url": {
                        "format": "uri",
                        "type": "string"
                    }
                },
                "type": "object"
            },
            "type": "array"
        },

        "participants": {
            "items": {
                "properties": {

                    "name": {
                        "type": "string",
                        "minLength": 1,
                    },

                    "type": {
                        "enum": ["organization", "person"],
                        "type": "string",
                    },

                    "note": {
                        "type": "string",
                        "minLength": 1,
                    },

                },
                "type": "object"
            },
            "type": "array"
        },

        "agenda": {
            "items": {
                "properties": {
                    "description": {"type": "string", "minLength": 1},

                    "classification": {
                        "items": {"type": "string", "minLength": 1},
                        "type": "array",
                    },

                    "order": {
                        "type": ["string", "null"],
                    },

                    "subjects": {
                        "items": {"type": "string", "minLength": 1},
                        "type": "array"
                    },

                    "media": media_schema,

                    "notes": {
                        "items": {
                            "type": "string",
                            "minLength": 1,
                        },
                        "type": "array",
                    },

                    "related_entities": {
                        "items": {
                            "properties": {
                                "entity_type": {
                                    "type": "string",
                                    "minLength": 1,
                                },

                                "name": {
                                    "type": "string",
                                    "minLength": 1,
                                },

                                "note": {
                                    "type": ["string", "null", ],
                                    "minLength": 1,
                                },
                            },
                            "type": "object",
                        },
                        "minItems": 0,
                        "type": "array",
                    },
                },
                "type": "object"
            },
            "minItems": 0,
            "type": "array"
        },
        "sources": sources,
        "extras": extras,
        'pupa_id': {"type": ["string", "null"],
                    "minLength": 1,
                    },
    },
    "type": "object"
}
