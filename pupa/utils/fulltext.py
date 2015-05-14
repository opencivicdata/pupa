import urllib


def document_url_to_text(url):
    with open(urllib2.urlopen(url), 'wb') as doc:
        pass

    return text


def bill_to_elasticsearch(bill):
    es_bill = {}

    # Include auxilary informaiton about the bill, besides its text
    DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S'

    es_bill['jurisdiction'] = bill.get_jurisdiction_name()
    es_bill['session'] = bill.get_session_name()
    es_bill['identifier'] = bill.identifier
    es_bill['subjects'] = bill.subject
    es_bill['classifications'] = bill.classification
    es_bill['updated_at'] = bill.updated_at.strftime(DATETIME_FORMAT)
    es_bill['created_at'] = bill.created_at.strftime(DATETIME_FORMAT)

    es_bill['titles'] = [bill.title, ]
    for other_title in bill.other_titles.all():
        es_bill['titles'].append(other_title.title)

    # Recursively retrieve all organizations that the bill is related to
    es_bill['organizations'] = []
    organization = bill.from_organization
    while True:
        try:
            es_bill['organizations'].append(organization.name)
        except AttributeError:
            break
        organization = organization.parent

    es_bill['sponsors'] = []
    for sponsor in bill.sponsorships.all().filter(bill=bill):
        es_bill['sponsors'].append(sponsor.name)

    es_bill['action_dates'] = []
    for action in bill.actions.all():
        es_bill['action_dates'].append(action.date)

    # Gather the text of the most recent bill
    # If dates are present, use the one version most recently added to the database
    es_bill['text'] = []
    latest_version = None
    for version in bill.versions.all().order_by('date'):
        latest_version = version
    # es_bill['text'].append(document_url_to_text(latest_version.url))

    return es_bill
