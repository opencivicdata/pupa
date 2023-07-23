from .common import (
    links,
    contact_details,
    identifiers,
    other_names,
    sources,
    extras,
    fuzzy_date_blank,
)

schema = {
    "properties": {
        "name": {"type": "string", "minLength": 1},
        "other_names": other_names,
        "identifiers": identifiers,
        "sort_name": {"type": "string"},
        "family_name": {"type": "string"},
        "given_name": {"type": "string"},
        "gender": {"type": "string"},
        "birth_date": fuzzy_date_blank,
        "death_date": fuzzy_date_blank,
        "image": {"format": "uri-blank", "type": "string"},
        "summary": {"type": "string"},
        "biography": {"type": "string"},
        "national_identity": {"type": "string"},
        "contact_details": contact_details,
        "links": links,
        "sources": sources,
        "extras": extras,
    },
    "type": "object",
}
