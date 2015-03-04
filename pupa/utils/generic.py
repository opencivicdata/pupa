import re
import os
import json
import pytz
import datetime
import subprocess
from urllib.parse import urlsplit, parse_qsl, urlencode, urlunsplit, SplitResult
from validictory.validator import SchemaValidator


def make_pseudo_id(**kwargs):
    """ pseudo ids are just JSON """
    return '~' + json.dumps(kwargs)


def get_pseudo_id(pid):
    if pid[0] != '~':
        raise ValueError("pseudo id doesn't start with ~")
    return json.loads(pid[1:])


def makedirs(dname):
    if not os.path.isdir(dname):
        os.makedirs(dname)


_bill_id_re = re.compile(r'([A-Z]*)\s*0*([-\d]+)')
_mi_bill_id_re = re.compile(r'(SJR|HJR)\s*([A-Z]+)')


def fix_bill_id(bill_id):
    # special case for MI Joint Resolutions
    if _mi_bill_id_re.match(bill_id):
        return _mi_bill_id_re.sub(r'\1 \2', bill_id, 1).strip()
    return _bill_id_re.sub(r'\1 \2', bill_id, 1).strip()


class DatetimeValidator(SchemaValidator):
    """ add 'datetime' type that verifies that it has a datetime instance """

    def validate_type_datetime(self, x):
        return isinstance(x, (datetime.date, datetime.datetime))


class JSONEncoderPlus(json.JSONEncoder):
    """
    JSONEncoder that encodes datetime objects as Unix timestamps.
    """
    def default(self, obj, **kwargs):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            if obj.tzinfo is None:
                raise TypeError(
                    "date '%s' is not fully timezone qualified." % (obj))
            obj = obj.astimezone(pytz.UTC)
            return "{}".format(obj.isoformat())
        return super(JSONEncoderPlus, self).default(obj, **kwargs)


def convert_pdf(filename, type='xml'):
    commands = {'text': ['pdftotext', '-layout', filename, '-'],
                'text-nolayout': ['pdftotext', filename, '-'],
                'xml': ['pdftohtml', '-xml', '-stdout', filename],
                'html': ['pdftohtml', '-stdout', filename]}
    try:
        pipe = subprocess.Popen(commands[type], stdout=subprocess.PIPE, close_fds=True).stdout
    except OSError as e:
        raise EnvironmentError("error running %s, missing executable? [%s]" %
                               ' '.join(commands[type]), e)
    data = pipe.read()
    pipe.close()
    return data


def canonize_url(url):
    split_url = urlsplit(url)

    canonical_query = urlencode(sorted(parse_qsl(split_url.query)))
    return urlunsplit(SplitResult(scheme=split_url.scheme,
                                  netloc=split_url.netloc,
                                  path=split_url.path,
                                  query=canonical_query,
                                  fragment=split_url.fragment))
