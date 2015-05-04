FROM python:3.4.3
MAINTAINER Ash Wilson <ash.wilson@rackspace.com>

RUN mkdir -p /usr/src/app /usr/control-repo

COPY . /usr/src/app
RUN pip install /usr/src/app

VOLUME /usr/control-repo
WORKDIR /usr/control-repo

CMD ["deconst-preparer-sphinx"]
