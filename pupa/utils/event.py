import datetime as dt
import pytz


EVENT_TIME_FORMATS = [
    "%Y-%m-%dT%H:%M:%S.%f+00:00",
    "%Y-%m-%dT%H:%M:%S+00:00",
    "%Y-%m-%dT%H:%M+00:00",

    "%Y-%m-%dT%H:%M:%S.%fZ",
    "%Y-%m-%dT%H:%M:%SZ",
    "%Y-%m-%dT%H:%MZ",

    "%Y-%m-%d",
]


def read_event_iso_8601(when):
    for fmt in EVENT_TIME_FORMATS:
        try:
            return dt.datetime.strptime(when, fmt)
        except ValueError:
            continue
    raise ValueError("Error: `%s' does not match any known format." % (when))
