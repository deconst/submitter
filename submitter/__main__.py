#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import sys
from datetime import datetime

from .config import Config
from .submit import submit

c = Config(os.environ)

if c.verbose:
    level=logging.DEBUG
else:
    level=logging.INFO
logging.basicConfig(format='%(message)s', level=level)
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

sys.exit(1)
