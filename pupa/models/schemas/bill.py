"""
    Schema for bill objects.
"""

from .common import sources


BILL_TYPES = ['bill', 'resolution', 'concurrent resolution',
              'joint resolution', 'memorial']
ACTION_TYPES = ['introduced', 'reading:1', 'reading:2', 'reading:3']
VERSION_TYPES = []
DOCUMENT_TYPES = []


schema = {
    "description": "bill data",
    "type": "object",
    "properties": {

        # == Basics ==

        # **_type** - All objects must have a _type field set to bill.
        "_type": {"enum": ["bill"], "type": "string"},

        # **organization** - name of the Legislative body that this instrument
        # was introduced into.
        "organization": {"type": ["string", "null"]},

        # **organization_id** - ID of the Legislative body that this instrument
        # was introduced into.
        "organization_id": {"type": ["string", "null"]},

        # **session** - Associated with one of jurisdiction's sessions
        "session": {"type": "string"},

        # **name** - Jurisdiction-assigned permanent name, unique within a
        # given jurisdiction's session (e.g. HB 3)
        # (this is not guaranteed to be numeric, etc. but should not be
        #  confused with title)
        "name": {"type": "string"},

        # **updated_at** - the time that this object was last updated.
        "updated_at": {"type": ["string", "datetime"], "required": False},

        # **created_at** - the time that this object was first created.
        "created_at": {"type": ["string", "datetime"], "required": False},

        # **chamber** - (if legislature is bicameral) otherwise can be null
        "chamber": {
            "enum": ["upper", "lower"], "type": ["string", "null"],
        },

        # **title** - primary display title for bill
        "title": {"type": "string"},

        # **type** - array of types (e.g. bill, resolution, etc.)
        "type": {"items": {"type": "string"}, "type": "array"},

        # **subject** - List of related subjects.
        "subject": {
            "items": {"type": "string"},
            "type": "array"
        },

        # **summaries** - List of summaries of bill.  Each item in list
        # has a note and text attribute.
        "summaries": {
            "items": {
                "properties": {
                    "text": {"type": "string"},
                    "note": {"type": ["string", "null"]},
                },
                "type": "object"
            },
            "type": "array"
        },

        # == Other/Related Bills ==

        # **other_titles** - list of other titles this bill is known by.
        # A common use is when a state provides a common title and a long
        # or technical title as well.  It is also acceptable to include
        # popular but unofficial titles of the bill as well, such as
        # 'Obamacare' for the 'Patient Protection and Affordable Care Act'
        # Note can be used to describe the relationship this has to the
        # bill, for example Obamacare might be noted as a colloquial name.
        # Each item in the list has a title and a note.
        "other_titles": {
            "items": {
                "properties": {
                    "title": {"type": "string"},
                    "note": {"type": ["string", "null"]},
                },
                "type": "object"
            },
            "type": "array"
        },

        # **other_names** - list of other names this bill is known by
        # in the current session, for example if HB 33 and SB 17 refer to the
        # same bill this prevents having to have identical entries for each.
        # Each item in the list has a name and a note.
        "other_names": {
            "items": {
                "properties": {
                    "name": {"type": "string"},
                    "note": {"type": ["string", "null"]},
                },
                "type": "object"
            },
            "type": "array"
        },

        # **related_bills** - Links to related bills, currently only used
        # for companion bills, but extensible for other uses.
        # Each entry in the related_bills array has the following properties:
        #
        "related_bills": {
            "items": {
                "properties": {
                    #  * **session** - session of related bill.
                    "session": {"type": "string"},
                    #  * **name** - name of related bill.
                    "name": {"type": "string"},
                    #  * **relation_type** - currently should be 'companion', others may be
                    #                        introduced in the future
                    "relation_type": {"enum": ["companion"], "type": "string"},
                },
                "type": "object"
            },
            "type": "array"
        },

        # == Sponsors and Actions ==

        # **sponsors** - List of entities responsible for sponsoring/authoring
        # the bill.  Each object in the array has the following properties:
        "sponsors": {
            "items": {
                "properties": {
                    # * **sponsorship_type** - Type of sponsorship, indicated by upstream source.
                    "sponsorship_type": {"type": "string"},
                    # * **primary** - Indicates if sponsor is considered primary by the upstream
                    #                 source.
                    "primary": {"type": "boolean"},
                    # * **name** - Name of sponsor, as given by source data.
                    "name": {"type": "string"},
                    # * **chamber** - Chamber of sponsor, for use with resolution.
                    #                 TODO: convert to a 'hint' object?
                    "chamber": {"enum": ["upper", "lower"], "type": ["string", "null"]},
                    # * **id** - ID of entity if the sponsor has been resolved to another entity
                    #            in the database.
                    "id": {"type": ["string", "null"]},
                    # * **_type** - type of entity if the sponsor has been resolved to another
                    #               entity in the database.
                    "_type": {"type": ["string", "null"], "enum": ["organization", "person"]}
                },
                "type": "object"
            },
            "type": "array"
        },

        # **actions** - List of actions taken on the bill.  Each object in the
        # array has the following properties:
        "actions": {
            "items": {
                "properties": {
                    # * **action** - description of the action taken, as given by upstream source.
                    "description": {"type": "string"},
                    # * **actor** - name for the actor (e.g. 'upper', 'lower', 'executive', etc.)
                    "actor": {"type": ["string", "null"]},
                    # * **date** - date of the action
                    "date": {"pattern": "^[0-9]{4}(-[0-9]{2}){0,2}$", "type": "string"},
                    # * **type** - array of categorized action types
                    "type": {
                        "items": {
                            "type": "string"
                        },
                        "type": "array"
                    },
                    # * **related_entities** - list of related entities for
                    # this action, such as a related committee for a referral
                    # or sponsor for a sponsorship.  An array of objects with
                    # the following properties:
                    #     * **name** - Name of entity, as given by source data.
                    #     * **_type** - type of entity if the sponsor has been resolved to
                    #                   another entity in the database.
                    #     * **id** - ID of entity if the sponsor has been resolved to another
                    #                entity in the database.
                    "related_entities": {
                        "items": {
                            "properties": {
                                "name": {"type": "string"},
                                "_type": {"enum": ["organization", "person"],
                                          "type": ["string", "null"]},
                                "id": {"type": ["string", "null"]},
                            },
                            "type": "object"
                        },
                        "type": "array"
                    },
                },
                "type": "object"
            },
            "type": "array"
        },


        # == Documents and Versions ==

        # **documents** and **versions** are both arrays of objects with the
        # same properties. The difference between the two is that versions are
        # versions of a bill's text (e.g. First Printing, As Amended, etc.)
        # while documents can be any other related documents (such as
        # Fiscal Notes, Committee Reports, etc.).
        #
        # Properties of document/version objects are:
        #
        # * **name** - name of document/version
        # * **type** - type of document/version
        # * **date** - date that document/version was created
        # * **links** - array of links to the version/document.
        #               Multiple links should point to same version/document
        #               in different formats. Each link consists of:
        #       * **url**   - URL of resource.
        #       * **mimetype** - mimetype of the resource.
        "documents": {
            "items": {
                "properties": {
                    "name": {"type": "string"},
                    "type": {"type": ["string", "null"], "enum": DOCUMENT_TYPES},
                    "date": {
                        "pattern": "^[0-9]{4}(-[0-9]{2}){0,2}$",
                        "type": ["string", "null"]
                    },
                    "links": {
                        "items": {
                            "properties": {
                                "mimetype": {"type": ["string", "null"]},
                                "url": {"type": "string"}
                            },
                            "type": "object"
                        },
                        "type": "array"
                    },
                },
                "type": "object"
            },
            "type": "array"
        },
        "versions": {
            "items": {
                "properties": {
                    "name": {"type": "string"},
                    "type": {"type": ["string", "null"], "enum": VERSION_TYPES},
                    "date": {
                        "pattern": "^[0-9]{4}(-[0-9]{2}){0,2}$",
                        "type": ["string", "null"],
                    },
                    "links": {
                        "items": {
                            "properties": {
                                "mimetype": {"type": ["string", "null"]},
                                "url": {"type": "string"}
                            },
                            "type": "object"
                        },
                        "type": "array"
                    },
                },
                "type": "object"
            },
            "type": "array"
        },
        "sources": sources,
    }
}
