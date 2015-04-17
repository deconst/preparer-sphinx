# -*- coding: utf-8 -*-

import os
from os import path

import requests
from docutils import nodes
from sphinx.builders.html import JSONHTMLBuilder
from sphinx.util import jsonimpl
from deconstrst.config import Configuration


class DeconstJSONBuilder(JSONHTMLBuilder):
    """
    Custom Sphinx builder that generates Deconst-compatible JSON documents.
    """

    implementation = jsonimpl
    name = 'deconst'
    out_suffix = '.json'

    def init(self):
        JSONHTMLBuilder.init(self)

        self.deconst_config = Configuration(os.environ)
        self.should_submit = not self.deconst_config.skip_submit_reasons()

    def finish(self):
        """
        We need to write images and static assets *first*.

        Also, the search indices and so on aren't necessary.
        """

    def dump_context(self, context, filename):
        """
        Override the default serialization code to save a derived metadata
        envelope, instead.
        """

        envelope = {
            "body": context["body"],
            "title": context["title"],
            "layout_key": context["deconst_layout_key"]
        }

        super().dump_context(envelope, filename)

    def handle_page(self, pagename, ctx, *args, **kwargs):
        """
        Override the default serialization code to save a derived metadata
        envelope, instead.
        """

        meta = self.env.metadata[pagename]
        ctx["deconst_layout_key"] = meta.get("deconstlayout", "default")

        super().handle_page(pagename, ctx, *args, **kwargs)

    def post_process_images(self, doctree):
        """
        Publish images to the content store. Modify the image reference with
        the
        """

        JSONHTMLBuilder.post_process_images(self, doctree)

        if self.should_submit:
            for node in doctree.traverse(nodes.image):
                node['uri'] = self._publish_entry(node['uri'])

    def _publish_entry(self, srcfile):
        # TODO guess the content-type

        url = self.deconst_config.content_store_url + "assets"
        basename = path.basename(srcfile)
        files = {basename: open(srcfile, 'rb')}

        response = requests.post(url, files=files)
        response.raise_for_status()
        return response.json()[basename]
