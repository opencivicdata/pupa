schema = {
    "description": "Information about a jurisdiction, including session, chamber, etc.",
    "type": "object",
    "_order": (
        ('Basic Details', ('name', 'url', 'sessions')),
        ('Additional Metadata', ('feature_flags', 'building_maps')),
    ),
    "properties": {
        "name": {"type": "string",
                 "description": "Name of jurisdiction (e.g. North Carolina General Assembly)"},
        "url": {"type": "string", "description": "URL pointing to jurisdiction's website.", },
        "sessions": {
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
        "building_maps": {
            "type": "array", "items": {"type": "object", "properties": {
                "name": {"type": "string", "description": "Name of map (e.g. Floor 1)"},
                "url": {"type": "string", "description": "URL to map image/PDF"}
            }},
            "description": ("Links to image/PDF maps of the building."), }
    }
}
