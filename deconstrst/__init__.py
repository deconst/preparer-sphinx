# -*- coding: utf-8 -*-

import os
import sys

from pip import pip
from deconstrst.deconstrst import build, get_conf_builder
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

    # Install pip requirements when possible.
    install_requirements()

    # Lock source and destination to the same paths as the Makefile.
    srcdir = '.'
    destdir = os.path.join('_build', get_conf_builder(srcdir))

    status = build(srcdir, destdir)
    if status != 0:
        sys.exit(status)

    reasons = config.missing_values()
    if reasons:
        print("Not preparing content because:", file=sys.stderr)
        print(file=sys.stderr)
        for reason in reasons:
            print(" * " + reason, file=sys.stderr)
        print(file=sys.stderr)
        sys.exit(1)

def install_requirements():
    """
    Install non-colliding dependencies from a "requirements.txt" file found at
    the content root.
    """

    if not os.path.exists('requirements.txt'):
        return

    dependencies = []

    with open('requirements.txt', 'r', encoding='utf-8') as rf:
        for line in rf:
            if line.startswith('#'):
                continue

            stripped = line.strip()
            if not stripped:
                continue

            dependencies.append(stripped)

    print("Installing dependencies: {}.".format(', '.join(dependencies)))
    pip.main(['install', '--quiet'] + dependencies)

if __name__ == '__main__':
    main()
