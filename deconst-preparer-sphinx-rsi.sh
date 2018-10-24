#!/bin/bash

set -euo pipefail

CONTENT_ROOT=${1:-$(pwd)}
CONTENT_ID_BASE=${CONTENT_ID_BASE:-$(jq -r .contentIDBase ${CONTENT_ROOT}/_deconst.json)}
ENVELOPE_DIR=${ENVELOPE_DIR:-"${CONTENT_ROOT}/_build/deconst-envelopes"} && mkdir -p ${ENVELOPE_DIR}
ASSET_DIR=${ASSET_DIR:-"${CONTENT_ROOT}/_build/deconst-assets"} && mkdir -p ${ASSET_DIR}

echo "CONTENT_ROOT: ${CONTENT_ROOT}"
echo "CONTENT_ID_BASE: ${CONTENT_ID_BASE}"
echo "ENVELOPE_DIR: ${ENVELOPE_DIR}"
echo "ASSET_DIR: ${ASSET_DIR}"

exec docker run \
  --rm=true \
  -e CONTENT_ID_BASE=${CONTENT_ID_BASE:-} \
  -e ENVELOPE_DIR=${ENVELOPE_DIR:-} \
  -e ASSET_DIR=${ASSET_DIR:-} \
  -e VERBOSE=${VERBOSE:-} \
  -v ${CONTENT_ROOT}:/usr/content-repo \
  docker-registry-default.devapps.rsi.rackspace.net/deconst-cicd/preparer-sphynx:latest
