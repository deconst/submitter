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

    def __len__(self):
        return len(self.assets)
