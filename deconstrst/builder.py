# -*- coding: utf-8 -*-

import os
import mimetypes
from os import path

import requests
from urllib.parse import urljoin
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

        rel_next, rel_previous = None, None
        for rellink in context.get("rellinks"):
            if rellink[2] == "N":
                rel_next = rellink
            elif rellink[2] == "P":
                rel_previous = rellink

        if rel_next:
            envelope["next"] = {
                "contentID": self._content_id_for_docname(rel_next[0]),
                "title": rel_next[1]
            }
        if rel_previous:
            envelope["previous"] = {
                "contentID": self._content_id_for_docname(rel_previous[0]),
                "title": rel_previous[1]
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

    def get_relative_uri(self, from_, to, typ=None):
        """
        Generate a content ID directive that deconst will use to map an href
        to the correct content at presentation-time.
        """

        to_content_id = self._content_id_for_docname(to, typ=None)
        return "{{ to('" + to_content_id + "') }}"

    def _content_id_for_docname(self, docname, typ=None):
        """
        Generate a normalized content ID that corresponds to a Sphinx document
        name.
        """

        base = self.deconst_config.content_id_base
        doc_uri = self.get_target_uri(docname, typ=type)
        doc_content_id = urljoin(base, doc_uri, allow_fragments=True)

        if doc_content_id and doc_content_id[-1] == "/":
            doc_content_id = doc_content_id[:-1]

        return doc_content_id

    def _publish_entry(self, srcfile):
        (content_type, _) = mimetypes.guess_type(srcfile)

        auth = 'deconst apikey="{}"'.format(
            self.deconst_config.content_store_apikey)
        headers = {"Authorization": auth}

        url = self.deconst_config.content_store_url + "assets"
        basename = path.basename(srcfile)
        if content_type:
            payload = (basename, open(srcfile, 'rb'), content_type)
        else:
            payload = open(srcfile, 'rb')
        files = {basename: payload}

        response = requests.post(url, files=files, headers=headers)
        response.raise_for_status()
        return response.json()[basename]
