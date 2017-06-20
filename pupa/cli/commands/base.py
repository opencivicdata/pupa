class BaseCommand(object):

    def __init__(self, subparsers):
        self.subparser = subparsers.add_parser(self.name, description=self.help)
        self.add_args()

    def add_args(self):
        pass

    def add_argument(self, *args, **kwargs):
        self.subparser.add_argument(*args, **kwargs)

    def handle(self, args):
        raise NotImplementedError('commands must implement handle(args)')
