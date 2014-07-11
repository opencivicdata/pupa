"""
    Schema for event objects.
"""

from .common import sources, extras, fuzzy_date_blank

media_schema = {
    "items": {
        "properties": {
            "name": { "type": "string" },
            "type": { "type": "string" },
            "date": fuzzy_date_blank,
            "offset": { "type": ["number", "null"] },
            "links": {
                "items": {
                    "properties": {
                        "media_type": { "type": "string", "blank": True },
                        "url": { "type": "string" },
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
        "name": { "type": "string" },
        "start_time": { "type": "datetime", },
        "timezone": { "type": "string" },
        "all_day": { "type": "boolean" },
        "end_time": { "type": ["datetime", "null"] },
        "status": {
            "type": "string", "blank": True,
            "enum": ["cancelled", "tentative", "confirmed", "passed"],
        },
        "classification": { "type": "string" }, # TODO: enum
        "description": { "type": "string", "blank": True, },

        "location": {
            "type": "object",
            "properties": {

                "name": { "type": "string", },

                "note": {
                    "type": "string", "blank": True,
                },

                "url": {
                    "required": False,
                    "type": "string",
                },

                "coordinates": {
                    "type": ["object", "null"],
                    "properties": {
                        "latitude": {
                            "type": "string",
                        },

                        "longitude": {
                            "type": "string",
                        }
                    }
                },
            },
        },

        "media": media_schema,

        "documents": {
            "items": {
                "properties": {
                    "note": { "type": "string", },
                    "url": { "type": "string", },
                    "media_type": { "type": "string", },
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
                        "blank": True,
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
                    },

                    "id": {
                        "type": ["string", "null"],
                    },

                    "type": {
                        "enum": ["organization", "person"],
                        "type": "string",
                    },

                    "note": {
                        "type": "string",
                    },

                },
                "type": "object"
            },
            "type": "array"
        },

        "agenda": {
            "items": {
                "properties": {
                    "description": { "type": "string", },

                    "order": {
                        "type": ["string", "null"],
                    },

                    "subjects": {
                        "items": {"type": "string"},
                        "type": "array"
                    },

                    "media": media_schema,

                    "notes": {
                        "items": {
                            "type": "string",
                        },
                        "type": "array",
                        "minItems": 0,
                    },

                    "related_entities": {
                        "items": {
                            "properties": {
                                "type": {
                                    "type": "string",
                                },

                                "id": {
                                    "type": ["string", "null"],
                                },

                                "name": {
                                    "type": "string",
                                },

                                "note": {
                                    "type": ["string", "null"],
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
    },
    "type": "object"
}
