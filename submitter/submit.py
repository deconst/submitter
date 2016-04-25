# -*- coding: utf-8 -*-

import io
import json
import os
import tarfile
import logging
from datetime import datetime
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

    asset_result = submit_assets(
        config.asset_dir,
        config.asset_batch_size,
        content_service
    )
    envelope_result = submit_envelopes(
        config.envelope_dir,
        asset_result.asset_set,
        config.content_id_base,
        content_service
    )

    if envelope_result.failed != 0:
        state = FAILURE
    elif envelope_result.uploaded == 0:
        state = NOOP
    else:
        state = SUCCESS

    return SubmitResult(asset_result, envelope_result, state)


def submit_assets(directory, batch_size, content_service):
    """
    Recursively discover each asset file beneath "directory". Check the
    content service API to determine which assets need to be uploaded.
    Construct a tarball containing those assets and upload them. Return the
    generated AssetSet.
    """

    asset_set = AssetSet()

    logging.debug('Discovering and fingerprinting asset files within {}.'.format(directory))
    ts = datetime.utcnow()
    for root, dirs, files in os.walk(directory):
        for fname in files:
            fullpath = join(root, fname)
            localpath = relpath(fullpath, directory)
            with open(fullpath, 'rb') as af:
                asset = Asset(localpath, af)
                asset_set.append(asset)
    logging.debug('Discovered {} asset files in {}.'.format(len(asset_set), datetime.utcnow() - ts))

    check_result = content_service.checkassets(asset_set.fingerprint_query())
    asset_set.accept_urls(check_result)

    uploaded, batches = 0, 0
    while not asset_set.all_public():
        batches += 1

        logging.debug('Creating asset tarball for batch {}.'.format(batches))
        ts = datetime.utcnow()
        asset_archive = io.BytesIO()
        tf = tarfile.open(fileobj=asset_archive, mode='w:gz')
        for asset in asset_set.to_upload():
            fullpath = join(directory, asset.localpath)
            entry = tf.gettarinfo(fullpath, arcname=asset.localpath)

            with open(fullpath, 'rb') as af:
                tf.addfile(entry, fileobj=af)
            uploaded += 1

            if tf.offset > batch_size:
                break
        tf.close()
        logging.debug('Created {}-byte tarball containing {} assets for batch {} in {}.'.format(
            tf.offset,
            uploaded,
            batches,
            datetime.utcnow() - ts
        ))

        upload_result = content_service.bulkasset(asset_archive.getvalue())
        asset_set.accept_urls(upload_result)

    return AssetSubmitResult(
        asset_set=asset_set,
        uploaded=uploaded,
        present=len(asset_set) - uploaded,
        batches=batches
    )

def submit_envelopes(directory, asset_set, content_id_base, content_service):
    """
    Enumerate metadata envelopes within "directory". Inject asset public URLs
    into each, then compute a fingerprint based on a stable representation
    of the modified JSON documents. Query the content service to determine
    which envelopes are already present on the content service. Construct
    a tarball containing the rest and perform a bulk upload of the missing
    envelopes.
    """

    envelope_set = EnvelopeSet()

    logging.debug('Discovering and parsing envelopes within {}.'.format(directory))
    ts = datetime.utcnow()
    for entry in os.scandir(directory):
        if entry.is_dir():
            # TODO Output a warning
            continue

        if not entry.name.endswith(".json"):
            continue

        with open(entry.path, 'r') as ef:
            envelope = Envelope(entry.path, ef)
            envelope_set.append(envelope)
    logging.debug('Discovered {} envelopes in {}.'.format(len(envelope_set), datetime.utcnow() - ts))

    envelope_set.apply_asset_offsets(asset_set)

    check_response = content_service.checkcontent(envelope_set.fingerprint_query())
    envelope_set.accept_presence(check_response)

    logging.debug('Creating envelope tarball.')
    envelope_archive = io.BytesIO()
    tf = tarfile.open(fileobj=envelope_archive, mode='w:gz')

    # Metadata entry: metadata/config.json
    config = { 'contentIDBase': content_id_base }
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
    logging.debug('Created tarball containing {} envelopes in {}.'.format(uploaded, datetime.utcnow() - ts))

    upload_response = content_service.bulkcontent(envelope_archive.getvalue())

    return EnvelopeSubmitResult(
        envelope_set=envelope_set,
        uploaded=upload_response['accepted'],
        present=len(keep['keep']),
        deleted=upload_response['deleted'],
        failed=upload_response['failed']
    )


class AssetSubmitResult():

    def __init__(self, asset_set, uploaded, present, batches):
        self.asset_set = asset_set
        self.uploaded = uploaded
        self.present = present
        self.batches = batches


class EnvelopeSubmitResult():

    def __init__(self, envelope_set, uploaded, present, deleted, failed):
        self.envelope_set = envelope_set
        self.uploaded = uploaded
        self.present = present
        self.deleted = deleted
        self.failed = failed

class SubmitResult():

    def __init__(self, asset_result, envelope_result, state):
        self.asset_result = asset_result
        self.envelope_result = envelope_result
        self.state = state
