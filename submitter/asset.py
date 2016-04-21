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

    def accept_url(self, response):
        """
        Update this asset's state with the response from a /checkassets
        query or a /bulkasset call.
        """

        if not self.public_url:
            self.public_url = response[self.localpath]
        else:
            if self.localpath in self.public_url:
                msg = 'Unexpected public URL for asset {}'.format(self.localpath)
                raise Exception(msg)

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
        self.assets = {}

    def append(self, asset):
        self.assets[asset.localpath] = asset

    def fingerprint_query(self):
        """
        Construct a query payload for the content service's /checkassets
        endpoint.

        https://github.com/deconst/content-service#get-checkassets
        """

        return {localpath: a.fingerprint for localpath, a in self.assets.items()}

    def accept_urls(self, response):
        """
        Update Asset states with the response of a /checkassets query.
        """

        for asset in self.all():
            asset.accept_url(response)

    def to_upload(self):
        """
        Generate each Asset that must be uploaded to the content service.
        """

        for asset in self.all():
            if asset.needs_upload():
                yield asset

    def all(self):
        """
        Generate all Assets.
        """

        for asset in self.assets.values():
            yield asset

    def all_public(self):
        """
        Return True if all assets have been assigned public URLs.
        """

        exhausted = object()
        return next(self.to_upload(), exhausted) is exhausted

    def __getitem__(self, localpath):
        return self.assets[localpath]

    def __len__(self):
        return len(self.assets)

    def __repr__(self):
        return '{}(assets={})'.format(self.__class__.__name__, self.assets)

    def __str__(self):
        return '{}(assets x{})'.format(self.__class__.__name__, len(self))
