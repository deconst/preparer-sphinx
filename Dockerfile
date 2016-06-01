FROM alpine:3.3
MAINTAINER Ash Wilson <ash.wilson@rackspace.com>

RUN apk add --no-cache python3 git
RUN python3 -m ensurepip
RUN ln -s /usr/bin/python3 /usr/bin/python && \
  ln -s /usr/bin/pip3 /usr/bin/pip
RUN pip install --upgrade pip

RUN adduser -D -g "" -u 1000 preparer
RUN mkdir -p /preparer /venv /usr/content-repo
RUN chown -R preparer:preparer /preparer /venv
ENV PYTHONPATH /preparer

USER preparer

RUN pyvenv /venv
ENV PATH /venv/bin:${PATH}

COPY ./requirements.txt /preparer/requirements.txt
RUN pip install -r /preparer/requirements.txt
COPY . /preparer

VOLUME /usr/content-repo
WORKDIR /usr/content-repo

CMD ["python", "-m", "deconstrst"]
