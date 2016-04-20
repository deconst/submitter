
from nose.tools import assert_equal, assert_true, assert_false, assert_in
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

    assert_true(c.is_valid())
    assert_equal(c.missing(), [])

def test_missing_value():
    c = Config({
        'ENVELOPE_DIR': '/envelopes/',
        'ASSET_DIR': '',
        'CONTENT_SERVICE_URL': 'http://localhost:9000/'
    })

    assert_false(c.is_valid())
    assert_in('ASSET_DIR', c.missing())
    assert_in('CONTENT_SERVICE_APIKEY', c.missing())
