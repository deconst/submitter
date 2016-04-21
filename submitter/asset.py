# -*- coding: utf-8 -*-

import hashlib

class Asset():
    """
    An asset file discovered beneath ASSET_DIR.
    """

    def __init__(self, localpath, stream):
        self.localpath = localpath
        self.fingerprint = hashlib.sha256(stream.read()).hexdigest()
        self.public_url = None

    def needs_upload(self):
        """
        Return true if this asset should be included within the asset tarball.
        """

        return self.public_url is None

    def accept_check(self, check_result):
        """
        Update this asset's state with the response from a /checkassets
        query.
        """

        self.public_url = check_result[self.localpath]

    def __repr__(self):
        return '{}(localpath={},fingerprint={},public_url={})'.format(
            self.__class__.__name__,
            self.localpath,
            self.fingerprint,
            self.public_url
        )

    def __str__(self):
        upload_mark = ''
        if self.needs_upload():
            upload_mark = ': *'

        return '{}({}{})'.format(
            self.__class__.__name__,
            self.localpath,
            upload_mark
        )

class AssetSet():
    """
    The collection of all assets discovered within the asset directory.
    """

    def __init__(self):
        self.assets = []

    def append(self, asset):
        self.assets.append(asset)

    def fingerprint_query(self):
        """
        Construct a query payload for the content service's /checkassets
        endpoint.

        https://github.com/deconst/content-service#get-checkassets
        """

        return {a.localpath: a.fingerprint for a in self.assets}

    def accept_check(self, response):
        """
        Update Asset states with the response of a /checkassets query.
        """

        for asset in self.assets:
            asset.accept_check(response)

    def to_upload(self):
        """
        Generate each Asset that must be uploaded to the content service.
        """

        for asset in self.assets:
            if asset.needs_upload():
                yield asset

    def all(self):
        """
        Generate all Assets.
        """

        for asset in self.assets:
            yield asset

    def __len__(self):
        return len(self.assets)

    def __repr__(self):
        return '{}(assets={})'.format(self.__class__.__name__, self.assets)

    def __str__(self):
        return '{}(assets x{})'.format(self.__class__.__name__, len(self))
