# -*- coding: utf-8 -*-

import json
from termcolor import colored


def diff(actual, expected, keypath=[], indent=''):
    tp = type(expected)
    if tp != type(actual):
        return [_unequal(keypath, actual, expected, indent)]

    if tp == list:
        return _diff_lists(actual, expected, keypath, indent)

    if tp == dict:
        return _diff_dicts(actual, expected, keypath, indent)

    if actual == expected:
        return []
    else:
        return [_unequal(keypath, actual, expected, indent)]


def _diff_dicts(actual, expected, keypath=[], indent=''):
    actual_keys = actual.keys()
    expected_keys = expected.keys()

    diffs = []
    for missing in expected_keys - actual_keys:
        diffs.append(_missing(keypath + [missing], expected[missing], indent))

    for extra in actual_keys - expected_keys:
        diffs.append(_extra(keypath + [extra], actual[extra], indent))

    for shared in expected_keys & actual_keys:
        if expected[shared] != actual[shared]:
            diffs += diff(actual[shared], expected[shared],
                          keypath + [shared], indent)

    return diffs


def _diff_lists(actual, expected, keypath=[], indent=''):
    actual_set = set(actual)
    expected_set = set(expected)

    diffs = []
    for missing in expected_set - actual_set:
        diffs.append(colored('- {}'.format(missing), 'red'))

    for extra in actual_set - expected_set:
        diffs.append(colored('+ {}'.format(extra), 'green'))

    return diffs


def _missing(keypath, missing, indent=''):
    hline = _hline('-', keypath, 'red')
    return hline + _body(missing, indent)


def _extra(keypath, extra, indent=''):
    hline = _hline('+', keypath, 'green')
    return hline + _body(extra, indent)


def _unequal(keypath, actual, expected, indent=''):
    hline = _hline('~', keypath, 'magenta')
    actual_body = '\n' + indent + \
        colored('actual:', attrs=['underline']) + _body(actual, indent)
    expected_body = '\n' + indent + \
        colored('expected:', attrs=['underline']) + _body(expected, indent)
    return hline + actual_body + expected_body


def _hline(op, keypath, color):
    line = op + ' ' + '.'.join(keypath)
    return colored(line, color)


def _body(item, indent=''):
    body = json.dumps(item, indent='  ')
    if '\n' in body:
        # Multiline object.
        indented_body = body.replace('\n', '\n' + indent)
        return '\n' + indent + indented_body
    else:
        # Single-line object.
        return ' ' + body
