# -*- coding: utf-8 -*-

import hashlib

class Asset():
    """
    An asset file discovered beneath ASSET_DIR.
    """

    def __init__(self, localpath, stream):
        self.localpath = localpath
        self.fingerprint = hashlib.sha256(stream.read()).hexdigest()

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
