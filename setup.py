#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.md') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

with open('requirements.txt') as requirements_file:
    requirements = requirements_file.read().split("\n")

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='deconstrst',
    version='0.1.0',
    description="Build sphinx documentation to JSON and jam it in the cloud",
    long_description=readme + '\n\n' + history,
    author="Ash Wilson",
    author_email='ash.wilson@rackspace.com',
    url='https://github.com/deconst/preparer-sphinx',
    packages=[
        'deconstrst',
    ],
    package_dir={'deconstrst':
                 'deconstrst'},
    include_package_data=True,
    install_requires=requirements,
    license="Apache 2",
    zip_safe=False,
    keywords='deconstrst',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    entry_points={
        'console_scripts': [
            'deconst-prepare-rst = deconstrst:main'
        ],
    },
    test_suite='tests',
    tests_require=test_requirements
)
