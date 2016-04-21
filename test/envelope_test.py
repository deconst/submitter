# -*- coding: utf-8 -*-

import io

from nose.tools import assert_equal

from submitter.envelope import Envelope

class TestEnvelope():

    def test_construct(self):
        data = io.StringIO(r'''{
            "title": "aaa",
            "body": "<p>This is an envelope</p>"
        }''')
        e = Envelope('https%3A%2F%2Fgithub.com%2Forg%2Frepo%2Fpage.json', data)

        assert_equal(e.encoded_content_id(), 'https%3A%2F%2Fgithub.com%2Forg%2Frepo%2Fpage')
        assert_equal(e.content_id(), 'https://github.com/org/repo/page')
        assert_equal(e.body, {
            'title': 'aaa',
            'body': '<p>This is an envelope</p>'
        })
