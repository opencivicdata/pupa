from .common import links, contact_details, extras, fuzzy_date_blank

schema = {
    "properties": {
        "label": { "type": "string" },
        "role": { "type": "string", "blank": True },
        "organization_id": { "type": "string" },
        "start_date": fuzzy_date_blank,
        "end_date": fuzzy_date_blank,
        "contact_details": contact_details,
        "links": links,
        "extras": extras,
    },
    "type": "object"
}
