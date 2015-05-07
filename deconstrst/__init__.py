# -*- coding: utf-8 -*-

import os
import sys

from deconstrst.deconstrst import build, submit
from deconstrst.config import Configuration

__author__ = 'Ash Wilson'
__email__ = 'ash.wilson@rackspace.com'
__version__ = '0.1.0'


def main():

    config = Configuration(os.environ)

    # Lock source and destination to the same paths as the Makefile.
    srcdir, destdir = '.', '_build/deconst'

    status = build(srcdir, destdir)
    if status != 0:
        sys.exit(status)

    reasons = config.skip_submit_reasons()
    if reasons:
        print("Not submitting content to the content service because:",
              file=sys.stderr)
        print(file=sys.stderr)
        for reason in reasons:
            print(" * " + reason, file=sys.stderr)
        print(file=sys.stderr)
        return

    submit(destdir,
           config.content_store_url,
           config.content_store_apikey,
           config.content_id_base)


if __name__ == '__main__':
    main()
