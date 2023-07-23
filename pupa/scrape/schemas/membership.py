from .common import links, contact_details, extras, fuzzy_date_blank

schema = {
    "properties": {
        "label": {"type": "string"},
        "role": {"type": "string"},
        "person_id": {"type": ["string", "null"]},
        "person_name": {"type": ["string"], "minLength": 1},
        "organization_id": {"type": "string", "minLength": 1},
        "post_id": {"type": ["string", "null"]},
        "on_behalf_of_id": {"type": ["string", "null"]},
        "start_date": fuzzy_date_blank,
        "end_date": fuzzy_date_blank,
        "contact_details": contact_details,
        "links": links,
        "extras": extras,
        # division & jurisdiction are additions to popolo
        "division_id": {"type": ["string", "null"]},
        "jurisdiction_id": {"type": "string", "minLength": 1},
    },
    "type": "object",
}
