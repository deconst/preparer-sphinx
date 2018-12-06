# -*- coding: utf-8 -*-

import sys
import os

from deconstrst.builders.serial import DeconstSerialJSONBuilder
from deconstrst.builders.single import DeconstSingleJSONBuilder
from sphinx.application import Sphinx

DEFAULT_BUILDER = 'deconst-serial'


def build(srcdir, destdir):
    """
    Invoke Sphinx with locked arguments to generate JSON content.
    """

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


def builder_init_handler(app: Sphinx):
    """builder_init_handler reports initialization of a builder.

    Arguments:
        app {Sphinx} -- the instance of the applicaiton
    """
    print('{} successfully initialized.'.format(app.builder))


def setup(app: Sphinx):
    app.connect('builder-inited', builder_init_handler)
    app.setup_extension('sphinx.builders.html')
    app.add_builder(DeconstSerialJSONBuilder)
    app.add_builder(DeconstSingleJSONBuilder)
    return {}
