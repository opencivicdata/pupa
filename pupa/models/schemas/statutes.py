from .common import links, contact_details, identifiers, other_names, sources

structure_schema = {
    "$schema": "http://json-schema.org/draft-03/schema#",
    "description": "A structural node within a statute hierarchy.",
    "id": "http://openstates.com/schemas/statute_structure_node.json#",
    "properties": {
        "division": {
            "description": "Title, Part, SubChapter, Section, etc.",
            "type": ["string"],
        },
        "enum": {
            "description": "1 or a. or 123.4-a, etc.",
            "type": ["string"],
        },
        "heading": {
            "description": "Heading or title text associated with this node.",
            "type": ["string"],
        },
        "sources": sources,
    },
    "title": "structure_node",
    "type": "object"
}

edge_schema = {
    "$schema": "http://json-schema.org/draft-03/schema#",
    "description": "A structural node within a statute hierarchy.",
    "id": "http://openstates.com/schemas/statute_edge.json#",
    "properties": {
        "in_id": {
            "description": "The id of the inbound node.",
            "type": ["string"],
        },
        "out_id": {
            "description": "The id of the outbound node.",
            "type": ["string"],
        },
    },
    "title": "edge",
    "type": "object"
}


note_schema = []
history_schema = []

content_schema = {
    "$schema": "http://json-schema.org/draft-03/schema#",
    "description": "A content node within a statute hierarchy.",
    "id": "http://openstates.com/schemas/statute_content_node.json#",
    "properties": {
        "division": {
            "description": "Title, Part, SubChapter, Section, etc.",
            "type": ["string"],
        },
        "enum": {
            "description": "1 or a. or 123.4-a, etc.",
            "type": ["string"],
        },
        "heading": {
            "description": "Heading or title text associated with this node.",
            "type": ["string"],
        },
        "children": [],
        "sources": sources,
    },
    "title": "content_node",
    "type": "object"
}

content_schema['properties']['children'].append(content_schema)
