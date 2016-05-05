#!/usr/bin/env python

import json
import os
import io
import sys
import datadiff
import traceback
from os import path
from shutil import rmtree
from contextlib import redirect_stdout, redirect_stderr
from termcolor import colored, cprint

sys.path.append(path.join(path.dirname(__file__), '..'))

import deconstrst

TESTCASE_ROOT = path.dirname(__file__)

# Potential outcomes

PENDING = object()
OK = object()
FAIL = object()
ERROR = object()

class Testcase:
    """
    A single pair of input and expected output directories.
    """

    def __init__(self, root):
        self.root = root

        self.src_root = path.join(root, 'src')
        self.expected_root = path.join(root, 'dest')
        self.expected_envelope_root = path.join(self.expected_root, 'envelopes')
        self.expected_asset_root = path.join(self.expected_root, 'assets')

        scratch_dir = os.environ.get('SCRATCH_DIR', os.getcwd())
        self.actual_root = path.join(scratch_dir, 'preparer-test-{}'.format(self.name()))
        self.actual_envelope_root = path.join(self.actual_root, 'envelopes')
        self.actual_asset_root = path.join(self.actual_root, 'assets')

        self.outcome = PENDING
        self.stacktrace = ''
        self.envelope_diff = None
        self.asset_diff = None
        self.output = ''

    def name(self):
        return path.basename(self.root)

    def run(self):

        os.environ['CONTENT_ROOT'] = self.src_root
        os.environ['ENVELOPE_DIR'] = self.actual_envelope_root
        os.environ['ASSET_ROOT'] = self.expected_envelope_root

        capture = io.StringIO()
        with redirect_stderr(capture):
            with redirect_stdout(capture):
                try:
                    deconstrst.main()
                    if self.compare():
                        self.outcome = OK
                        rmtree(self.actual_root)
                    else:
                        self.outcome = FAIL
                except BaseException as e:
                    self.outcome = ERROR
                    self.stacktrace = traceback.format_exc(sys.exc_info())
        self.output = capture.getvalue()

    def compare(self):
        expected_envelopes = self.envelope_set_from(self.expected_envelope_root)
        expected_assets = self.asset_set_from(self.expected_asset_root)

        actual_envelopes = self.envelope_set_from(self.actual_envelope_root)
        actual_assets = self.asset_set_from(self.actual_asset_root)

        self.envelope_diff = datadiff.diff(actual_envelopes, expected_envelopes)
        self.asset_diff = datadiff.diff(actual_assets, expected_assets)

        return not self.envelope_diff and not self.asset_diff

    def envelope_set_from(self, root):
        envelopes = {}
        for dirpath, dirnames, filenames in os.walk(root):
            for filename in filenames:
                fullpath = path.join(dirpath, filename)
                try:
                    with open(fullpath, 'r') as ef:
                        envelopes[filename] = json.load(ef)
                except (OSError, json.JSONDecoderError):
                    pass
        return envelopes

    def asset_set_from(self, root):
        assets = []
        for dirpath, dirnames, filenames in os.walk(root):
            for filename in filenames:
                fullpath = path.join(dirpath, filename)
                relpath = path.relpath(fullpath, root)
                assets.append(relpath)
        return assets

    def report(self):
        report = io.StringIO()
        header, output, diff, stacktrace = False, False, False, False

        if self.outcome is FAIL:
            header, diff = True, True
        elif self.outcome is ERROR:
            header, output, stacktrace = True, True, True

        if header:
            report.write('\n')
            report.write(colored('== Report [{}]'.format(self.name()), attrs=['reverse']))
            report.write('\n')

        if output:
            report.write(colored('>> stdout and stderr\n', 'cyan'))
            report.write(self.output)

        if diff:
            report.write(colored('>> diff\n', 'cyan'))
            report.write(self.envelope_diff.stringify())
            report.write(self.asset_diff.stringify())

        if stacktrace:
            report.write(colored('>> stacktrace\n', 'cyan'))
            report.write(self.stacktrace)

        return report.getvalue()


testcases = []
for entry in os.scandir(TESTCASE_ROOT):
    if entry.is_dir():
        testcases.append(Testcase(entry.path))

s = 's'
if len(testcases) == 1:
    s = ''
summary = '{} testcase{} discovered.'.format(len(testcases), s)
cprint(summary, attrs=['bold'])

for testcase in testcases:
    cprint('{} .. '.format(testcase.name()), 'cyan', end='')

    testcase.run()

    if testcase.outcome is OK:
        cprint('ok', 'green')
    elif testcase.outcome is FAIL:
        cprint('fail', 'red')
    elif testcase.outcome is ERROR:
        cprint('error', 'red')

r = join([t.report() for t in testcases], '\n')

if any(t.outcome is not OK for t in testcases):
    sys.exit(1)
