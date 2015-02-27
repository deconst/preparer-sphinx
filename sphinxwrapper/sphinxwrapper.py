# -*- coding: utf-8 -*-

import sys
from os import path

from sphinx.application import Sphinx


def build(argv):
    try:
        srcdir, destdir = argv[1], argv[2]
    except IndexError:
        print("Insufficient arguments.")
        print("Please specify source and destination directories.")
        return 1

    doctreedir = path.join(destdir, '.doctrees')

    app = Sphinx(srcdir=srcdir, confdir=srcdir, outdir=destdir,
                 doctreedir=doctreedir, buildername="json", confoverrides={},
                 status=sys.stdout, warning=sys.stderr, freshenv=True,
                 warningiserror=False, tags=[], verbosity=0, parallel=1)
    app.build(True, [])
    return app.statuscode
