# -*- coding: utf-8 -*-

import io

from nose.tools import assert_equal, assert_is, assert_is_none, assert_false, \
    assert_true, assert_in, assert_not_in
from submitter.asset import Asset, AssetSet

class TestAsset():

    def setup(self):
        self.data = io.BytesIO(b'this is totally a jpg')

    def test_fingerprint(self):
        asset = Asset('local/image.jpg', self.data)

        # echo -n "this is totally a jpg" | shasum -a 256
        assert_equal(asset.fingerprint, '0ce34a6ca011d365236867577a770a038a91b0474057d275689e51ed6c1affa1')

    def test_public_url(self):
        asset = Asset('local/image.jpg', self.data)
        assert_is_none(asset.public_url)
        assert_true(asset.needs_upload())

        asset.accept_url({
            'local/image.jpg': 'https://cdn.horse/image-0ce34a6c.jpg'
        })

        assert_false(asset.needs_upload())
        assert_equal(asset.public_url, 'https://cdn.horse/image-0ce34a6c.jpg')

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

    def test_to_upload(self):
        asset_set = AssetSet()
        asset_set.append(self.asset0)
        asset_set.append(self.asset1)

        asset_set.accept_urls({
            'local/image.jpg': 'https://cdn.horse/image-0ce34a6c.jpg',
            'kittens.gif': None
        })

        to_upload = [a for a in asset_set.to_upload()]
        assert_not_in(self.asset0, to_upload)
        assert_in(self.asset1, to_upload)
