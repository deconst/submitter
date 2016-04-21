# -*- coding: utf-8 -*-

from betamax import Betamax
from requests import Session
from nose.tools import assert_is_not_none, assert_equal, assert_true

from . import URL, APIKEY
from submitter.content_service import ContentService
from submitter.submit import submit_assets

class TestSubmit():

    def setup(self):
        session = Session()
        self.betamax = Betamax(session)
        self.cs = ContentService(url=URL, apikey=APIKEY, session=session)

    def test_submit_assets(self):
        with self.betamax.use_cassette('test_submit_assets'):
            asset_set = submit_assets('test/fixtures/assets', self.cs)

            aaa, bbb = None, None
            for asset in asset_set.all():
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
