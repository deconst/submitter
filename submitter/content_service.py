# -*- coding: utf-8 -*-

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

        u = self.base_url + '/checkassets'
        r = self.session.get(u, json=query, headers={
            'Content-Type': 'application/json'
        })
        r.raise_for_status()
        return r.json()

    def bulkasset(self, tarball):
        """
        Bulk-upload a binary buffer containing multiple assets within a
        .tar.gz file.

        https://github.com/deconst/content-service#post-bulkasset
        """

        u = self.base_url + '/bulkasset'
        r = self.session.post(u, data=tarball, headers={
            'Content-Type': 'application/tar+gzip'
        })
        r.raise_for_status()
        return r.json()

    def checkcontent(self, query):
        """
        Query the content service with a map of content IDs and the SHA256
        checksums of their corresponding metadata envelopes.

        https://github.com/deconst/content-service#get-checkcontent
        """

        u = self.base_url + '/checkcontent'
        r = self.session.get(u, json=query, headers={
            'Content-Type': 'application/json'
        })
        r.raise_for_status()
        return r.json()

    def bulkcontent(self, tarball):
        """
        Bulk-upload a binary buffer containing multiple envelopes and
        metadata files within a .tar.gz file.

        https://github.com/deconst/content-service#post-bulkcontent
        """

        u = self.base_url + '/bulkcontent'
        r = self.session.post(u, data=tarball, headers={
            'Content-Type': 'application/tar+gzip'
        })
        r.raise_for_status()
        return r.json()
