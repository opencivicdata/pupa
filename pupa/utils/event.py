import datetime as dt
import pytz


EVENT_TIME_FORMATS = [
    "%Y-%m-%dT%I:%M:SZ",
    "%Y-%m-%dT%I:%MZ",
    "%Y-%m-%d",
]


def read_event_iso_8601(when):
    for fmt in EVENT_TIME_FORMATS:
        try:
            return dt.datetime.strptime(when, fmt)
        except ValueError:
            continue
    raise ValueError("Error: `%s' does not match any known format." % (when))
