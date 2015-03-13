# -*- coding: utf-8 -*-

from __future__ import print_function

import argparse
import sys
import os
import json

import requests
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
    content_store_url = os.getenv("CONTENT_STORE_URL")
    content_id_base = os.getenv("CONTENT_ID_BASE")

    if args.submit:
        missing = {}

        if not content_store_url:
            missing["CONTENT_STORE_URL"] = "Base URL of the content storage " \
                "service."
        if not content_id_base:
            missing["CONTENT_ID_BASE"] = "Base URL used to generate IDs for " \
                "content within this repository."

        if missing:
            print("Required environment variables are missing!",
                  file=sys.stderr)
            for var, meaning in missing.iteritems():
                print("  {}\t{}".format(var, meaning), file=sys.stderr)
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

    os.path.walk(destdir, submit_files, content_store_url)
    print("All generated content submitted to the content store.")

    return 0


def submit_files(content_store_url, dirname, names):
    """
    Submit a directory of generated JSON files to the content store API.
    """

    headers = {
        "Content-Type": "application/json"
    }

    for name in names:
        fullpath = os.path.join(dirname, name)
        if os.path.isfile(fullpath) and os.path.splitext(name)[1] == ".json":
            print("submitting [{}] ... ".format(fullpath), end='')

            payload = dict(id="")

            with open(fullpath, "r") as inf:
                payload["body"] = json.load(inf)

            response = requests.put(content_store_url + "content",
                                    data=json.dumps(payload),
                                    headers=headers)
            response.raise_for_status()
            print("success")
