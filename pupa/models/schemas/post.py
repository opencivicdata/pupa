from .common import links, contact_details

schema = {
    "$schema": "http://json-schema.org/draft-03/schema#",
    "id": "http://popoloproject.com/schemas/post.json#",
    "description": "A position that exists independent of the person holdint it",
    "properties": {
        "updated_at": {
            "description": "The time at which the resource was last modified",
            "type": ["string", "datetime", "null"],
        },
        "created_at": {
            "description": "The time at which the resource was created",
            "type": ["string", "datetime", "null"],
        },
        "label": {
            "description": "A label describing the post",
            "type": ["string", "null"],
        },
        "role": {
            "description": "The function that the holder of the post fulfills",
            "type": ["string", "null"],
        },
        "organization_id": {
            "description": "The ID of the organization in which the post is held",
            "type": "string",
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
    "title": "Post",
    "type": "object"
}
