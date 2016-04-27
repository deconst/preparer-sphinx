# -*- coding: utf-8 -*-

import shutil
import re
import os
from os import path
from collections import defaultdict

from sphinx.writers.html import HTMLTranslator

# Regexp to match the source attribute of an <img> tag that's been generated
# with a placeholder.
RE_SRCATTR = re.compile(r"src\s*=\s*\"(X)\"")

class OffsetHTMLTranslator(HTMLTranslator):
    """
    Hook Sphinx's HTMLTranslator to track the offsets of image nodes within the
    rendered content.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.asset_offsets = defaultdict(list)

        dc = self.builder.deconst_config
        self.asset_src_root = path.realpath('_images') # This is actually hardcoded in StandaloneHTMLBuilder
        self.asset_dest_root = path.realpath(dc.asset_dir)

    def visit_image(self, node):
        """
        Record the offset for this asset reference.
        """

        asset_src_path = path.realpath(node['uri'])
        if asset_src_path.startswith(self.asset_src_root):
            asset_rel_path = path.relpath(asset_src_path, self.asset_src_root)
        else:
            asset_rel_path = path.relpath(asset_src_path)
        asset_dest_path = path.join(self.asset_dest_root, asset_rel_path)

        os.makedirs(path.dirname(asset_dest_path), exist_ok=True)
        shutil.copyfile(asset_src_path, asset_dest_path)
        node['uri'] = 'X'

        super().visit_image(node)

        chunk = self.body[-1]
        chunk_match = RE_SRCATTR.search(chunk)
        if not chunk_match:
            msg = "Unable to find image tag placeholder src attribute within [{}]".format(self.body[-1])
            raise Exception(msg)

        chunk_index = len(self.body) - 1
        chunk_offset = chunk_match.start(1)

        self.asset_offsets[asset_rel_path].append(AssetOffset(chunk_index, chunk_offset))

    def calculate_offsets(self):
        """
        Use the final translator state to compute body offsets for all assets.
        """

        if not self.asset_offsets:
            return {}

        total = 0

        chunk_offsets = []
        for chunk in self.body:
            chunk_offsets.append(total)
            total += len(chunk)

        results = {}
        for (asset_rel_path, asset_offsets) in self.asset_offsets.items():
            offsets = [chunk_offsets[o.chunk_index] + o.chunk_offset for o in asset_offsets]
            results[asset_rel_path] = offsets
        return results

class AssetOffset:
    """
    Store the location of an asset URL reference within the document.
    """

    def __init__(self, chunk_index, chunk_offset):
        self.chunk_index = chunk_index
        self.chunk_offset = chunk_offset
