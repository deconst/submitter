# -*- coding: utf-8 -*-

import io

from betamax import Betamax
from requests import Session
from nose.tools import assert_is_not_none, assert_equal, assert_true

from . import URL, APIKEY
from submitter.config import Config
from submitter.asset import AssetSet, Asset
from submitter.content_service import ContentService
from submitter.submit import submit, submit_assets, submit_envelopes, \
    SUCCESS

CONFIG = Config({
    'ENVELOPE_DIR': 'test/fixtures/envelopes/',
    'ASSET_DIR': 'test/fixtures/assets/',
    'CONTENT_SERVICE_URL': URL,
    'CONTENT_SERVICE_APIKEY': APIKEY,
    'CONTENT_ID_BASE': 'https://github.com/org/repo/'
})

class TestSubmit():

    def setup(self):
        self.session = Session()
        self.betamax = Betamax(self.session)
        self.cs = ContentService(url=URL, apikey=APIKEY, session=self.session)

        assert_true(CONFIG.is_valid())

    def test_submit_assets(self):
        with self.betamax.use_cassette('test_submit_assets'):
            result = submit_assets('test/fixtures/assets', self.cs)

            assert_equal(result.uploaded, 2)
            assert_equal(result.present, 0)

            aaa, bbb = None, None
            for asset in result.asset_set.all():
                if asset.localpath == 'foo/aaa.jpg':
                    aaa = asset
                elif asset.localpath == 'bar/bbb.gif':
                    bbb = asset
                else:
                    assert_true(False, 'Unrecognized asset: {}'.format(asset.localpath))

            assert_is_not_none(aaa)
            assert_is_not_none(bbb)

            assert_equal(aaa.public_url, '/__local_asset__/aaa-e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.jpg')
            assert_equal(bbb.public_url, '/__local_asset__/bbb-e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.gif')

    def test_submit_envelopes(self):
        with self.betamax.use_cassette('test_submit_envelopes'):
            asset_set = AssetSet()
            asset_set.append(Asset('foo/aaa.jpg', io.BytesIO()))
            asset_set.append(Asset('bar/bbb.gif', io.BytesIO()))

            asset_set.accept_urls({
                'foo/aaa.jpg': '/__local_asset__/aaa-e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.jpg',
                'bar/bbb.gif': '/__local_asset__/bbb-e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.gif'
            })

            result = submit_envelopes(CONFIG, 'test/fixtures/envelopes', asset_set, self.cs)

            assert_equal(result.uploaded, 3)
            assert_equal(result.present, 0)
            assert_equal(result.failed, 0)

            one, two, three = None, None, None
            for envelope in result.envelope_set.all():
                if envelope.content_id() == 'https://github.com/org/repo/one':
                    one = envelope
                elif envelope.content_id() == 'https://github.com/org/repo/two':
                    two = envelope
                elif envelope.content_id() == 'https://github.com/org/repo/three':
                    three = envelope
                else:
                    assert_true(False, 'Unrecognized envelope: {}'.format(envelope.content_id()))

            assert_is_not_none(one)
            assert_is_not_none(two)
            assert_is_not_none(three)

    def test_submit_success(self):
        # Record this one with an empty content service.
        with self.betamax.use_cassette('test_submit_success'):
            result = submit(CONFIG, self.session)

            assert_equal(result.asset_result.uploaded, 2)
            assert_equal(result.asset_result.present, 0)
            assert_equal(result.envelope_result.uploaded, 3)
            assert_equal(result.envelope_result.present, 0)
            assert_equal(result.envelope_result.deleted, 0)
            assert_equal(result.envelope_result.failed, 0)
            assert_equal(result.state, SUCCESS)
