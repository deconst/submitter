# -*- coding: utf-8 -*-

import os

from betamax import Betamax
from betamax_serializers import pretty_json

URL = os.environ.get('CONTENT_SERVICE_URL', 'http://dockerdev:9000')
APIKEY = os.environ.get('CONTENT_SERVICE_APIKEY', '12341234')

if URL.endswith('/'):
    URL = URL[:-1]

Betamax.register_serializer(pretty_json.PrettyJSONSerializer)
with Betamax.configure() as config:
    config.cassette_library_dir = 'test/fixtures/cassettes'
    config.define_cassette_placeholder('<APIKEY>', APIKEY)
    config.default_cassette_options['serialize_with'] = 'prettyjson'
