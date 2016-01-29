FROM alpine:3.3
MAINTAINER Ash Wilson <ash.wilson@rackspace.com>

RUN apk add --no-cache python3 && \
    apk add --no-cache --virtual=build-dependencies wget ca-certificates && \
    wget "https://bootstrap.pypa.io/get-pip.py" -O /dev/stdout | python3 && \
    apk del build-dependencies

RUN pip install --upgrade pip

RUN adduser -D -g "" -u 1000 preparer
RUN mkdir -p /usr/src/app /venv /usr/content-repo
RUN chown -R preparer:preparer /usr/src/app /venv

USER preparer

RUN pyvenv /venv
ENV PATH /venv/bin:${PATH}

COPY . /usr/src/app
RUN pip install /usr/src/app

VOLUME /usr/content-repo
WORKDIR /usr/content-repo

CMD ["deconst-preparer-sphinx"]
