# -*- coding: utf-8 -*-

from nose.tools import assert_equal, assert_true, assert_false, assert_in
from submitter.config import Config

def test_valid_config():
    c = Config({
        'ENVELOPE_DIR': '/envelopes/',
        'ASSET_DIR': '/assets/',
        'CONTENT_SERVICE_URL': 'http://localhost:9000',
        'CONTENT_SERVICE_APIKEY': '12341234',
        'CONTENT_ID_BASE': 'https://github.com/org/repo/',
        'VERBOSE': 'true'
    })

    assert_equal(c.envelope_dir, '/envelopes/')
    assert_equal(c.asset_dir, '/assets/')
    assert_equal(c.content_service_url, 'http://localhost:9000')
    assert_equal(c.content_service_apikey, '12341234')
    assert_equal(c.content_id_base, 'https://github.com/org/repo/')
    assert_true(c.verbose)

    assert_true(c.is_valid())
    assert_equal(c.missing(), [])

def test_missing_value():
    c = Config({
        'ENVELOPE_DIR': '/envelopes/',
        'ASSET_DIR': '',
        'CONTENT_SERVICE_URL': 'http://localhost:9000/',
        'CONTENT_ID_BASE': 'https://github.com/org/repo/'
    })

    assert_false(c.is_valid())
    assert_in('ASSET_DIR', c.missing())
    assert_in('CONTENT_SERVICE_APIKEY', c.missing())

def test_normalize_url():
    c = Config({
        'ENVELOPE_DIR': '/envelopes/',
        'ASSET_DIR': '/assets/',
        'CONTENT_SERVICE_APIKEY': '12341234',
        'CONTENT_SERVICE_URL': 'http://with.trailing.slash:9000/',
        'CONTENT_ID_BASE': 'https://github.com/org/repo/'
    })

    assert_equal(c.content_service_url, 'http://with.trailing.slash:9000')

def test_normalize_id_base():
    c = Config({
        'ENVELOPE_DIR': '/envelopes/',
        'ASSET_DIR': '/assets/',
        'CONTENT_SERVICE_APIKEY': '12341234',
        'CONTENT_SERVICE_URL': 'http://localhost:9000',
        'CONTENT_ID_BASE': 'https://github.com/org/repo'
    })

    assert_equal(c.content_id_base, 'https://github.com/org/repo/')

def test_verbose_defaults_to_false():
    c = Config({
        'ENVELOPE_DIR': '/envelopes/',
        'ASSET_DIR': '/assets/',
        'CONTENT_SERVICE_APIKEY': '12341234',
        'CONTENT_SERVICE_URL': 'http://localhost:9000',
        'CONTENT_ID_BASE': 'https://github.com/org/repo'
    })

    assert_false(c.verbose)
