from .common import (links, contact_details, identifiers, other_names, sources, extras,
                     fuzzy_date_blank)

schema = {
    "properties": {
        "name": { "type": "string" },
        "other_names": other_names,
        "identifiers": identifiers,
        "sort_name": { "type": "string", "blank": True },
        "gender": { "type": "string", "blank": True },
        "birth_date": fuzzy_date_blank,
        "death_date": fuzzy_date_blank,
        "image": { "format": "uri", "type": "string", "blank": True },
        "summary": { "type": "string", "blank": True },
        "biography": { "type": "string", "blank": True },
        "national_identity": { "type": "string", "blank": True },
        "contact_details": contact_details,
        "links": links,
        "source_identified": { "type": ["null", "boolean"] },
        "sources": sources,
        "extras": extras,
    },
    "type": "object"
}
