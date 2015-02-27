#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

with open('requirements.txt') as requirements_file:
    requirements = requirements_file.read().split("\n")

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='sphinxwrapper',
    version='0.1.0',
    description="Build sphinx documentation to JSON and jam it in the cloud",
    long_description=readme + '\n\n' + history,
    author="Ash Wilson",
    author_email='ash.wilson@rackspace.com',
    url='https://github.com/smashwilson/sphinxwrapper',
    packages=[
        'sphinxwrapper',
    ],
    package_dir={'sphinxwrapper':
                 'sphinxwrapper'},
    include_package_data=True,
    install_requires=requirements,
    license="BSD",
    zip_safe=False,
    keywords='sphinxwrapper',
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
            'sphinxwrapper-build = sphinxwrapper:main'
        ],
    },
    test_suite='tests',
    tests_require=test_requirements
)
