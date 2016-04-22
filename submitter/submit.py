# -*- coding: utf-8 -*-

import io
import json
import os
import tarfile
from os.path import join, relpath

from .asset import Asset, AssetSet
from .envelope import Envelope, EnvelopeSet
from .content_service import ContentService

SUCCESS = 'success'
NOOP = 'noop'
FAILURE = 'failure'

def submit(config, session=None):
    """
    Discover and upload assets, then discover, process, and upload envelopes.
    """

    content_service = ContentService(
        url=config.content_service_url,
        apikey=config.content_service_apikey,
        session=session
    )

    asset_set = submit_assets(config.asset_dir, content_service)
    submit_envelopes(config, config.envelope_dir, asset_set, content_service)


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
    uploaded = 0
    for asset in asset_set.to_upload():
        fullpath = join(directory, asset.localpath)
        tf.add(fullpath, arcname=asset.localpath)
        uploaded += 1
    tf.close()

    upload_result = content_service.bulkasset(asset_archive.getvalue())
    asset_set.accept_urls(upload_result)

    return AssetSubmitResult(
        asset_set=asset_set,
        uploaded=uploaded,
        present=len(asset_set) - uploaded
    )

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
    uploaded = 0
    for envelope in envelope_set.to_upload():
        envelope_path = relpath(envelope.fname, directory)
        envelope_entry = tarfile.TarInfo(envelope_path)
        envelope_buffer = envelope.serialize().encode('utf-8')
        envelope_entry.size = len(envelope_buffer)
        tf.addfile(envelope_entry, io.BytesIO(envelope_buffer))

    tf.close()

    upload_response = content_service.bulkcontent(envelope_archive.getvalue())

    return EnvelopeSubmitResult(
        envelope_set=envelope_set,
        uploaded=upload_response['accepted'],
        present=len(keep['keep']),
        deleted=upload_response['deleted'],
        failed=upload_response['failed']
    )


class AssetSubmitResult():

    def __init__(self, asset_set, uploaded, present):
        self.asset_set = asset_set
        self.uploaded = uploaded
        self.present = present


class EnvelopeSubmitResult():

    def __init__(self, envelope_set, uploaded, present, deleted, failed):
        self.envelope_set = envelope_set
        self.uploaded = uploaded
        self.present = present
        self.deleted = deleted
        self.failed = failed
