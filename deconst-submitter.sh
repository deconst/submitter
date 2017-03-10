#!/bin/bash

set -euo pipefail

ENVELOPE_DIR=${ENVELOPE_DIR:-"$(pwd)/_build/deconst-envelopes"}
ASSET_DIR=${ASSET_DIR:-"$(pwd)/_build/deconst-assets"}
CONTENT_ID_BASE=${CONTENT_ID_BASE:-$(jq -r .contentIDBase _deconst.json)}

exec docker run \
  --rm=true \
  -e CONTENT_SERVICE_APIKEY=${CONTENT_SERVICE_APIKEY:-} \
  -e CONTENT_SERVICE_URL=${CONTENT_SERVICE_URL:-} \
  -e CONTENT_ID_BASE=${CONTENT_ID_BASE} \
  -e VERBOSE=${VERBOSE:-} \
  -e ENVELOPE_DIR=/usr/deconst-envelopes \
  -e ASSET_DIR=/usr/deconst-assets \
  -v ${ENVELOPE_DIR}:/usr/deconst-envelopes \
  -v ${ASSET_DIR}:/usr/deconst-assets \
  quay.io/deconst/submitter
