# -*- coding: utf-8 -*-

import urllib.parse

from docutils import nodes
from sphinx import addnodes
from sphinx.builders.html import JSONHTMLBuilder
from sphinx.util import jsonimpl
from sphinx.util.osutil import relative_uri
from .common import init_builder, derive_content_id
from .envelope import Envelope
from deconstrst.builders.writer import OffsetHTMLTranslator


TOC_DOCNAME = '_toc'


class DeconstSerialJSONBuilder(JSONHTMLBuilder):
    """
    Custom Sphinx builder that generates Deconst-compatible JSON documents.
    """

    implementation = jsonimpl
    name = 'deconst-serial'
    out_suffix = '.json'
    translator_class = OffsetHTMLTranslator

    def init(self):
        super().init()
        init_builder(self)
        self.toc_envelope = None

    def prepare_writing(self, docnames):
        """
        Emit the global TOC envelope for this content repository.
        """

        super().prepare_writing(docnames)

        self.toc_envelope = self._toc_envelope()
        if self.toc_envelope:
            self.dump_context(self.toc_envelope.serialization_payload(),
                              self.toc_envelope.serialization_path())

    def handle_page(self, pagename, context, **kwargs):
        """
        Override to call write_context.
        """

        context['current_page_name'] = pagename
        self.add_sidebars(pagename, context)
        self.write_context(context)

    def finish(self):
        """
        We need to write images and static assets *first*.

        Also, the search indices and so on aren't necessary.
        """
        self.finish_tasks.add_task(self.copy_image_files)
        self.finish_tasks.add_task(self.copy_download_files)
        # self.finish_tasks.add_task(self.copy_static_files)
        self.finish_tasks.add_task(self.copy_extra_files)
        self.finish_tasks.add_task(self.write_buildinfo)

    def write_context(self, context):
        """
        Override the default serialization code to save a derived metadata
        envelope, instead.
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
        # docwriter=self.docwriter)

        # Omit the TOC envelope. It's handled in prepare_writing().
        # I am not sure the first part of this conditional should
        # be necesarry
        if self.toc_envelope and \
                envelope.content_id == self.toc_envelope.content_id:
            return

        envelope.set_next(context.get('next'))
        envelope.set_previous(context.get('prev'))

        # If this repository has a TOC, reference it as an addenda.
        if self.toc_envelope:
            envelope.add_addenda(
                'repository_toc', self.toc_envelope.content_id)

        self.dump_context(envelope.serialization_payload(),
                          envelope.serialization_path())

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
            toctree = self.env.resolve_toctree(
                self.config.master_doc,
                self,
                toctreenode,
                prune=True,
                includehidden=includehidden,
                maxdepth=0)

            if toctree:
                # Rewrite refuris from this resolved toctree
                for refnode in toctree.traverse(nodes.reference):
                    if 'refuri' not in refnode:
                        continue

                    refstr = refnode['refuri']
                    parts = urllib.parse.urlparse(refstr)

                    if parts.scheme or parts.netloc:
                        # Absolute URL
                        continue

                    # target = "{{ to('"
                    # + derive_content_id(self.deconst_config, parts.path)
                    # + "') }}"
                    target = '{}{}{}'.format(
                        '{{ to(\'',
                        derive_content_id(self.deconst_config, parts.path),
                        '\') }}')
                    if parts.fragment:
                        target += '#' + parts.fragment

                    refnode['refuri'] = target

                toctreenode.replace_self(toctree)

                toctrees.append(toctree)

        # No toctree found.
        if not toctrees:
            return None

        # Consolidate multiple toctrees
        toctree = toctrees[0]
        for t in toctrees[1:]:
            toctree.extend(t.children)

        # Render either the toctree alone, or the full doctree
        if full_render:
            self.secnumbers = self.env.toc_secnumbers.get(docname, {})
            self.fignumbers = self.env.toc_fignumbers.get(docname, {})
            self.imgpath = relative_uri(
                self.get_target_uri(docname), '_images')
            print(f'!!!~~~The image path: {self.imgpath}~~~!!!')
            self.dlpath = relative_uri(
                self.get_target_uri(docname), '_downloads')
            self.current_docname = docname

            rendered_toc = self.render_partial(doctree)['body']
        else:
            # Include the wrapper <div> for consistent markup.
            rendered_toc = self.render_partial(toctree.parent)['body']

        return Envelope(docname=TOC_DOCNAME,
                        body=rendered_toc,
                        title=None,
                        toc=None,
                        builder=self,
                        deconst_config=self.deconst_config,
                        per_page_meta={'deconstunsearchable': True})
        # docwriter=self._publisher.writer)
