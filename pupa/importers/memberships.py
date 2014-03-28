from .base import BaseImporter
from .utils import people_by_jurisdiction_and_name
from pupa.models import Membership
from pupa.core import db


def match_membership(membership, people=None):
    if membership.unmatched_legislator:
        if people is None:
            unmatched_name = membership['unmatched_legislator']['name']
            people = people_by_jurisdiction_and_name(
                unmatched_name,
                membership['jurisdiction_id'],
            )

        if people.count() == 1:
            person = people[0]
            #   + update membership with this person's details (if it's
            #     not there already)
            membership.person_id = person['_id']
            membership.unmatched_legislator = None
            return (True, membership)
    return (False, membership)


class MembershipImporter(BaseImporter):
    _type = 'membership'
    _model_class = Membership

    def __init__(self, jurisdiction_id, person_importer, org_importer):
        super(MembershipImporter, self).__init__(jurisdiction_id)
        self.person_importer = person_importer
        self.org_importer = org_importer

    def get_db_spec(self, membership):
        spec = {'organization_id': membership.organization_id,
                'person_id': membership.person_id,
                'role': membership.role,
                # if this is a historical role, only update historical roles
                'end_date': membership.end_date}

        if membership.post_id:
            # The reason for adding this in a conditional is that
            # we may not always know the post in the scraper, but we shouldn't
            # make a mess with membership that have been attached to a post
            # manually. If we know it in the scraper, it better be in the DB!
            spec['post_id'] = membership.post_id

        if membership.unmatched_legislator:
            spec['unmatched_legislator'] = membership.unmatched_legislator
            unmatched_name = membership.unmatched_legislator['name']

            people = people_by_jurisdiction_and_name(membership.jurisdiction_id, unmatched_name)

            matched, membership = match_membership(membership, people=people)

            if matched:
                # We were able to simply match. Let's roll with this.
                spec = self.get_db_spec(membership)

                # OK. Since we matched, let's also update existing
                # copies of this guy.

                # This will find anyone who has our ID *OR* has a None.
                pspec = spec.copy()
                pspec['person_id'] = membership.person_id

                person = db.people.find_one({"_id": membership.person_id})
                if person is None:
                    # Um. OK. This membership is linked to a ghost-person.
                    print("Warning: %s is linked to an UNKNOWN PERSON" % membership['_id'])
                    # The proper behavior here isn't clear. Rather than let
                    # unclean data into the DB, I'm going to break the import
                    # process.
                    raise Exception(
                        """
                        Bad membership link that got matched. This is likely an
                        internal bug. Please look at this *CAREFULLY* to work
                        out proper behavior
                        """
                    )

                uspec = spec.copy()
                uspec['person_id'] = None
                uspec['unmatched_legislator.name'] = {
                    "$in": [
                        x['name'] for x in person['other_names']
                    ] + [person['name']]
                }
                spec = {"$or": [pspec, uspec]}
                return spec

            # This will find anyone who has our name *OR* has a None.
            # (not the same code as above)
            pspec = spec.copy()
            pspec['person_id'] = {"$in": people.distinct("_id")}
            pspec.pop('unmatched_legislator')
            # Either we have this person, who's already matched (e.g.
            # everything already matches)

            uspec = spec.copy()
            uspec['person_id'] = None
            # Or we don't, and we need to find a membership with an
            # unmatched ID
            spec = {"$or": [pspec, uspec]}

        return spec

    def prepare_object_from_json(self, obj):
        org_json_id = obj['organization_id']

        if org_json_id.startswith("jurisdiction:"):
            _, jid = org_json_id.split(":", 1)
            org = self.org_importer._resolve_org_by_chamber(jid, obj['chamber'])
            if org is None:
                raise ValueError("Something went wrong with the Jurisidction "
                                 "import")
            obj['organization_id'] = org['_id']
        else:
            obj['organization_id'] = self.org_importer.resolve_json_id(org_json_id)

        person_json_id = obj['person_id']
        obj['person_id'] = self.person_importer.resolve_json_id(person_json_id)
        return obj
