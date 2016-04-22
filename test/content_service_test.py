# -*- coding: utf-8 -*-

import os
import io
import tarfile

from betamax import Betamax
from requests import Session
from nose.tools import assert_equal, assert_true, assert_false, assert_in

from . import URL, APIKEY
from submitter.content_service import ContentService

class TestContentService():

    def setup(self):
        session = Session()
        self.betamax = Betamax(session)
        self.cs = ContentService(url=URL, apikey=APIKEY, session=session)

    def test_checkassets(self):
        # curl -X POST -H "Authorization: deconst ${APIKEY}" \
        #   http://dockerdev:9000/assets \
        #   -F aaa=@test/fixtures/assets/foo/aaa.jpg \
        #   -F bbb=@test/fixtures/assets/bar/bbb.gif

        with self.betamax.use_cassette('checkassets'):
            response = self.cs.checkassets({
                'foo/aaa.jpg': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                'bar/bbb.gif': '8810ad581e59f2bc3928b261707a71308f7e139eb04820366dc4d5c18d980225',
                'baz/missing.css': 'ffa63583dfa6706b87d284b86b0d693a161e4840aad2c5cf6b5d27c3b9621f7d'
            })

            assert_equal(response, {
                'foo/aaa.jpg': '/__local_asset__/aaa-e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.jpg',
                'bar/bbb.gif': None,
                'baz/missing.css': None
            })

    def test_bulkasset(self):
        with self.betamax.use_cassette('bulkasset'):
            tarball = io.BytesIO()
            tf = tarfile.open(fileobj=tarball, mode='w:gz')
            add_tar_entry(tf, 'bar/bbb.gif')
            add_tar_entry(tf, 'foo/aaa.jpg')
            tf.close()

            response = self.cs.bulkasset(tarball.getvalue())

            assert_equal(response, {
                'bar/bbb.gif': '/__local_asset__/bbb-e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.gif',
                'foo/aaa.jpg': '/__local_asset__/aaa-e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.jpg'
            })

    def test_checkcontent(self):
        # curl -X PUT -H "Authorization: deconst ${APIKEY}" \
        #   -H 'Content-Type: application/json' \
        #   http://dockerdev:9000/content/https%3A%2F%2Fgithub.com%2Forg%2Frepo%2Fone \
        #   -d '{"title":"one","body":"one"}'

        # echo -n '{"body":"one","title":"one"}' | shasum -a 256

        # curl -X PUT -H "Authorization: deconst ${APIKEY}" \
        #   -H 'Content-Type: application/json' \
        #   http://dockerdev:9000/content/https%3A%2F%2Fgithub.com%2Forg%2Frepo%2Ftwo \
        #   -d '{"title":"two","body":"two"}'

        # echo -n '{"body":"two","title":"two"}' | shasum -a 256

        with self.betamax.use_cassette('checkcontent'):
            response = self.cs.checkcontent({
                'https://github.com/org/repo/one': '842d36ad29589a39fc4be06157c5c204a360f98981fc905c0b2a114662172bd8',
                'https://github.com/org/repo/two': 'f0e62392fc00c71ba3118c91b97c6f2cbfdcd75e8053fe2d9f029ebfcf6c23fe'
            })

            assert_equal(response, {
                'https://github.com/org/repo/one': True,
                'https://github.com/org/repo/two': False
            })

    def test_bulkcontent(self):
        with self.betamax.use_cassette('bulkcontent'):
            tarball = io.BytesIO()
            tf = tarfile.open(fileobj=tarball, mode='w:gz')
            add_tar_entry(
                tf,
                'https%3A%2F%2Fgithub.com%2Forg%2Frepo%2Fone.json',
                b'{"body":"one","title":"one"}')
            add_tar_entry(
                tf,
                'https%3A%2F%2Fgithub.com%2Forg%2Frepo%2Ftwo.json',
                b'{"body":"two","title":"two"}')
            tf.close()

            response = self.cs.bulkcontent(tarball.getvalue())

            assert_equal(response, {
                'accepted': 2,
                'failed': 0,
                'deleted': 0
            })

def add_tar_entry(tf, entryname, buf = b''):
    """
    Add a manually constructed TarInfo to a TarFile.
    """

    entry = tarfile.TarInfo(entryname)
    entry.size = len(buf)
    tf.addfile(entry, io.BytesIO(buf))
