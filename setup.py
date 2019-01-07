from setuptools import setup
import os


def get_dependencies():
    """
    Install non-colliding dependencies from a "requirements.txt" file found at
    the content root.
    """

    reqfile = None
    if os.path.exists('deconst-requirements.txt'):
        reqfile = 'deconst-requirements.txt'
    elif os.path.exists('requirements.txt'):
        reqfile = 'requirements.txt'
    else:
        return

    dependencies = []

    with open(reqfile, 'r', encoding='utf-8') as rf:
        for line in rf:
            if line.startswith('#'):
                continue

            stripped = line.strip()
            if not stripped:
                continue

            dependencies.append(stripped)
    return dependencies


setup(
    name='deconstrst',
    author='Patrick Kirchhoff',
    author_email='patrick.kirchhoff@rackspace.co.uk',
    description='A sphinx extension.',
    # Package info
    packages=['deconstrst', 'deconstrst.builders'],
    install_requires=get_dependencies(),
    entry_points={
        'sphinx.builders': [
            'deconst-serial = builders.serial:DeconstSerialJSONBuilder',
            'deconst-single = builders.single:DeconstSingleJSONBuilder',
        ]
    }
)
