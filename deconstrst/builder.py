# -*- coding: utf-8 -*-

import os
from os import path

import requests
from docutils import nodes
from sphinx.builders.html import JSONHTMLBuilder
from sphinx.util import jsonimpl
from deconstrst.config import Configuration


class DeconstJSONImpl:
    """
    Enhance the default JSON encoder by adding additional keys.
    """

    def dump(self, obj, fp, *args, **kwargs):
        self._enhance(obj)
        return jsonimpl.dump(obj, fp, *args, **kwargs)

    def dumps(self, obj, *args, **kwargs):
        self._enhance(obj)
        return jsonimpl.dumps(obj, *args, **kwargs)

    def load(self, *args, **kwargs):
        return jsonimpl.load(*args, **kwargs)

    def loads(self, *args, **kwargs):
        return jsonimpl.loads(*args, **kwargs)

    def _enhance(self, obj):
        """
        Add additional properties to "obj" to get them into the JSON.
        """

        obj["hello"] = "Sup"


class DeconstJSONBuilder(JSONHTMLBuilder):
    """
    Custom Sphinx builder that generates Deconst-compatible JSON documents.
    """

    implementation = DeconstJSONImpl()
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
