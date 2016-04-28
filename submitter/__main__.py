#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import sys
from datetime import datetime

from .config import Config
from .submit import submit, SUCCESS, NOOP

c = Config(os.environ)

# Configure the logger.
# <= INFO to stdout
# >= WARNING to stderr

class LessThanFilter(logging.Filter):
    def __init__(self, exclusive_maximum):
        super().__init__('')
        self.exclusive_maximum = exclusive_maximum

    def filter(self, record):
        if record.levelno < self.exclusive_maximum:
            return 1
        else:
            return 0

if c.verbose:
    level=logging.DEBUG
else:
    level=logging.INFO

rootLogger = logging.getLogger()
rootLogger.setLevel(level)

plainFormatter = logging.Formatter('%(message)s')

outHandler = logging.StreamHandler(sys.stdout)
outHandler.setLevel(logging.DEBUG)
outHandler.addFilter(LessThanFilter(logging.WARNING))
outHandler.setFormatter(plainFormatter)
rootLogger.addHandler(outHandler)

errHandler = logging.StreamHandler(sys.stderr)
errHandler.setLevel(logging.WARNING)
errHandler.setFormatter(plainFormatter)
rootLogger.addHandler(errHandler)

# Squelch requests and urllib messages.
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

if not c.is_valid():
    logging.error('Invalid configuration. Missing the following environment variables:')
    for var in c.missing():
        logging.error("  " + var)
    sys.exit(1)

start = datetime.utcnow()
result = submit(c)
finish = datetime.utcnow()

pattern = 'Submitted {asset_uploaded} / {asset_total} assets and ' \
    '{envelope_uploaded} / {envelope_total} envelopes in {duration}.'
summary = pattern.format(
    asset_uploaded=result.asset_result.uploaded,
    asset_total=len(result.asset_result.asset_set),
    envelope_uploaded=result.envelope_result.uploaded,
    envelope_total=len(result.envelope_result.envelope_set),
    duration=finish - start
)
logging.info(summary)

if result.state is SUCCESS:
    sys.exit(0)
elif result.state is NOOP:
    # Signal to the Strider plugin that we did nothing.
    sys.exit(2)
else:
    # FAILURE
    logging.error('Failed to upload {} envelopes.'.format(result.envelope_result.failed))
    sys.exit(1)
