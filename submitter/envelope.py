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
        self.body = json.load(stream)

    def encoded_content_id(self):
        return splitext(basename(self.fname))[0]

    def content_id(self):
        return unquote(self.encoded_content_id())
