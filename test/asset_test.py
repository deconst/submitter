# -*- coding: utf-8 -*-

import io

from nose.tools import assert_equal, assert_is
from submitter.asset import Asset, AssetSet

class TestAsset():

    def test_fingerprint(self):
        data = io.BytesIO(b'this is totally a jpg')
        asset = Asset('local/image.jpg', data)

        # echo -n "this is totally a jpg" | shasum -a 256
        assert_equal(asset.fingerprint, '0ce34a6ca011d365236867577a770a038a91b0474057d275689e51ed6c1affa1')

class TestAssetSet():

    def setup(self):
        data0 = io.BytesIO(b'this is totally a jpg')
        self.asset0 = Asset('local/image.jpg', data0)

        data1 = io.BytesIO(b'a gif or something I guess')
        self.asset1 = Asset('kittens.gif', data1)

    def test_append(self):
        asset_set = AssetSet()

        asset_set.append(self.asset0)
        assert_equal(len(asset_set), 1)

        asset_set.append(self.asset1)
        assert_equal(len(asset_set), 2)

    def test_fingerprint_query(self):
        asset_set = AssetSet()
        asset_set.append(self.asset0)
        asset_set.append(self.asset1)

        actual_query = asset_set.fingerprint_query()
        expected_query = {
            'local/image.jpg': '0ce34a6ca011d365236867577a770a038a91b0474057d275689e51ed6c1affa1',
            'kittens.gif': '02ed10d61a9efd82184b8b4ebf6f34cffddf0e02ae89b6029e7a4edc7bbdb6ff'
        }
        assert_equal(actual_query, expected_query)
