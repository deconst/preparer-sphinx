# -*- coding: utf-8 -*-

import os
import re
import mimetypes
from os import path
import glob
import urllib.parse
import shutil

import requests
from docutils import nodes
from sphinx import addnodes
from sphinx.builders.html import JSONHTMLBuilder
from sphinx.util import jsonimpl
from sphinx.util.osutil import relative_uri
from deconstrst.config import Configuration
from .writer import OffsetHTMLTranslator


TOC_DOCNAME = '_toc'

class DeconstSerialJSONBuilder(JSONHTMLBuilder):
    """
    Custom Sphinx builder that generates Deconst-compatible JSON documents.
    """

    implementation = jsonimpl
    name = 'deconst'
    out_suffix = '.json'

    def init(self):
        JSONHTMLBuilder.init(self)

        self.translator_class = OffsetHTMLTranslator

        self.deconst_config = Configuration(os.environ)

        if os.path.exists("_deconst.json"):
            with open("_deconst.json", "r", encoding="utf-8") as cf:
                self.deconst_config.apply_file(cf)

        try:
            self.git_root = self.deconst_config.get_git_root(os.getcwd())
        except FileNotFoundError:
            self.git_root = None

        self.toc_content_id = self._content_id(TOC_DOCNAME)

    def prepare_writing(self, docnames):
        """
        Emit the global TOC envelope for this content repository.
        """

        super().prepare_writing(docnames)

        toc_envelope = self._toc_envelope()
        if toc_envelope:
            toc_filename = self._envelope_path(self.toc_content_id)
            super().dump_context(toc_envelope, toc_filename)

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

        content_id = self._content_id(context['current_page_name'])

        # Omit the TOC envelope. It's handled in prepare_writing().
        if content_id == self.toc_content_id:
            return

        # Merge this page's metadata with the repo-wide data.
        meta = self.deconst_config.meta.copy()
        meta.update(context['meta'])

        if self.git_root != None and self.deconst_config.github_url != "":
            # current_page_name has no extension, and it _might_ not be .rst
            fileglob = path.join(
                os.getcwd(), context["current_page_name"] + ".*"
            )

            edit_segments = [
                self.deconst_config.github_url,
                "edit",
                self.deconst_config.github_branch,
                path.relpath(glob.glob(fileglob)[0], self.git_root)
            ]

            meta["github_edit_url"] = '/'.join(segment.strip('/') for segment in edit_segments)

        envelope = {
            "body": context["body"],
            "title": context["deconst_title"],
            "layout_key": context["deconst_layout_key"],
            "meta": meta
        }

        if context["deconst_unsearchable"] is not None:
            unsearchable = context["deconst_unsearchable"] in ("true", True)
            envelope["unsearchable"] = unsearchable

        page_cats = context["deconst_categories"]
        global_cats = self.config.deconst_categories
        if page_cats is not None or global_cats is not None:
            cats = set()
            if page_cats is not None:
                cats.update(re.split("\s*,\s*", page_cats))
            cats.update(global_cats or [])
            envelope["categories"] = list(cats)

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

        # Inject asset offsets so the submitter can inject asset URLs.
        envelope["asset_offsets"] = self.docwriter.visitor.calculate_offsets()

        # Write the envelope to ENVELOPE_DIR.
        envelope_path = self._envelope_path(content_id)

        super().dump_context(envelope, envelope_path)

    def handle_page(self, pagename, ctx, *args, **kwargs):
        """
        Override the default serialization code to save a derived metadata
        envelope, instead.
        """

        meta = self.env.metadata[pagename]
        ctx["deconst_layout_key"] = meta.get(
            "deconstlayout", self.config.deconst_default_layout)
        ctx["deconst_title"] = meta.get("deconsttitle", ctx["title"])
        ctx["deconst_categories"] = meta.get("deconstcategories")
        ctx["deconst_unsearchable"] = meta.get(
            "deconstunsearchable", self.config.deconst_default_unsearchable)

        super().handle_page(pagename, ctx, *args, **kwargs)

    def _content_id(self, docname):
        """
        Construct the content ID corresponding to the document produced from a
        docname.
        """

        dirname, basename = path.split(docname)
        if basename == 'index':
            content_id_suffix = dirname
        else:
            content_id_suffix = docname

        content_id = path.join(self.deconst_config.content_id_base, content_id_suffix)
        if content_id.endswith('/'):
            content_id = content_id[:-1]

        return content_id

    def _envelope_path(self, content_id):
        """
        Return the destination path for the metadata envelope with the provided
        content ID.
        """

        envelope_filename = urllib.parse.quote(content_id, safe='') + '.json'
        envelope_path = path.join(self.deconst_config.envelope_dir, envelope_filename)
        return envelope_path

    def _toc_envelope(self):
        """
        Generate an envelope containing the TOC for this content repository.

        If the repository contains a document named "_toc.rst", render its
        entire doctree as the TOC envelope's body. Otherwise, extract the
        toctree from the repository's master document (usually "index.rst"),
        ignore any :hidden: directive arguments, and render it alone.

        URLs within the TOC are replaced with "{{ to('<content-id>') }}"
        expressions. At page presentation time, these are replaced with the
        presented URL of the named envelope based on that envelope's current
        mapping.
        """

        if '_toc' in self.env.found_docs:
            docname = '_toc'
            full_render = True
            includehidden = False
        else:
            docname = self.config.master_doc
            full_render = False
            includehidden = True

        doctree = self.env.get_doctree(docname)

        # Identify toctree nodes from the chosen document
        toctrees = []
        for toctreenode in doctree.traverse(addnodes.toctree):
            toctree = self.env.resolve_toctree(docname, self, toctreenode,
                                               prune=True,
                                               includehidden=includehidden,
                                               maxdepth=0)

            # Rewrite refuris from this resolved toctree
            for refnode in toctree.traverse(nodes.reference):
                if 'refuri' not in refnode:
                    continue

                refstr = refnode['refuri']
                parts = urllib.parse.urlparse(refstr)

                target = "{{ to('" + self._content_id(parts.path) + "') }}"
                if parts.fragment:
                    target += '#' + parts.fragment

                refnode['refuri'] = target

            toctreenode.replace_self(toctree)

            toctrees.append(toctree)

        # No toctree found.
        if not toctrees:
            return

        # Consolidate multiple toctrees
        toctree = toctrees[0]
        for t in toctrees[1:]:
            toctree.extend(t.children)

        # Render either the toctree alone, or the full doctree
        if full_render:
            self.secnumbers = self.env.toc_secnumbers.get(docname, {})
            self.fignumbers = self.env.toc_fignumbers.get(docname, {})
            self.imgpath = relative_uri(self.get_target_uri(docname), '_images')
            self.dlpath = relative_uri(self.get_target_uri(docname), '_downloads')
            self.current_docname = docname

            rendered_toc = self.render_partial(doctree)['body']
        else:
            rendered_toc = self.render_partial(toctree)['body']

        return {
            "unsearchable": True,
            "body": rendered_toc
        }
