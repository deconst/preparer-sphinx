FROM alpine:3.3
MAINTAINER Ash Wilson <ash.wilson@rackspace.com>

RUN apk add --no-cache python3 && \
    apk add --no-cache --virtual=build-dependencies wget ca-certificates && \
    wget "https://bootstrap.pypa.io/get-pip.py" -O /dev/stdout | python3 && \
    apk del build-dependencies

RUN mkdir -p /usr/src/app /usr/content-repo

COPY . /usr/src/app
RUN pip3 install /usr/src/app

VOLUME /usr/content-repo
WORKDIR /usr/content-repo

CMD ["deconst-preparer-sphinx"]
