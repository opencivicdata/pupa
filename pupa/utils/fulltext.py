import os
import subprocess

import lxml.html
import requests
import scrapelib


s = scrapelib.Scraper()


def html_to_text(response):
    doc = lxml.html.fromstring(response.text)
    text = doc.text_content()
    return text


def pdf_to_text(response):
    # Download the file
    if not os.path.exists(os.path.join(os.getcwd(), '_cache')):
        os.makedirs(os.path.join(os.getcwd(), '_cache'))
    local_filename = os.path.join(os.getcwd(), '_cache', format(response.url.split('/')[-1]))
    with open(local_filename, 'wb') as pdf_file:
        for block in response.iter_content(1024):
            if block:
                pdf_file.write(block)

    try:
        pipe = subprocess.Popen(['pdftotext', '-layout', local_filename, '-'],
            stdout=subprocess.PIPE,
            close_fds=True).stdout
    except OSError as e:
        print('Unable to parse the bill PDF\n{}'.format(e))
    text = pipe.read().decode('utf-8')

    pipe.close()
    os.remove(local_filename)

    return text


def clean_text(text):
    text = ' '.join(text.split())

    return text


def version_to_text(version):
    text = ''

    link = None
    filetype = None
    preferred_mimetypes = ['text/html', 'application/pdf', ]
    for mimetype in preferred_mimetypes:
        for link_obj in version.links.all():
            if link_obj.media_type == mimetype:
                try:
                    r = s.get(link_obj.url)
                except scrapelib.HTTPError, requests.exceptions.ReadTimeout:
                    pass
                else:
                    filetype = mimetype.split('/')[-1]
                    link = link_obj.url
        if filetype or link:
            break

    if filetype == 'html':
        text = html_to_text(r)
    elif filetype == 'pdf':
        text = pdf_to_text(r)
    else:
        pass

    text = clean_text(text)
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
    es_bill['text'] = ''
    latest_version = None
    for version in bill.versions.all().order_by('date'):
        latest_version = version
    if latest_version:
        text = version_to_text(latest_version)
        es_bill['text'] = text

    return es_bill
