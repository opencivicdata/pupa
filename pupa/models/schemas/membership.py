from .common import links, contact_details

schema = {
    "$schema": "http://json-schema.org/draft-03/schema#",
    "description": "A relationship between a person and an organization",
    "id": "http://popoloproject.com/schemas/membership.json#",
    "properties": {
        # **updated_at** - the time that this object was last updated.
        "updated_at": {"type": ["string", "datetime"], "required": False},
        # **created_at** - the time that this object was first created.
        "created_at": {"type": ["string", "datetime"], "required": False},

        "organization_id": {
            "description": "The ID of the organization that is a party to the relationship",
            "type": "string"
        },
        "person_id": {
            "description": "The ID of the person who is a party to the relationship",
            "type": ["string", "null"],
        },
        "post_id": {
            "description": "Post ID key.",
            "type": ["string", "null"],
        },
        "role": {
            "description": "The role that the holder of the post fulfills",
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
