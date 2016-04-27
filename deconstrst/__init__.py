# -*- coding: utf-8 -*-

import os
import sys

from deconstrst.deconstrst import build, submit, get_conf_builder
from deconstrst.config import Configuration

__author__ = 'Ash Wilson'
__email__ = 'ash.wilson@rackspace.com'
__version__ = '0.1.0'


def main(directory=False):

    config = Configuration(os.environ)

    if config.content_root:
        if directory and directory != config.content_root:
            print("Warning: Overriding CONTENT_ROOT [{}] with argument [{}].".format(config.content_root, directory))
        else:
            os.chdir(config.content_root)
    elif directory:
        os.chdir(directory)

    if os.path.exists("_deconst.json"):
        with open("_deconst.json", "r", encoding="utf-8") as cf:
            config.apply_file(cf)

    # Ensure that the envelope and asset directories exist.
    os.makedirs(config.envelope_dir, exist_ok=True)
    os.makedirs(config.asset_dir, exist_ok=True)

    # Lock source and destination to the same paths as the Makefile.
    srcdir = '.'
    destdir = os.path.join('_build', get_conf_builder(srcdir))

    status = build(srcdir, destdir)
    if status != 0:
        sys.exit(status)

    reasons = config.skip_submit_reasons()
    if reasons:
        print("Not preparing content because:", file=sys.stderr)
        print(file=sys.stderr)
        for reason in reasons:
            print(" * " + reason, file=sys.stderr)
        print(file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
