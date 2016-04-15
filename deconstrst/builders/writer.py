# -*- coding: utf-8 -*-

import shutil
import re
from os import path

from sphinx.writers.html import HTMLTranslator

# Regexp to match the source attribute of an <img> tag that's been generated
# with a placeholder.
RE_SRCATTR = re.compile(r"src\s*=\s*\\\"(X)\\\"")

class OffsetHTMLTranslator(HTMLTranslator):
    """
    Hook Sphinx's HTMLTranslator to track the offsets of image nodes within the
    rendered content.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.asset_offsets = {}

        dc = self.builder.deconst_config
        self.should_submit = not dc.skip_submit_reasons()
        self.asset_src_root = '_images' # This is actually hardcoded in StandaloneHTMLBuilder
        self.asset_dest_root = dc.asset_dir

        self.jsonimpl = self.builder.implementation

    def visit_image(self, node):
        """
        Record the offset for this asset reference.
        """

        if not self.should_submit:
            asset_src_path = node['uri']
            asset_rel_path = path.relpath(asset_src_path, self.asset_src_root)
            asset_dest_path = path.join(self.asset_dest_root, asset_rel_path)

            shutil.copyfile(asset_src_path, asset_dest_path)
            node['uri'] = 'X'

            base_offset = self.current_body_offset()

        super().visit_image(node)

        if not self.should_submit:
            chunk = self.body[-1]
            chunk_match = RE_SRCATTR.search(self.jsonimpl.dumps(chunk))
            if not chunk_match:
                msg = "Unable to find image tag placeholder src attribute within [{}]".format(self.body[-1])
                raise Exception(msg)

            # Account for the starting " prepended by the jsonimpl.dumps call
            chunk_offset = chunk_match.start() - 1
            offset = base_offset + chunk_offset

            print("asset [{}] offset = {}".format(asset_rel_path, offset))
            self.asset_offsets[asset_rel_path] = offset

    def current_body_offset(self):
        """
        Calculate the current character offset within "body".
        """

        # Account for preamble material.
        # See docutils.writers.html4css1.HTMLTranslator.astext
        content = ''.join(self.head_prefix + self.head + self.stylesheet
            + self.body_prefix + self.body_pre_docinfo + self.docinfo
            + self.body)
        return len(self.jsonimpl.dumps(content)) - 2
