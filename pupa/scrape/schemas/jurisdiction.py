from .common import extras
from opencivicdata import common


schema = {
    "description": "Information about a jurisdiction, including session, chamber, etc.",
    "type": "object",
    "properties": {
        "classification": {"type": "string",
                 "description": "Jurisidction's type (e.g. government or school board)"},
        "name": {"type": "string",
                 "description": "Name of jurisdiction (e.g. North Carolina General Assembly)"},
        "url": {"type": "string", "description": "URL pointing to jurisdiction's website.", },
        "legislative_sessions": {
            "type": "array", "items": {"type": "object", "properties": {
                "name": {"type": "string", "description": "Name of session."},
                "type": {"type": "string", "required": False,
                         "description": "Type of session: primary or special."},
                "start_date": {"type": ["datetime"], "required": False,
                               "description": "Start date of session."},
                "end_date": {"type": ["datetime"], "required": False,
                             "description": "End date of session."}
            }},
            "description": ("List of sessions. Elements "
                            "consist of several fields giving detail about the session.")
        },
        "jurisdiction_id": {
            "description": "ID of the jurisdiction",
            "type": ["string"],
        },
        "jurisdiction_id": {
            "description": "ID of the jurisdiction",
            "type": "string",
            "enum": common.JURISDICTION_CLASSIFICATIONS,
        },
        "division_id": {
            "description": "Linked geospatial ID in OCD division ID format",
            "type": ["string", "null"],
        },
        "feature_flags": {
            "type": "array",
            "items": {"type": "string"},
            "description": ("A way to mark certain features as available on a per-jurisdiction "
                            "basis."),
        },
        "extras": extras,
    }
}
