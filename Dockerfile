FROM        debian:jessie
MAINTAINER  Paul R. Tagliamonte <paultag@sunlightfoundation.com>

RUN apt-get update && apt-get install -y \
    python3.4 python3-pip libpq-dev git libgeos-dev

RUN mkdir -p /opt/sunlightfoundation.com/
ADD . /opt/sunlightfoundation.com/pupa/
RUN pip3 install -r /opt/sunlightfoundation.com/pupa/requirements-test.txt
RUN pip3 install psycopg2
RUN pip3 install -e /opt/sunlightfoundation.com/pupa/
RUN pip3 install -e git://github.com/opencivicdata/python-opencivicdata-django.git#egg=opencivicdata-django
RUN pip3 install jsonfield django-uuidfield
RUN pip3 install jsonfield kafka-python

RUN mkdir -p /pupa
WORKDIR /pupa

ENV PYTHONIOENCODING 'utf-8'
ENV LANG 'en_US.UTF-8'

ENTRYPOINT ["pupa"]
