# -*- coding: utf-8 -*-

import argparse
import os
import sys

from deconstrst.deconstrst import build, submit

__author__ = 'Ash Wilson'
__email__ = 'ash.wilson@rackspace.com'
__version__ = '0.1.0'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--submit",
                        help="Submit results to the content store.",
                        action="store_true")

    args = parser.parse_args()
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
            for var, meaning in missing.items():
                print("  {}\t{}".format(var, meaning), file=sys.stderr)
            sys.exit(1)
        else:
            if not content_store_url.endswith("/"):
                content_store_url += "/"

            if not content_id_base.endswith("/"):
                content_id_base += "/"

    # Lock source and destination to the same paths as the Makefile.
    srcdir, destdir = '.', '_build/deconst'

    status = build(srcdir, destdir)

    if status != 0 or not args.submit:
        sys.exit(status)

    submit(destdir, content_store_url, content_id_base)


if __name__ == '__main__':
    main()
