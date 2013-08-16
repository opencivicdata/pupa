"""
    Schema for vote objects.
"""

from .common import sources


VOTE_TYPES = ['passage', 'amendment', 'reading:2', 'reading:3',
              'veto_override', 'other']
ROLLCALL_TYPES = ['yes', 'no', 'abstain', 'not-voting', 'other']


schema = {
    "description": "vote data",
    "type": "object",
    "properties": {

        # == Basics ==

        # **organization** - name of the voting organization.
        "organization": {"type": ["string", "null"]},

        # **organization_id** - ID of the voting organization.
        "organization_id": {"type": ["string", "null"]},

        # **_type** - All vote objects must have a _type field set to vote.
        "_type": {"enum": ["vote"], "type": "string"},

        # **session** - Associated with one of jurisdiction's sessions
        "session": {"type": "string"},

        # **updated_at** - the time that this object was last updated.
        "updated_at": {"type": ["string", "datetime"], "required": False},

        # **created_at** - the time that this object was first created.
        "created_at": {"type": ["string", "datetime"], "required": False},


        # **chamber** - chamber vote took place in (if legislature is
        # bicameral, otherwise null)
        "chamber": {
            "enum": ["upper", "lower", "joint"], "type": ["string", "null"],
        },

        # **date** - date of the action
        "date": {"pattern": "^[0-9]{4}(-[0-9]{2}){0,2}$", "type": "string"},

        # **motion** - description of motion (from upstream source)
        "motion": {"type": "string"},

        # **type** - array of types (e.g. passage, veto_override, etc.)
        "type": {"items": {"type": "string", "enum": VOTE_TYPES},
                 "type": "array"},

        # **passed** - boolean indicating passage
        "passed": {"type": "boolean"},

        # == Relationship to Bill ==

        # **bill** - Related bill, votes will have a non-null bill object if
        # they are related to a bill. Bills will have the following fields:
        #

        "bill": {
            "type": ["object", "null"],
            "properties": {
                # * **id** - bill's internal id if bill was matched with
                # an object in the database
                "id": {"type": ["string", "null"]},
                # * **name** - bill name (e.g. HB 21)
                "name": {"type": "string"},
                # * **chamber** - bill's chamber if vote was on a bill (and
                # legislature is bicameral, otherwise null)
                "chamber": {
                    "enum": ["upper", "lower"], "type": ["string", "null"],
                },
            }
        },

        # == Vote Counts ==

        # **vote_counts** is a list of objects with vote_type and count
        # properties.  vote_type is something like 'yes', 'no', 'not-voting',
        # etc.
        "vote_counts": {
            "items": {
                "properties": {
                    "vote_type": {"type": "string", "enum": ROLLCALL_TYPES},
                    "count": {"type": "integer", "minimum": 0}
                },
                "type": "object"
            },
        },

        # **roll_call** is a list of objects with the following fields:
        #
        "roll_call": {
            "items": {
                "type": "object",
                "properties": {
                    # * **vote_type** - type of vote (e.g. yes, no, abstain)
                    "vote_type": {"type": "string", "enum": ROLLCALL_TYPES},

                    # * **person** - person object representing the voter,
                    # has the following fields:
                    #     * **name** - person's name as provided by source
                    #     * **id** - person's internal id if they've been
                    #       matched to an entity in the database
                    "person": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "id": {"type": ["string", "null"]},
                        }
                    }
                }
            }
        },

        "sources": sources,
    }
}
