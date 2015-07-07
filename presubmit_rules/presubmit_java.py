#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015 Sean Kirmani <sean@kirmani.io>
#
# Distributed under terms of the MIT license.
"""TODO(Sean Kirmani): DO NOT SUBMIT without one-line documentation for test

TODO(Sean Kirmani): DO NOT SUBMIT without a detailed description of test.
"""
import sys
sys.dont_write_bytecode = True

COLUMN_LIMIT = 100

def DoJavaChecks(input_api, output_api, files):
  results = []
  for f in files:
    results += _DoJavaCheck(input_api, output_api, f)
  return results

def _DoJavaCheck(input_api, output_api, f):
  results = []
  results.append(_CheckLineLength(input_api, output_api, f))
  return results

def _CheckLineLength(input_api, output_api, f):
  results = ()
  with open(f) as fh:
    lines = [l.strip() for l in fh.readlines()]
  line_num = 1
  errors = []
  for line in lines:
    if len(line) > COLUMN_LIMIT:
      errors.append(_ReportErrorFileAndLine("FILEPATH", line_num, line))
    line_num += 1
  if errors:
    msg = 'Found lines longer than %s characters.' % COLUMN_LIMIT
    return output_api.PresubmitPromptWarning(msg, items=errors)
  else:
    return []

def _ReportErrorFileAndLine(filename, line_num, dummy_line):
  """Default error formatter"""
  return '%s:%s' % (filename, line_num)
