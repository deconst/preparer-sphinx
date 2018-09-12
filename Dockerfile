FROM alpine:3.8
LABEL author Ash Wilson @smashwilson

# Alpine python3 now includes pip
RUN apk add --no-cache --update --virtual .build-deps build-base python3-dev && \
    apk add --no-cache --update git python3
RUN if [[ ! -e /usr/bin/pip ]]; then ln -s /usr/bin/pip3 /usr/bin/pip ; fi && \
    if [[ ! -e /usr/bin/python ]]; then ln -s /usr/bin/python3 /usr/bin/python; fi

RUN adduser -D -g "" -u 1000 preparer
RUN mkdir -p /preparer /venv /usr/content-repo
RUN chown -R preparer:preparer /preparer /venv
ENV PYTHONPATH /preparer

USER preparer
RUN python -m venv /venv
ENV PATH /venv/bin:${PATH}

# Use the version of pip integrated in this release of Alpine
# and don't complain.
RUN mkdir -p $HOME/.config/pip
RUN printf "[global]\ndisable-pip-version-check = True\n" \
  > $HOME/.config/pip/pip.conf

COPY ./requirements.txt /preparer/requirements.txt
RUN python -m pip install --no-cache-dir -r /preparer/requirements.txt
# USER root
# RUN apk del .build-deps
# USER preparer
COPY . /preparer

VOLUME /usr/content-repo
WORKDIR /usr/content-repo

CMD ["python", "-m", "deconstrst"]
