# -*- coding: utf-8 -*-

import io

from nose.tools import assert_equal, assert_not_in

from submitter.asset import Asset, AssetSet
from submitter.envelope import Envelope

class TestEnvelope():

    def test_construct(self):
        data = io.StringIO('''{
            "title": "aaa",
            "body": "<p>This is an envelope</p>"
        }''')
        e = Envelope('https%3A%2F%2Fgithub.com%2Forg%2Frepo%2Fpage.json', data)

        assert_equal(e.encoded_content_id(), 'https%3A%2F%2Fgithub.com%2Forg%2Frepo%2Fpage')
        assert_equal(e.content_id(), 'https://github.com/org/repo/page')
        assert_equal(e.document, {
            'title': 'aaa',
            'body': '<p>This is an envelope</p>'
        })

    def test_apply_offsets(self):
        a0 = Asset('local/one.jpg', io.BytesIO())
        a1 = Asset('local/two.gif', io.BytesIO())
        a2 = Asset('local/three.png', io.BytesIO())
        asset_set = AssetSet()
        asset_set.append(a0)
        asset_set.append(a1)
        asset_set.append(a2)

        asset_set.accept_urls({
            'local/one.jpg': 'https://assets.horse/one-111.jpg',
            'local/two.gif': 'https://assets.horse/two-222.gif',
            'local/three.png': 'https://assets.horse/three-333.png'
        })

        data = io.StringIO('''{
            "title": "envelope with asset references",
            "body": "<p>Hey everyone here X are X some assets X</p>",
            "asset_offsets": {
                "local/one.jpg": [21, 41],
                "local/three.png": [27]
            }
        }''')
        e = Envelope('https%3A%2F%2Fgithub.com%2Forg%2Frepo%2Fpage.json', data)

        e.apply_asset_offsets(asset_set)

        assert_not_in('asset_offsets', e.document)
        assert_equal(e.document['body'], '<p>Hey everyone here ' \
            'https://assets.horse/one-111.jpg are ' \
            'https://assets.horse/three-333.png some ' \
            'assets https://assets.horse/one-111.jpg</p>')
