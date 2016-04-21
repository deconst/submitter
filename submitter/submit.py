# -*- coding: utf-8 -*-

import io
import os
import tarfile
from os.path import join, relpath

from .asset import Asset, AssetSet

def submit_assets(directory, content_service):
    """
    Recursively discover each asset file beneath "directory". Check the
    content service API to determine which assets need to be uploaded.
    Construct a tarball containing those assets and upload them. Return the
    generated AssetSet.
    """

    asset_set = AssetSet()

    for root, dirs, files in os.walk(directory):
        for fname in files:
            fullpath = join(root, fname)
            localpath = relpath(fullpath, directory)
            with open(fullpath, 'rb') as af:
                asset = Asset(localpath, af)
                asset_set.append(asset)

    check_result = content_service.checkassets(asset_set.fingerprint_query())
    asset_set.accept_check(check_result)

    asset_archive = io.BytesIO()
    tf = tarfile.open(fileobj=asset_archive, mode='w:gz')
    for asset in asset_set.to_upload():
        fullpath = join(directory, asset.localpath)
        tf.add(fullpath, arcname=asset.localpath)
    tf.close()

    asset_result = content_service.bulkasset(asset_archive.getvalue())
    return asset_set
