# -*- coding: utf-8 -*-

from __future__ import print_function

import argparse
import sys
import os

from builder import DeconstJSONBuilder
from sphinx.application import Sphinx
from sphinx.builders import BUILTIN_BUILDERS


def build(argv):
    """
    Invoke Sphinx with locked arguments to generate JSON content.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--submit",
                        help="Submit results to the content store.",
                        action="store_true")

    args = parser.parse_args(argv[1:])
    content_store_url = os.getenv("CONTENT_STORE")

    if args.submit and not content_store_url:
        print("Please set CONTENT_STORE if submitting results.",
              file=sys.stderr)
        sys.exit(1)

    # I am a terrible person
    BUILTIN_BUILDERS['deconst'] = DeconstJSONBuilder

    # Lock source and destination to the same paths as the Makefile.
    srcdir, destdir = '.', '_build/deconst'

    doctreedir = os.path.join(destdir, '.doctrees')

    app = Sphinx(srcdir=srcdir, confdir=srcdir, outdir=destdir,
                 doctreedir=doctreedir, buildername="deconst",
                 confoverrides={}, status=sys.stdout, warning=sys.stderr,
                 freshenv=True, warningiserror=False, tags=[], verbosity=0,
                 parallel=1)
    app.build(True, [])

    if app.statuscode != 0 or not args.submit:
        return app.statuscode

    if not content_store_url.endswith("/"):
        content_store_url += "/"

    print("submit active")

    return 0
