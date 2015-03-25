# -*- coding: utf-8 -*-

import sys
import os
import json

import requests
from deconstrst.builder import DeconstJSONBuilder
from sphinx.application import Sphinx
from sphinx.builders import BUILTIN_BUILDERS


def build(srcdir, destdir):
    """
    Invoke Sphinx with locked arguments to generate JSON content.
    """

    # I am a terrible person
    BUILTIN_BUILDERS['deconst'] = DeconstJSONBuilder

    doctreedir = os.path.join(destdir, '.doctrees')

    app = Sphinx(srcdir=srcdir, confdir=srcdir, outdir=destdir,
                 doctreedir=doctreedir, buildername="deconst",
                 confoverrides={}, status=sys.stdout, warning=sys.stderr,
                 freshenv=True, warningiserror=False, tags=[], verbosity=0,
                 parallel=1)
    app.build(True, [])

    return app.statuscode


def submit(destdir, content_store_url, content_id_base):
    """
    Submit the generated json files to the content store API.
    """

    headers = {
        "Content-Type": "application/json"
    }

    for (dirpath, dirnames, filenames) in os.walk(destdir):
        for name in filenames:
            fullpath = os.path.join(dirpath, name)
            ext = os.path.splitext(name)[1]

            if os.path.isfile(fullpath) and ext == ".json":
                relpath = os.path.relpath(fullpath, destdir)

                print("submitting [{}] ... ".format(relpath), end='')

                payload = dict(id=content_id_base + relpath)

                with open(fullpath, "r") as inf:
                    payload["body"] = json.load(inf)

                response = requests.put(content_store_url + "content",
                                        data=json.dumps(payload),
                                        headers=headers)
                response.raise_for_status()
                print("success")

    print("All generated content submitted to the content store.")

    return 0
