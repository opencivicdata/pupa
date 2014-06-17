"""
    Schema for bill objects.
"""

from .common import sources, extras
from opencivicdata import common

schema = {
    "description": "bill data",
    "type": "object",
    "_order": (
        ('Basics', ('from_organization', 'session', 'name', 'chamber',
                    'title', 'type', 'subject', 'summaries')),
        ('Common Fields', ['updated_at', 'created_at', 'sources']),
        ('Other/Related Bills', ('other_titles', 'other_names', 'related_bills')),
        ('Sponsors and Actions', ('sponsors', 'actions')),
        ('Documents and Versions', ('documents', 'versions')),
    ),
    "properties": {

        "from_organization": {
            "type": ["string", "null"],
            "description": "name of the legislative body that this bill belongs to"
        },

        "session": {"type": "string",
                    "description": "associated with one of the jurisdiction's sessions"},

        "name": {"type": "string",
                 "description": ("jurisdiction-assigned permanent name.  Must be unique within a "
                                 "given session (e.g. HB 3).  Note: not to be confused with "
                                 "``title``.")},

        'updated_at': {"type": ["string", "datetime"], "required": False,
                       "description": "the time that the object was last updated", },

        'created_at': {"type": ["string", "datetime"], "required": False,
                       "description": "the time that this object was first created", },

        "title": {"type": "string", "description": "primary display title for the bill"},

        "classification": {"items": {"type": "string", "enum": common.BILL_CLASSIFICATIONS},
                           "type": "array",
                           "description": "array of types (e.g. bill, resolution)"},

        "subject": {
            "items": {"type": "string"},
            "type": "array",
            "description": "List of related subjects.",
        },

        "summaries": {
            "items": {
                "properties": {
                    "text": {"type": "string", "description": "Summary of bill."},
                    "note": {"type": ["string", "null"],
                             "description": "note describing source of summary"},
                },
                "type": "object"},
            "type": "array",
            "description": ("List of summaries of bill, each item in list has a note and text "
                            "attribute."),
        },

        "other_titles": {
            "items": {
                "properties": {
                    "title": {"type": "string", "description": "Alternate title."},
                    "note": {"type": ["string", "null"], "description": "Note describing source."},
                },
                "type": "object"
            },
            "type": "array",
            "description": ("list of other titles this bill is known by."
                            "A common use is when a state provides a common title and a long "
                            "or technical title as well.  It is also acceptable to include "
                            "popular but unofficial titles of the bill as well, such as"
                            "'Obamacare' for the 'Patient Protection and Affordable Care Act.'"
                            "`note` can be used to describe the relationship this has to the "
                            "bill, for example Obamacare might be noted as a colloquial name. "
                            "Each item in the list has a title and a note.")
        },

        "other_names": {
            "items": {
                "properties": {
                    "name": {"type": "string", "description": "name (e.g. HB 22)"},
                    "note": {"type": ["string", "null"],
                             "description": "note describing why this name is attached"},
                },
                "type": "object"
            },
            "type": "array",
            "description": ("list of other names this bill is known by in the current session, "
                            "for example if HB 33 and SB 17 refer to the same bill this prevents "
                            "having to have identical entries for each.")

        },

        "related_bills": {
            "items": {
                "properties": {
                    "session": {"type": "string", "description": "Session of related bill."},
                    "name": {"type": "string", "description": "Name of related bill."},
                    "relation_type": {
                        "enum": common.BILL_RELATION_TYPES,
                        "type": "string",
                        "description": (
                            """
                            This notes what kind of relation exists between the
                            two bills - something like 'companion' for a
                            companion bill, 'other-session' for a reintroduction
                            or past session of a bill, or 'replaces' /
                            'replaced-by' for something like an omnibus bill.
                            """
                        ),
                    },
                },
                "type": "object"
            },
            "type": "array",
            "description": ("Links to related bills.  Currently only used for companion bills, "
                            "but extensible for other uses."),

        },

        "sponsors": {
            "items": {
                "properties": {
                    "classification": {
                        "type": "string",
                        "description": "Type of sponsorship, via upstream source."
                    },
                    "primary": {
                        "type": "boolean",
                        "description": "Indicates if sponsor is considered primary by source",
                    },
                    "name": {"type": "string",
                             "description": "Name of sponsor, as given by source.", },
                    "id": {"type": ["string", "null"],
                           "description": ("ID of entity if the sponsor has been resolved to "
                                           "another entity in the database."), },
                    "_type": {"type": ["string", "null"], "enum": ["organization", "person"],
                              "description": ("Type of entity if the sponsor has been resolved to "
                                              "another entity in the database."), }
                },
                "type": "object"
            },
            "type": "array",
            "description": "List of entities responsible for sponsoring/authoring the bill."
        },

        "actions": {
            "items": {
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "description of the action taken as given by source"
                    },
                    "organization": {
                        "type": ["string", "null"],
                        "description": "organization the action took place in"
                    },
                    "date": {
                        "pattern": "^[0-9]{4}(-[0-9]{2}){0,2}$",
                        "type": "string",
                        "description": "date of action"
                    },
                    "classification": {
                        "items": {
                            "type": "string",
                            "enum": common.BILL_ACTION_CLASSIFICATIONS,
                        },
                        "type": "array",
                        "description": "array of normalized action types",
                    },
                    "related_entities": {
                        "items": {
                            "properties": {
                                "name": {"type": "string",
                                         "description": "Name of entity given by source data"},
                                "entity_type": {
                                    "enum": ["organization", "person"],
                                    "type": ["string", "null"],
                                    "description": ("Type of entity if the sponsor has been "
                                                    "resolved to another entity in the "
                                                    "database."), },
                                "id": {"type": ["string", "null"],
                                       "description": ("ID of entity if the sponsor has been "
                                                       "resolved to another entity in the "
                                                       "database.")},
                            },
                            "type": "object"
                        },
                        "type": "array",
                        "description": ("list of related entities for the action, such as related "
                                        "committee for a referral or a person for a sponsorship.")
                    },
                },
                "type": "object"
            },
            "type": "array",
            "description": "List of actions taken on the bill."
        },


        # == Documents and Versions ==

        "versions": {
            "items": {
                "properties": {
                    "name": {"type": "string", "description": "Name of version"},
                    "type": {"type": "string", "blank": True,
                             "description": "Type of version"},
                    "date": {
                        "pattern": "^([0-9]{4})?(-[0-9]{2}){0,2}$",
                        "type": "string", "blank": True,
                        "description": "Version posting date",
                    },
                    "links": {
                        "items": {
                            "properties": {
                                "mimetype": {"type": "string", "blank": True,
                                             "description": "mimetype of document"},
                                "url": {"type": "string", "description": "URL to document"}
                            },
                            "type": "object"
                        },
                        "type": "array",
                        "description": "List of links for this version (pdf, html, etc.)."
                    },
                },
                "type": "object"
            },
            "type": "array",
            "description": "Versions of a bill's text (First Printing, As Amended, etc.)"
        },
        "documents": {
            "items": {
                "properties": {
                    "name": {"type": "string", "description": "Name of document"},
                    "type": {"type": "string", "blank": True,
                             "description": "Type of document"},
                    "date": {
                        "pattern": "^([0-9]{4})?(-[0-9]{2}){0,2}$",
                        "type": "string", "blank": True,
                        "description": "Document posting date",
                    },
                    "links": {
                        "items": {
                            "properties": {
                                "mimetype": {"type": "string", "blank": True,
                                             "description": "mimetype of document"},
                                "url": {"type": "string", "description": "URL to document"}
                            },
                            "type": "object"
                        },
                        "type": "array",
                        "description": "List of links to text for this document (pdf, html, etc.)."
                    },
                },
                "type": "object"
            },
            "type": "array",
            "description": "Any non-version related documents. (elements same format as versions)",
        },
        "sources": sources,
        "extras": extras,
    }
}
