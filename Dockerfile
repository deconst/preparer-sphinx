FROM alpine:3.2
MAINTAINER Ash Wilson <ash.wilson@rackspace.com>

RUN apk add --update python3 && rm -rf /var/cache/apk/*
RUN pip3 install --upgrade pip

RUN mkdir -p /usr/src/app /usr/content-repo

COPY . /usr/src/app
RUN pip3 install /usr/src/app

VOLUME /usr/content-repo
WORKDIR /usr/content-repo

CMD ["deconst-preparer-sphinx"]
