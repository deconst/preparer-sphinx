# -*- coding: utf-8 -*-

import sys
import os
import urllib.parse

import requests
from deconstrst.builders.serial import DeconstSerialJSONBuilder
from deconstrst.builders.single import DeconstSingleJSONBuilder
from sphinx.application import Sphinx
from sphinx.builders import BUILTIN_BUILDERS

DEFAULT_BUILDER = 'deconst-serial'


def build(srcdir, destdir):
    """
    Invoke Sphinx with locked arguments to generate JSON content.
    """

    # I am a terrible person
    BUILTIN_BUILDERS['deconst-serial'] = DeconstSerialJSONBuilder
    BUILTIN_BUILDERS['deconst-single'] = DeconstSingleJSONBuilder

    conf_builder = get_conf_builder(srcdir)
    doctreedir = os.path.join(destdir, '.doctrees')

    app = Sphinx(srcdir=srcdir, confdir=srcdir, outdir=destdir,
                 doctreedir=doctreedir, buildername=conf_builder,
                 confoverrides={}, status=sys.stdout, warning=sys.stderr,
                 freshenv=True, warningiserror=False, tags=[], verbosity=0,
                 parallel=1)
    app.build(True, [])

    return app.statuscode

def get_conf_builder(srcdir):
    with open(os.path.join(srcdir, 'conf.py'), encoding="utf-8") as conf_file:
        conf_data = conf_file.read()

    try:
        code = compile(conf_data, 'conf.py', 'exec')
        exec(code)
    except SyntaxError:
        """
        We'll just pretend nothing happened and use the default builder
        """

    return locals().get('builder', DEFAULT_BUILDER)
