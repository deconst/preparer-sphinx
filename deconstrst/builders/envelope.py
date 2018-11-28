# -*- coding: utf-8 -*-

import os
import urllib
import re
from os import path

from deconstrst.builders.writer import OffsetHTMLTranslator
from deconstrst.builders.common import derive_content_id


class Envelope:
    """
    A metadata envelope-in-waiting.
    """

    def __init__(self, docname, body, title, toc, builder, deconst_config,
                 per_page_meta, docwriter=OffsetHTMLTranslator):
        self.docname = docname

        self.body = body
        self.title = title
        self.toc = toc

        self.content_id = None
        self.unsearchable = None
        self.layout_key = None
        self.categories = None
        self.meta = None
        self.asset_offsets = None

        self.next = None
        self.previous = None
        self.addenda = None

        self.builder = builder
        self.deconst_config = deconst_config
        self.per_page_meta = per_page_meta
        self.docwriter = docwriter

        self._populate_meta()
        self._populate_git()
        self._populate_unsearchable()
        self._populate_layout_key()
        self._populate_categories()
        self._populate_asset_offsets()
        self._populate_content_id()
        self._override_title()

    def set_next(self, n):
        if not n:
            return
        self.next = {'url': n['link'], 'title': n['title']}

    def set_previous(self, p):
        if not p:
            return
        self.previous = {'url': p['link'], 'title': p['title']}

    def add_addenda(self, addenda_name, addenda_content_id):
        if self.addenda is None:
            self.addenda = {}
        self.addenda[addenda_name] = addenda_content_id

    def serialization_path(self):
        """
        Generate the full path at which this envelope should be serialized.
        """

        envelope_filename = urllib.parse.quote(
            self.content_id, safe='') + '.json'
        return path.join(self.deconst_config.envelope_dir, envelope_filename)

    def serialization_payload(self):
        """
        Construct a dict containing the data that should be serialized as part
        of the envelope.
        """

        payload = {'body': self.body}
        if self.title:
            payload['title'] = self.title
        if self.toc:
            payload['toc'] = self.toc

        if self.unsearchable is not None:
            payload['unsearchable'] = self.unsearchable
        if self.layout_key is not None:
            payload['layout_key'] = self.layout_key
        if self.categories is not None:
            payload['categories'] = self.categories
        if self.meta is not None:
            payload['meta'] = self.meta
        if self.asset_offsets is not None:
            payload['asset_offsets'] = self.asset_offsets

        if self.next is not None:
            payload['next'] = self.next
        if self.previous is not None:
            payload['previous'] = self.previous
        if self.addenda is not None:
            payload['addenda'] = self.addenda

        return payload

    def _populate_meta(self):
        """
        Merge repository-global and per-page metadata into the envelope's
        metadata.
        """

        self.meta = self.deconst_config.meta.copy()
        self.meta.update(self.per_page_meta)

    def _populate_git(self):
        """
        Set the github_edit_url property within "meta".
        """

        if self.deconst_config.git_root and self.deconst_config.github_url:
            full_path = path.join(os.getcwd(),
                                  self.builder.env.srcdir,
                                  self.docname
                                  + self.builder.config.source_suffix[0])

            edit_segments = [
                self.deconst_config.github_url,
                'edit',
                self.deconst_config.github_branch,
                path.relpath(full_path, self.builder.env.srcdir)
            ]

            self.meta['github_edit_url'] = '/'.join(
                segment.strip('/') for segment in edit_segments)

    def _populate_unsearchable(self):
        """
        Populate "unsearchable" from per-page or repository-wide settings.
        """

        unsearchable = self.per_page_meta.get(
            'deconstunsearchable',
            self.builder.config.deconst_default_unsearchable)
        if unsearchable is not None:
            self.unsearchable = unsearchable in ('true', True)

    def _populate_layout_key(self):
        """
        Derive the "layout_key" from per-page or repository-wide configuration.
        """

        default_layout = self.builder.config.deconst_default_layout
        self.layout_key = self.per_page_meta.get(
            'deconstlayout', default_layout)

    def _populate_categories(self):
        """
        Unify global and per-page categories.
        """

        page_cats = self.per_page_meta.get('deconstcategories')
        global_cats = self.builder.config.deconst_categories
        if page_cats is not None or global_cats is not None:
            cats = set()
            if page_cats is not None:
                cats.update(re.split("\s*,\s*", page_cats))
            cats.update(global_cats or [])
            self.categories = list(cats)

    def _populate_asset_offsets(self):
        """
        Read stored asset offsets from the docwriter.
        """

        self.asset_offsets = self.docwriter.calculate_offsets(self.docwriter)

    def _populate_content_id(self):
        """
        Derive this envelope's content ID.
        """

        self.content_id = derive_content_id(self.deconst_config, self.docname)

    def _override_title(self):
        """
        Override the envelope's title if requested by page metadata.
        """

        if 'deconsttitle' in self.per_page_meta:
            self.title = self.per_page_meta['deconsttitle']
