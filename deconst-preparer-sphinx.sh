#!/bin/bash

set -euo pipefail

CONTENT_ROOT=${1:-$(pwd)}

exec docker run \
  --rm=true \
  -e CONTENT_ID_BASE=${CONTENT_ID_BASE:-} \
  -e ENVELOPE_DIR=${ENVELOPE_DIR:-} \
  -e ASSET_DIR=${ASSET_DIR:-} \
  -e VERBOSE=${VERBOSE:-} \
  -v ${CONTENT_ROOT}:/usr/content-repo \
  quay.io/deconst/preparer-sphinx
