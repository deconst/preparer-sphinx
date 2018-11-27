# -*- coding: utf-8 -*-
"""
Code shared between Builder implementations.
"""

import os
from os import path
from deconstrst.config import Configuration


def init_builder(builder):
    """
    Common Builder initialization.
    """

    builder.deconst_config = Configuration(os.environ)

    if path.exists('_deconst.json'):
        with open('_deconst.json', 'r', encoding='utf-8') as cf:
            builder.deconst_config.apply_file(cf)


def derive_content_id(deconst_config, docname):
    """
    Consistently generate content IDs from document names.
    """

    dirname, basename = path.split(docname)
    if basename == 'index':
        content_id_suffix = dirname
    else:
        content_id_suffix = docname

    content_id = path.join(deconst_config.content_id_base, content_id_suffix)
    if content_id.endswith('/'):
        content_id = content_id[:-1]

    return content_id
