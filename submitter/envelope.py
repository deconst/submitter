# -*- coding: utf-8 -*-

import json
from os.path import basename, splitext
from urllib.parse import unquote

class Envelope():
    """
    A metadata envelope, read from disk.
    """

    def __init__(self, fname, stream):
        self.fname = fname
        self.document = json.load(stream)

    def encoded_content_id(self):
        return splitext(basename(self.fname))[0]

    def content_id(self):
        return unquote(self.encoded_content_id())

    def apply_asset_offsets(self, asset_set):
        """
        If this envelope has an "asset_offsets" attribute, replace each
        placeholder character with the asset URL and remove that attribute.
        """

        if 'asset_offsets' not in self.document:
            return

        paths_by_offset = {}
        for localpath, offsets in self.document['asset_offsets'].items():
            for offset in offsets:
                # TODO warn if there are offset collisions
                paths_by_offset[offset] = localpath

        body = self.document['body']
        processed = ''
        last = 0
        for offset in sorted(paths_by_offset.keys()):
            # Append the slice from the end of the last slice to just before
            # this placeholder.
            processed += body[last:offset]

            # Insert the asset URL.
            asset = asset_set[paths_by_offset[offset]]
            processed += asset.public_url

            # Mark the last occurrence.
            last = offset + 1

        # Append the rest of the body.
        processed += body[last:]

        self.document['body'] = processed
        del self.document['asset_offsets']
