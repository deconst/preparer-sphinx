#!/bin/bash

SUDO=sudo

which boot2docker >/dev/null 2>&1 && {
  SUDO=
  CONTENT_STORE_URL=${CONTENT_STORE_URL:-http://$(boot2docker ip):9000/}
}

CONTENT_STORE_URL=${CONTENT_STORE_URL:-http://localhost:9000/}
CONTENT_STORE_APIKEY=${CONTENT_STORE_APIKEY:-"12345"}
WORKDIR=${1:-$(pwd)}

[ -z "${CONTENT_ID_BASE}" ] && {
  cat <<EOM 1>&2
Please specify a content ID base:

  export CONTENT_ID_BASE=https://github.com/myname/myrepo

Our convention is to use the base URL of your GitHub repo.
EOM
  exit 1
}

${SUDO} docker run \
  --rm=true \
  -e CONTENT_STORE_URL=${CONTENT_STORE_URL} \
  -e CONTENT_STORE_APIKEY=${CONTENT_STORE_APIKEY} \
  -e CONTENT_ID_BASE=${CONTENT_ID_BASE} \
  -e TRAVIS_PULL_REQUEST="false" \
  -v ${WORKDIR}:/usr/control-repo \
  quay.io/deconst/preparer-sphinx
