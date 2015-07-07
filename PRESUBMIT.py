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
import sys, os, traceback, optparse
import time
from presubmit_rules import java_style
import re

def _GetFileType(input_api, filetype):
  result = []
  for f in input_api.GetAffectedFiles():
    if f.LocalPath().endswith('.' + filetype):
      result.append(f)
  return result


def CheckChangeOnUpload(input_api, output_api):
  result = []
  java_files = _GetFileType(input_api, 'java')
  result += java_style.DoJavaChecks(input_api, output_api, java_files)
  python_files = _GetFileType(input_api, 'py')
  return result
