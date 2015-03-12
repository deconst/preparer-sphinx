# -*- coding: utf-8 -*-

import argparse
import sys
from os import path, getenv, unsetenv

from builder import DeconstJSONBuilder
from sphinx.application import Sphinx
from sphinx.builders import BUILTIN_BUILDERS


def yankenv(key):
    """
    Remove an environment variable from the environment and return the value it
    had.
    """

    v = getenv(key)
    unsetenv(key)
    return v


def build(argv):
    """
    Invoke Sphinx with locked arguments to generate JSON content.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("source", help="Source directory.")
    parser.add_argument("destination", help="Destination directory.")
    parser.add_argument("-p", "--publish",
                        help="Publish the rendered content to Cloud Files.",
                        action="store_true")

    parser.parse_args(argv)

    # Read and unset environment variables.
    region = yankenv("OS_REGION")
    username = yankenv("OS_USERNAME")
    api_key = yankenv("OS_API_KEY")

    # I am a terrible person
    BUILTIN_BUILDERS['deconst'] = DeconstJSONBuilder

    doctreedir = path.join(parser.destination, '.doctrees')

    app = Sphinx(srcdir=parser.source, confdir=parser.source,
                 outdir=parser.destination, doctreedir=doctreedir,
                 buildername="deconst", confoverrides={}, status=sys.stdout,
                 warning=sys.stderr, freshenv=True, warningiserror=False,
                 tags=[], verbosity=0, parallel=1)
    app.build(True, [])
    return app.statuscode
