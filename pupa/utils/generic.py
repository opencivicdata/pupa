import os
import json
import pytz
import datetime
import subprocess


def utcnow():
    return datetime.datetime.now(datetime.timezone.utc)


def _make_pseudo_id(**kwargs):
    """ pseudo ids are just JSON """
    # ensure keys are sorted so that these are deterministic
    return '~' + json.dumps(kwargs, sort_keys=True)


def get_pseudo_id(pid):
    if pid[0] != '~':
        raise ValueError("pseudo id doesn't start with ~")
    return json.loads(pid[1:])


def makedirs(dname):
    if not os.path.isdir(dname):
        os.makedirs(dname)


class JSONEncoderPlus(json.JSONEncoder):
    """
    JSONEncoder that encodes datetime objects as Unix timestamps.
    """
    def default(self, obj, **kwargs):
        if isinstance(obj, datetime.datetime):
            if obj.tzinfo is None:
                raise TypeError(
                    "date '%s' is not fully timezone qualified." % (obj))
            obj = obj.astimezone(pytz.UTC)
            return "{}".format(obj.isoformat())
        elif isinstance(obj, datetime.date):
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


def format_datetime(dt, timezone):
    return pytz.timezone(timezone).localize(dt).replace(microsecond=0).isoformat()
