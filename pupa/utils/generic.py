import re
import os
import time
import json
import datetime
import subprocess
from validictory.validator import SchemaValidator


def make_psuedo_id(**kwargs):
    """ psuedo ids are just JSON """
    return '~' + json.dumps(kwargs)


def get_psuedo_id(pid):
    if pid[0] != '~':
        raise ValueError("psuedo id doesn't start with ~")
    return json.loads(pid[1:])


def psuedo_organization(organization, chamber, classification='legislature'):
    """ helper for setting an appropriate ID for organizations """
    if organization and chamber:
        raise ValueError('cannot specify both chamber and organization')
    elif chamber:
        return make_psuedo_id(classification=classification, chamber=chamber)
    elif organization:
        return organization
    else:
        # neither specified
        return make_psuedo_id(classification=classification)


def makedirs(dname):
    if not os.path.isdir(dname):
        os.makedirs(dname)


_bill_id_re = re.compile(r'([A-Z]*)\s*0*([-\d]+)')
_mi_bill_id_re = re.compile(r'(SJR|HJR)\s*([A-Z]+)')


def fix_bill_id(bill_id):
    bill_id = bill_id.replace('.', '')
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
        if isinstance(obj, datetime.datetime):
            return time.mktime(obj.utctimetuple())
        elif isinstance(obj, datetime.date):
            return time.mktime(obj.timetuple())

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
