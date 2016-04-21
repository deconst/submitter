# -*- coding: utf-8 -*-

import hashlib

class Asset():
    """
    An asset file discovered beneath ASSET_DIR.
    """

    def __init__(self, localpath, stream):
        self.localpath = localpath
        self.fingerprint = hashlib.sha256(stream.read()).hexdigest()
