schema = {
    "description": "API metadata response",
    "type": "object",
    "properties": {
        "name": {"type": "string",
                 "description": "Name of jurisdiction (e.g. North Carolina General Assembly)"},
        "url": {"type": "string"},
        "chambers": {
             "additionalProperties": {
                 "properties": {
                     "name": { "required": True, "type": "string" },
                     "title": { "required": True, "type": "string" }
                 },
                 "type": "object"
             },
             "required": False,
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
              "type": {"type": "string", "required": False},
              "start_date": {"type": "datetime", "required": False},
              "end_date": {"type": "datetime", "required": False}
            }
          }
        },
        "feature_flags": { "type": "array", "items": {"type": "string"}},
        "capitol_maps": { "type": "array", "required": False, "items":
           {"type":"object", "properties": {
            "name": {"type": "string"}, "url": {"type": "string"}
            }
           }
         }
    }
}
