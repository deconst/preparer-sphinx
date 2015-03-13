# -*- coding: utf-8 -*-

import sys
from os import path

from builder import DeconstJSONBuilder
from sphinx.application import Sphinx
from sphinx.builders import BUILTIN_BUILDERS


def build(argv):
    """
    Invoke Sphinx with locked arguments to generate JSON content.
    """

    # I am a terrible person
    BUILTIN_BUILDERS['deconst'] = DeconstJSONBuilder

    # Lock source and destination to the same paths as the Makefile.
    srcdir, destdir = '.', '_build/deconst'

    doctreedir = path.join(destdir, '.doctrees')

    app = Sphinx(srcdir=srcdir, confdir=srcdir, outdir=destdir,
                 doctreedir=doctreedir, buildername="deconst",
                 confoverrides={}, status=sys.stdout, warning=sys.stderr,
                 freshenv=True, warningiserror=False, tags=[], verbosity=0,
                 parallel=1)
    app.build(True, [])
    return app.statuscode
