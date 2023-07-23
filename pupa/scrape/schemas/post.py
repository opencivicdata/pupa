from .common import links, contact_details, extras, fuzzy_date_blank

schema = {
    "properties": {
        "label": {"type": "string", "minLength": 1},
        "role": {"type": "string"},
        "maximum_memberships": {"type": "number"},
        "organization_id": {"type": "string", "minLength": 1},
        "division_id": {"type": ["null", "string"], "minLength": 1},
        "start_date": fuzzy_date_blank,
        "end_date": fuzzy_date_blank,
        "contact_details": contact_details,
        "links": links,
        "extras": extras,
    },
    "type": "object",
}
