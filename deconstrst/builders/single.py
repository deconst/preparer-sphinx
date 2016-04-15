# -*- coding: utf-8 -*-

import os
import re
import mimetypes
import json
from os import path
import glob
import urllib.parse

import requests
from docutils import nodes
from sphinx.builders.html import SingleFileHTMLBuilder
from sphinx.util.osutil import relative_uri
from sphinx.util.console import bold
from docutils.io import StringOutput
from deconstrst.config import Configuration
from .writer import OffsetHTMLTranslator


class DeconstSingleJSONBuilder(SingleFileHTMLBuilder):
    """
    Custom Sphinx builder that generates Deconst-compatible JSON documents.
    """

    name = 'deconst-single'

    def init(self):
        SingleFileHTMLBuilder.init(self)

        self.translator_class = OffsetHTMLTranslator

        self.deconst_config = Configuration(os.environ)

        if os.path.exists("_deconst.json"):
            with open("_deconst.json", "r", encoding="utf-8") as cf:
                self.deconst_config.apply_file(cf)

        try:
            self.git_root = self.deconst_config.get_git_root(os.getcwd())
        except FileNotFoundError:
            self.git_root = None

        self.should_submit = not self.deconst_config.skip_submit_reasons()

    def fix_refuris(self, tree):
        """
        The parent implementation of this includes the base file name, which
        breaks if we serve with a trailing slash. We just want what's between
        the last "#" and the end of the string
        """

        # fix refuris with double anchor
        for refnode in tree.traverse(nodes.reference):
            if 'refuri' not in refnode:
                continue
            refuri = refnode['refuri']
            hashindex = refuri.rfind('#')
            if hashindex < 0:
                continue

            # Leave absolute URLs alone
            if re.match("^https?://", refuri):
                continue

            refnode['refuri'] = refuri[hashindex:]

    def write(self, *ignored):
        docnames = self.env.all_docs

        self.info(bold('preparing documents... '), nonl=True)
        self.prepare_writing(docnames)
        self.info('done')

        self.info(bold('assembling single document... '), nonl=True)
        doctree = self.assemble_doctree()
        doctree.settings = self.docsettings

        self.env.toc_secnumbers = self.assemble_toc_secnumbers()
        self.secnumbers = self.env.toc_secnumbers.get(self.config.master_doc,
                                                      {})
        self.fignumbers = self.env.toc_fignumbers.get(self.config.master_doc,
                                                      {})

        target_uri = self.get_target_uri(self.config.master_doc)
        self.imgpath = relative_uri(target_uri, '_images')
        self.dlpath = relative_uri(target_uri, '_downloads')
        self.current_docname = self.config.master_doc

        if self.should_submit:
            self.post_process_images(doctree)

        # Merge this page's metadata with the repo-wide data.
        meta = self.deconst_config.meta.copy()
        meta.update(self.env.metadata.get(self.config.master_doc))

        title = self.env.longtitles.get(self.config.master_doc)
        toc = self.env.get_toctree_for(self.config.master_doc, self, False)

        self.fix_refuris(toc)

        rendered_title = self.render_partial(title)['title']
        rendered_toc = self.render_partial(toc)['fragment']
        layout_key = meta.get('deconstlayout',
                              self.config.deconst_default_layout)

        unsearchable = meta.get('deconstunsearchable',
                                self.config.deconst_default_unsearchable)
        if unsearchable is not None:
            unsearchable = unsearchable in ("true", True)

        rendered_body = self.write_body(doctree)

        if self.git_root != None and hasattr(self.deconst_config, "github_url"):
            # current_page_name has no extension, and it _might_ not be .rst
            fileglob = path.join(
                os.getcwd(), self.env.srcdir, self.config.master_doc + ".*"
            )

            edit_segments = [
                self.deconst_config.github_url,
                "edit",
                self.deconst_config.github_branch,
                path.relpath(glob.glob(fileglob)[0], self.git_root)
            ]

            meta["github_edit_url"] = '/'.join(segment.strip('/') for segment in edit_segments)

        envelope = {
            "title": meta.get('deconsttitle', rendered_title),
            "body": rendered_body,
            "toc": rendered_toc,
            "layout_key": layout_key,
            "meta": dict(meta)
        }

        if unsearchable is not None:
            envelope["unsearchable"] = unsearchable

        page_cats = meta.get('deconstcategories')
        global_cats = self.config.deconst_categories
        if page_cats is not None or global_cats is not None:
            cats = set()
            if page_cats is not None:
                cats.update(re.split("\s*,\s*", page_cats))
            cats.update(global_cats or [])
            envelope["categories"] = list(cats)

        if self.should_submit:
            outfile = os.path.join(self.outdir, self.config.master_doc + '.json')
        else:
            envelope["asset_offsets"] = self.docwriter.visitor.calculate_offsets()

            content_id = self.deconst_config.content_id_base
            if content_id.endswith('/'):
                content_id = content_id[:-1]
            envelope_filename = urllib.parse.quote(content_id, safe='') + '.json'
            outfile = os.path.join(self.deconst_config.envelope_dir, envelope_filename)

        with open(outfile, 'w', encoding="utf-8") as dumpfile:
            json.dump(envelope, dumpfile)

    def write_body(self, doctree):
        destination = StringOutput(encoding='utf-8')
        doctree.settings = self.docsettings

        self.docwriter.write(doctree, destination)
        self.docwriter.assemble_parts()

        return self.docwriter.parts['fragment']

    def finish(self):
        """
        Nothing to see here
        """

    def post_process_images(self, doctree):
        """
        Publish images to the content store. Modify the image reference with
        the
        """

        SingleFileHTMLBuilder.post_process_images(self, doctree)

        if self.should_submit:
            for node in doctree.traverse(nodes.image):
                node['uri'] = self._publish_entry(node['uri'])

    def _publish_entry(self, srcfile):
        (content_type, _) = mimetypes.guess_type(srcfile)

        auth = 'deconst apikey="{}"'.format(
            self.deconst_config.content_store_apikey)
        headers = {"Authorization": auth}
        verify = self.deconst_config.tls_verify

        url = self.deconst_config.content_store_url + "assets"
        basename = path.basename(srcfile)
        if content_type:
            payload = (basename, open(srcfile, 'rb'), content_type)
        else:
            payload = open(srcfile, 'rb')
        files = {basename: payload}

        response = requests.post(url, files=files, headers=headers,
                                 verify=verify)
        response.raise_for_status()
        return response.json()[basename]
