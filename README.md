# Submitter

.jpg / .css / .json :point_right: content service

[![Docker Repository on Quay.io](https://quay.io/repository/deconst/submitter/status "Docker Repository on Quay.io")](https://quay.io/repository/deconst/submitter) [![Build Status](https://travis-ci.org/deconst/submitter.svg?branch=master)](https://travis-ci.org/deconst/submitter)

Submit prepared JSON documents to the content service.

### Configuration

These environment variables must all be specified.

* `ENVELOPE_DIR` A flat directory containing a collection of metadata envelopes in files named with the pattern `<url-encoded-content-ID>.json`.
* `ASSET_DIR` Root of a directory tree containing assets to be uploaded.
* `CONTENT_SERVICE_URL` Root URL of the content service.
* `CONTENT_SERVICE_APIKEY` Valid API key for the content service, issued by an administrator.
* `CONTENT_ID_BASE` Content ID prefix common to the envelopes found in the envelope directory.

These are optional.

* `VERBOSE` Set to a non-empty value to enable debugging output. *default: false*
