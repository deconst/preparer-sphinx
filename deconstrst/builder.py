# -*- coding: utf-8 -*-

import os
import mimetypes
from os import path

import requests
from docutils import nodes
from sphinx.builders.html import JSONHTMLBuilder
from sphinx.util import jsonimpl
from sphinx.config import Config
from deconstrst.config import Configuration

# Tell Sphinx about the deconst_default_layout key.
Config.config_values["deconst_default_layout"] = ("default", "html")


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

        if os.path.exists("_deconst.json"):
            with open("_deconst.json", "r") as cf:
                self.deconst_config.apply_file(cf)

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
            "title": context["deconst_title"],
            "layout_key": context["deconst_layout_key"]
        }

        n = context.get("next")
        p = context.get("prev")

        if n:
            envelope["next"] = {
                "url": n["link"],
                "title": n["title"]
            }
        if p:
            envelope["previous"] = {
                "url": p["link"],
                "title": p["title"]
            }

        if context["display_toc"]:
            envelope["toc"] = context["toc"]

        super().dump_context(envelope, filename)

    def handle_page(self, pagename, ctx, *args, **kwargs):
        """
        Override the default serialization code to save a derived metadata
        envelope, instead.
        """

        meta = self.env.metadata[pagename]
        ctx["deconst_layout_key"] = meta.get(
            "deconstlayout", self.config.deconst_default_layout)
        ctx["deconst_title"] = meta.get("deconsttitle", ctx["title"])

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
        (content_type, _) = mimetypes.guess_type(srcfile)

        auth = 'deconst apikey="{}"'.format(
            self.deconst_config.content_store_apikey)
        headers = {"Authorization": auth}

        url = self.deconst_config.content_store_url + "assets"
        basename = path.basename(srcfile)
        if content_type:
            payload = (basename, open(srcfile, 'rb'), content_type, {})
        else:
            payload = open(srcfile, 'rb')
        files = {basename: payload}

        response = requests.post(url, files=files, headers=headers)
        response.raise_for_status()
        return response.json()[basename]
