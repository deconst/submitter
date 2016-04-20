
from nose.tools import assert_equal
from submitter.config import Config

def test_valid_config():
    c = Config({
        'ENVELOPE_DIR': '/envelopes/',
        'ASSET_DIR': '/assets/',
        'CONTENT_SERVICE_URL': 'http://localhost:9000/',
        'CONTENT_SERVICE_APIKEY': '12341234'
    })

    assert_equal(c.envelope_dir, '/envelopes/')
    assert_equal(c.asset_dir, '/assets/')
    assert_equal(c.content_service_url, 'http://localhost:9000/')
    assert_equal(c.content_service_apikey, '12341234')
