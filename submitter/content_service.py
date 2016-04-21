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

        self.session.auth = ('deconst', apikey)
        self.session.headers.update({
            'Accept': 'application/json',
            'User-Agent': 'submitter/0.0.0'
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
