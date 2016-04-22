# -*- coding: utf-8 -*-

import io
import json
import os
import tarfile
from os.path import join, relpath

from .asset import Asset, AssetSet
from .envelope import Envelope, EnvelopeSet

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
    asset_set.accept_urls(check_result)

    asset_archive = io.BytesIO()
    tf = tarfile.open(fileobj=asset_archive, mode='w:gz')
    for asset in asset_set.to_upload():
        fullpath = join(directory, asset.localpath)
        tf.add(fullpath, arcname=asset.localpath)
    tf.close()

    upload_result = content_service.bulkasset(asset_archive.getvalue())
    asset_set.accept_urls(upload_result)

    return asset_set

def submit_envelopes(config, directory, asset_set, content_service):
    """
    Enumerate metadata envelopes within "directory". Inject asset public URLs
    into each, then compute a fingerprint based on a stable representation
    of the modified JSON documents. Query the content service to determine
    which envelopes are already present on the content service. Construct
    a tarball containing the rest and perform a bulk upload of the missing
    envelopes.
    """

    envelope_set = EnvelopeSet()

    for entry in os.scandir(directory):
        if entry.is_dir():
            # TODO Output a warning
            continue

        if not entry.name.endswith(".json"):
            continue

        with open(entry.path, 'r') as ef:
            envelope = Envelope(entry.path, ef)
            envelope_set.append(envelope)

    envelope_set.apply_asset_offsets(asset_set)

    check_response = content_service.checkcontent(envelope_set.fingerprint_query())
    envelope_set.accept_presence(check_response)

    envelope_archive = io.BytesIO()
    tf = tarfile.open(fileobj=envelope_archive, mode='w:gz')

    # Metadata entry: metadata/config.json
    config = { 'contentIDBase': config.content_id_base }
    config_data = json.dumps(config).encode('utf-8')
    config_entry = tarfile.TarInfo('metadata/config.json')
    config_entry.size = len(config_data)
    tf.addfile(config_entry, io.BytesIO(config_data))

    # Metadata entry: metadata/keep.json
    keep = { 'keep': [e.content_id() for e in envelope_set.to_keep()] }
    keep_data = json.dumps(keep).encode('utf-8')
    keep_entry = tarfile.TarInfo('metadata/keep.json')
    keep_entry.size = len(keep_data)
    tf.addfile(keep_entry, io.BytesIO(keep_data))

    # Uploaded envelopes themselves
    for envelope in envelope_set.to_upload():
        envelope_path = relpath(envelope.fname, directory)
        envelope_entry = tarfile.TarInfo(envelope_path)
        envelope_buffer = envelope.serialize().encode('utf-8')
        envelope_entry.size = len(envelope_buffer)
        tf.addfile(envelope_entry, io.BytesIO(envelope_buffer))

    tf.close()

    upload_response = content_service.bulkcontent(envelope_archive.getvalue())
    failed = upload_response['failed']
    if failed > 0:
        raise Exception('Failed to upload {} envelopes.'.format(failed))

    return envelope_set
