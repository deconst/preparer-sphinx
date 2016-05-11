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
from sphinx.util import jsonimpl
from sphinx.util.osutil import relative_uri
from sphinx.util.console import bold
from docutils.io import StringOutput
from deconstrst.config import Configuration
from .envelope import Envelope
from .common import init_builder


class DeconstSingleJSONBuilder(SingleFileHTMLBuilder):
    """
    Custom Sphinx builder that generates Deconst-compatible JSON documents.
    """

    name = 'deconst-single'

    def init(self):
        super().init()
        init_builder(self)

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

    def handle_page(self, pagename, context, **kwargs):
        """
        Override to call write_context.
        """

        context['current_page_name'] = pagename

        titlenode = self.env.longtitles.get(pagename)
        renderedtitle = self.render_partial(titlenode)['title']
        context['title'] = renderedtitle

        self.add_sidebars(pagename, context)
        self.write_context(context)

    def finish(self):
        """
        Nothing to see here
        """

    def write_context(self, context):
        """
        Write a derived metadata envelope to disk.
        """

        docname = context['current_page_name']
        per_page_meta = self.env.metadata[docname]

        local_toc = None
        if context['display_toc']:
            local_toc = context['toc']

        envelope = Envelope(docname=docname,
                            body=context['body'],
                            title=context['title'],
                            toc=local_toc,
                            builder=self,
                            deconst_config=self.deconst_config,
                            per_page_meta=per_page_meta)

        with open(envelope.serialization_path(), 'w', encoding="utf-8") as f:
            jsonimpl.dump(envelope.serialization_payload(), f)
