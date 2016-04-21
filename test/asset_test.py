# -*- coding: utf-8 -*-

import io

from nose.tools import assert_equal
from submitter.asset import Asset

class TestAsset():

    def test_fingerprint(self):
        data = io.BytesIO(b'this is totally a jpg')
        asset = Asset('local/image.jpg', data)

        # echo -n "this is totally a jpg" | shasum -a 256
        assert_equal(asset.fingerprint, '0ce34a6ca011d365236867577a770a038a91b0474057d275689e51ed6c1affa1')
