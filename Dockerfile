FROM python:3.4.3
MAINTAINER Ash Wilson <ash.wilson@rackspace.com>

RUN mkdir -p /usr/src/app /usr/content-repo

COPY . /usr/src/app
RUN pip install /usr/src/app

VOLUME /usr/content-repo
WORKDIR /usr/content-repo

CMD ["deconst-preparer-sphinx"]
