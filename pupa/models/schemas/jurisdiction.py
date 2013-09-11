schema = {
    "description": "Information about a jurisdiction, including session, term, etc. details.",
    "type": "object",
    "_order": (
        ('Basic Details', ('name', 'url', 'chambers', 'terms', 'session_details')),
        ('Additional Metadata', ('feature_flags', 'building_maps')),
    ),
    "properties": {
        "name": {"type": "string",
                 "description": "Name of jurisdiction (e.g. North Carolina General Assembly)"},
        "url": {"type": "string",
                "description": "URL pointing to jurisdiction's website."
               },
        "chambers": {
            "additionalProperties": {
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Human-readable name of chamber (e.g. Senate)"
                    },
                    "title": {
                        "type": "string",
                        "description": "Title of an individual in this chamber (e.g. Senator)"
                    }
                },
                "type": "object"
            },
            "type": "object",
            "description": ("Dictionary where keys are slugs for chambers (e.g. upper, lower) "
                            " and values describe the chamber in human-readable terms. "
                            " (only needs to be specified if there are multiple chambers)")

        },
        "terms": {
            "type": "array", "minItems": 1, "items": { "type":"object", "properties": {
                "name": {
                    "type": "string",
                    "description": ("Name of term, typically a year span (e.g. 2011-2012)")
                },
                "start_year": {
                    "type": "integer", "minimum": 1000, "maximum": 2020,
                    "description": "Year that term started.",
                },
                "end_year": {
                    "type": "integer", "minimum": 1000, "maximum": 2030,
                    "description": "Year that term ended."
                },
                "sessions": {
                    "type": "array", "minItems": 1, "items": {"type": "string"},
                    "description": ("List of sessions within this term. "
                                    "Each session must also appear in session_details"),
                }
            }},
            "description": "List of all terms, in chronological order.",
        },
        "session_details": {
            "type": "object",
            "additionalProperties": { "type": "object",
            "properties": {
              "type": {"type": "string", "required": False,
                       "description": "Type of session: primary or special." },
              "start_date": {"type": ["datetime"], "required": False,
                             "description": "Start date of session."
                            },
              "end_date": {"type": ["datetime"], "required": False,
                           "description": "End date of session."
                          }
            } },
            "description": ("Dictionary describing sessions, each key is a session slug that "
                            "must also appear in one ``sessions`` list in ``terms``.  Values "
                            "consist of several fields giving more detail about the session.")
        },
        "feature_flags": {
            "type": "array",
            "items": {"type": "string"},
            "description": ("A way to mark certain features as available on a per-jurisdiction "
                            "basis."),
        },
        "building_maps": {
            "type": "array", "items": {"type":"object", "properties": {
                "name": {"type": "string", "description": "Name of map (e.g. Floor 1)"},
                "url": {"type": "string", "description": "URL to map image/PDF"}
            } },
            "description": ("Links to image/PDF maps of the building."),
         }
    }
}
