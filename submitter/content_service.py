# -*- coding: utf-8 -*-

import logging
from datetime import datetime

from requests import Session

class ContentService():
    """
    Perform operations with the content service API.

    https://github.com/deconst/content-service#api
    """

    def __init__(self, url, apikey, session=None):
        self.base_url = url

        self.session = session
        if not self.session:
            self.session = Session()

        self.session.headers.update({
            'Accept': 'application/json',
            'User-Agent': 'submitter/0.0.0',
            'Authorization': 'deconst {}'.format(apikey)
        })

    def checkassets(self, query):
        """
        Query the content service with a map of local asset filenames and their
        SHA256 checksums.

        https://github.com/deconst/content-service#get-checkassets
        """

        logging.debug('Beginning /checkassets request.')
        start = datetime.utcnow()
        u = self.base_url + '/checkassets'
        r = self.session.get(u, json=query, headers={
            'Content-Type': 'application/json'
        })
        r.raise_for_status()
        finish = datetime.utcnow()
        logging.debug('Completed /checkassets request in {}.', finish - start)
        return r.json()

    def bulkasset(self, tarball):
        """
        Bulk-upload a binary buffer containing multiple assets within a
        .tar.gz file.

        https://github.com/deconst/content-service#post-bulkasset
        """

        logging.debug('Beginning /bulkasset request.')
        start = datetime.utcnow()
        u = self.base_url + '/bulkasset'
        r = self.session.post(u, data=tarball, headers={
            'Content-Type': 'application/tar+gzip'
        })
        r.raise_for_status()
        finish = datetime.utcnow()
        logging.debug('Completed /bulkasset request in {}.', finish - start)
        return r.json()

    def checkcontent(self, query):
        """
        Query the content service with a map of content IDs and the SHA256
        checksums of their corresponding metadata envelopes.

        https://github.com/deconst/content-service#get-checkcontent
        """

        logging.debug('Beginning /checkcontent request.')
        start = datetime.utcnow()
        u = self.base_url + '/checkcontent'
        r = self.session.get(u, json=query, headers={
            'Content-Type': 'application/json'
        })
        r.raise_for_status()
        finish = datetime.utcnow()
        logging.debug('Completed /bulkasset request in {}.', finish - start)
        return r.json()

    def bulkcontent(self, tarball):
        """
        Bulk-upload a binary buffer containing multiple envelopes and
        metadata files within a .tar.gz file.

        https://github.com/deconst/content-service#post-bulkcontent
        """

        logging.debug('Beginning /bulkcontent request.')
        start = datetime.utcnow()
        u = self.base_url + '/bulkcontent'
        r = self.session.post(u, data=tarball, headers={
            'Content-Type': 'application/tar+gzip'
        })
        r.raise_for_status()
        finish = datetime.utcnow()
        logging.debug('Completed /bulkasset request in {}.', finish - start)
        return r.json()
