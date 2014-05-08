FROM        debian:jessie
MAINTAINER  Paul R. Tagliamonte <paultag@sunlightfoundation.com>

RUN apt-get update && apt-get install -y \
    python3.4 python3-pip libpq-dev

RUN mkdir -p /opt/sunlightfoundation.com/
ADD . /opt/sunlightfoundation.com/pupa/
RUN pip3 install https://www.djangoproject.com/download/1.7b3/tarball/
RUN pip3 install psycopg2
RUN pip3 install -e /opt/sunlightfoundation.com/pupa/

RUN mkdir -p /tmp/pupa
WORKDIR /tmp/pupa

ENTRYPOINT ["pupa"]
