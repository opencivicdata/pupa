from opencivicdata.models.bill import Bill

from .base import BaseCommand
from pupa.utils.fulltext import bill_to_elasticsearch
from pupa.settings import elasticsearch


class Command(BaseCommand):
    name = 'elasticsearch-push'
    help = 'Push information about `Bill` objects to the elasticsearch instance'

    def add_args(self):
        self.add_argument('jurisdictions', type=str, nargs='+',
            help="Full OCD jurisdiction IDs to push; pass `all` to push all")

    def handle(self, args, other):
        if elasticsearch is None:
            raise AssertionError(
                "No elasticsearch instance found; make sure it's configured")

        if args.jurisdictions == ['all', ]:
            for bill in Bill.objects.all():
                elasticsearch.index(
                    index='ocd', doc_type='bill', id=bill.id,
                    doc=bill_to_elasticsearch(bill))

        else:
            for jurisdiction in args.jurisdictions:
                for bill in Bill.objects.filter(from_organization__jurisdiction=jurisdiction):
                    elasticsearch.index(
                        index='ocd', doc_type='bill', id=bill.id,
                        doc=bill_to_elasticsearch(bill))
