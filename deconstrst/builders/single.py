# -*- coding: utf-8 -*-

import os
import mimetypes
import json
from os import path

import requests
from docutils import nodes
from docutils.io import DocTreeInput, StringOutput
from sphinx.builders.html import SingleFileHTMLBuilder
from sphinx.builders.html import JSONHTMLBuilder
from sphinx.util import jsonimpl
from sphinx.util.osutil import os_path, relative_uri
from sphinx.util.console import bold, darkgreen, brown
from sphinx.writers.html import HTMLWriter
from sphinx.config import Config
from deconstrst.config import Configuration
from pprint import pprint

# Tell Sphinx about the deconst_default_layout key.
Config.config_values["deconst_default_layout"] = ("default", "html")


class DeconstSingleJSONBuilder(SingleFileHTMLBuilder):
    """
    Custom Sphinx builder that generates Deconst-compatible JSON documents.
    """

    name = 'deconst-single'

    def init(self):
        SingleFileHTMLBuilder.init(self)

        self.deconst_config = Configuration(os.environ)

        if os.path.exists("_deconst.json"):
            with open("_deconst.json", "r") as cf:
                self.deconst_config.apply_file(cf)

        self.should_submit = not self.deconst_config.skip_submit_reasons()

    def write(self, *ignored):
        docnames = self.env.all_docs

        self.info(bold('preparing documents... '), nonl=True)
        self.prepare_writing(docnames)
        self.info('done')

        self.info(bold('assembling single document... '), nonl=True)
        doctree = self.assemble_doctree()
        doctree.settings = self.docsettings

        self.env.toc_secnumbers = self.assemble_toc_secnumbers()
        self.secnumbers = self.env.toc_secnumbers.get(self.config.master_doc, {})
        self.fignumbers = self.env.toc_fignumbers.get(self.config.master_doc, {})
        self.imgpath = relative_uri(self.get_target_uri(self.config.master_doc), '_images')
        self.dlpath = relative_uri(self.get_target_uri(self.config.master_doc), '_downloads')
        self.current_docname = self.config.master_doc

        if self.should_submit:
            self.post_process_images(doctree)

        meta = self.env.metadata.get(self.config.master_doc)

        title = self.env.longtitles.get(self.config.master_doc)
        toc = self.env.get_toctree_for(self.config.master_doc, self, False)

        rendered_title = self.render_partial(title)['title']
        rendered_body = self.render_partial(doctree)['fragment']
        rendered_toc = self.render_partial(toc)['fragment']

        envelope = {
            "title": meta.get('deconsttitle', rendered_title),
            "body": rendered_body,
            "toc": rendered_toc,
            "layout_key": meta.get('deconstlayout', self.config.deconst_default_layout),
            "meta": dict(meta)
        }

        outfile = os.path.join(self.outdir, self.config.master_doc + '.json')

        with open(outfile, 'w') as dumpfile:
            json.dump({"envelope": envelope}, dumpfile)

    def finish(self):
        """
        Nothing to see here
        """


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
            payload = (basename, open(srcfile, 'rb'), content_type)
        else:
            payload = open(srcfile, 'rb')
        files = {basename: payload}

        response = requests.post(url, files=files, headers=headers)
        response.raise_for_status()
        return response.json()[basename]