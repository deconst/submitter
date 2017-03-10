# Submitter

.jpg / .css / .json :point_right: content service

[![Docker Repository on Quay.io](https://quay.io/repository/deconst/submitter/status "Docker Repository on Quay.io")](https://quay.io/repository/deconst/submitter) [![Build Status](https://travis-ci.org/deconst/submitter.svg?branch=master)](https://travis-ci.org/deconst/submitter)

Submit prepared JSON documents to the content service.

## Running locally

To run the submitter locally, you'll need to install:

 * [Docker](https://docs.docker.com/installation/#installation) for your platform.
 * [jq](https://stedolan.github.io/jq/download/) for your platform.

Once you have Docker set up, export any desired configuration variables below and run `deconst-submitter.sh`.

```bash
./deconst-submitter.sh
```

This script is easiest to run within a content repo as then you only need to set `CONTENT_SERVICE_APIKEY` and `CONTENT_SERVICE_URL`.

### Configuration

These environment variables must all be specified.

* `ENVELOPE_DIR` A flat directory containing a collection of metadata envelopes in files named with the pattern `<url-encoded-content-ID>.json`.
* `ASSET_DIR` Root of a directory tree containing assets to be uploaded.
* `CONTENT_SERVICE_URL` Root URL of the content service.
* `CONTENT_SERVICE_APIKEY` Valid API key for the content service, issued by an administrator.
* `CONTENT_ID_BASE` Content ID prefix common to the envelopes found in the envelope directory.

These are optional.

* `VERBOSE` Set to a non-empty value to enable debugging output. *default: false*
* `ASSET_BATCH_SIZE` Suggested archive size, in bytes, to be uploaded to the content service in a single transaction. *default: 30MB*
