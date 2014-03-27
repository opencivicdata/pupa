from .common import links, contact_details

schema = {
    "$schema": "http://json-schema.org/draft-03/schema#",
    "description": "A relationship between a person and an organization",
    "id": "http://popoloproject.com/schemas/membership.json#",
    "properties": {
        "updated_at": {
            "description": "The time at which the resource was last modified",
            "type": ["string", "datetime", "null"],
        },
        "created_at": {
            "description": "The time at which the resource was created",
            "type": ["string", "datetime", "null"],
        },

        "organization_id": {
            "description": "The ID of the organization that is a party to the relationship",
            "type": "string",
        },
        # The membership's person may only be linked at import time, but objects
        # are validated at scrape time; therefore, the person_id is allowed to
        # have a type of "null" at scrape time.
        "person_id": {
            "description": "The ID of the person who is a party to the relationship",
            "type": ["string", "null"],
        },
        "post_id": {
            "description": ("The ID of the post held by the person in the organization "
                            "through this membership"),
            "type": ["string", "null"],
        },
        "on_behalf_of_id": {
            "description": ("The ID of the organization on whose behalf the person "
                            "is a party to the relationship"),
            "type": ["string", "null"],
        },
        "label": {
            "description": "A label describing the membership",
            "type": ["string", "null"],
        },
        "role": {
            "description": "The role that the person fulfills in the organization",
            "type": ["string", "null"],
        },
        "start_date": {
            "description": "The date on which the relationship began",
            "pattern": "^[0-9]{4}(-[0-9]{2}){0,2}$",
            "type": ["string", "null"],
        },
        "end_date": {
            "description": "The date on which the relationship ended",
            "pattern": "^[0-9]{4}(-[0-9]{2}){0,2}$",
            "type": ["string", "null"],
        },
        "contact_details": contact_details,
        "links": links,
    },
    "title": "Membership",
    "type": "object"
}
