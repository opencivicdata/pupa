schema = {
    "description": "Information about a jurisdiction, including session, term, etc. details.",
    "type": "object",
    "properties": {
        "name": {"type": "string",
                 "description": "Name of jurisdiction (e.g. North Carolina General Assembly)"},
        "url": {"type": "string"},
        "chambers": {
             "additionalProperties": {
                 "properties": {
                     "name": { "type": "string" },
                     "title": { "type": "string" }
                 },
                 "type": "object"
             },
             "type": "object"
        },
        "terms": { "type": "array", "minItems": 1, "items":
          {"type":"object", "properties": {
            "name": {"type": "string"},
            "start_year": {"type": "integer", "minimum": 1000, "maximum": 2020},
            "end_year": {"type": "integer", "minimum": 1000, "maximum": 2030},
            "sessions": {"type": "array", "minItems": 1, "items": {"type": "string"}}
          }}},
        "session_details": { "type": "object",
          "additionalProperties": { "type": "object",
            "properties": {
              "type": {"type": "string" },
              "start_date": {"type": ["datetime", "null"] },
              "end_date": {"type": ["datetime", "null"] }
            }
          }
        },
        "feature_flags": { "type": "array", "items": {"type": "string"}},
        "capitol_maps": { "type": "array", "items":
           {"type":"object", "properties": {
            "name": {"type": "string"}, "url": {"type": "string"}
            }
           }
         }
    }
}
