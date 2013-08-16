from validictory.validator import SchemaValidator
import datetime


class DatetimeValidator(SchemaValidator):
    """ add 'datetime' type that verifies that it has a datetime instance """

    def validate_type_datetime(self, x):
        return isinstance(x, (datetime.date, datetime.datetime))


def add_associated_link(self, collection, name, url,
                        type, mimetype, on_duplicate, date=None, offset=None,
                        document_id=None):

    if on_duplicate not in ['error', 'ignore']:
        raise TypeError("Sorry; we accept either `error' or `ignore' for "
                        "on_duplicate behavior.")

    try:
        versions = getattr(self, collection)
    except AttributeError:
        versions = self[collection]

    ver = {'name': name, 'links': [], 'date': date, 'offset': offset,
           'type': type, 'document_id': document_id}

    seen_links = set()  # We iterate over everything anyway. Meh. Storing
    # as an instance var is actually non-trivial, since we abuse __slots__
    # for as_dict, and it's otherwise read-only or shared set() instance.

    matches = 0
    for version in versions:
        for link in version['links']:
            seen_links.add(link['url'])

        if False not in (ver.get(x) == version.get(x)
                         for x in ["name", "type", "date"]):
            matches = matches + 1
            ver = version

    if matches > 1:
        raise ValueError("Something went just very wrong internally")

    if url in seen_links:
        if on_duplicate == 'error':
            raise ValueError("Duplicate entry in `%s' - URL: `%s'" % (
                collection, url
            ))
        else:
            # This means we're in ignore mode. This situation right here
            # means we should *skip* adding this link silently and continue
            # on with our scrape. This should *ONLY* be used when there's
            # a site issue (Version 1 == Version 2 because of a bug) and
            # *NEVER* because "Current" happens to match "Version 3". Fix
            # that in the scraper, please.
            #  - PRT
            return None

    # OK. This is either new or old. Let's just go for it.
    ret = {'url': url, 'mimetype': mimetype}

    ver['links'].append(ret)

    if matches == 0:
        # in the event we've got a new entry; let's just insert it into
        # the versions on this object. Otherwise it'll get thrown in
        # automagically.
        versions.append(ver)

    return ver
