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
import unicodedata
import sys
sys.dont_write_bytecode = True

COLUMN_LIMIT = 100

def DoJavaChecks(input_api, output_api, files):
  results = []
  for f in files:
    results +=  _DoJavaCheck(input_api, output_api, f)
  return results

def _DoJavaCheck(input_api, output_api, f):
  results = []
  results += _CheckLineLength(input_api, output_api, f)
  results += _CheckFileName(input_api, output_api, f)
  results += _CheckWhiteSpaceCharacter(input_api, output_api, f)
  results += _CheckSpecialEscapeSequences(input_api, output_api, f)
  return results

def _CheckFileName(input_api, output_api, f):
  """2.1 File name

  The source file name consists of the case-sensitive name of the top-level
  class it contains, plus the .java extension.
  """
  file_name = f.FileName()
  errors = []
  if not file_name.endswith('.java'):
    errors.append("%s does not end in .java" % f.LocalPath())
  if not file_name[0].isupper():
    errors.append("%s must start with upper case letter." % f.LocalPath())
  if errors:
    msg = 'The source file name consists of the case-sensitive name of the ' \
      + 'top-level class it contains, plus the .java extension.'
    return [output_api.PresubmitPromptWarning(msg, items=errors)]
  else:
    return []

def _CheckWhiteSpaceCharacter(input_api, output_api, f):
  """2.3.1 Whitespace characters

  Aside from the line terminator sequence, the ASCII horizontal space character
  (0x20) is the only whitespace character that appears anywhere in a source
  file. This implies that:

  1. All other whitespace characters in string and character literals are
     escaped.
  2. Tab characters are not used for indentation.
  """
  errors = []
  banned_whitespace_characters = []
  for c in xrange(sys.maxunicode + 1):
    u = unichr(c)
    cat = unicodedata.category(u)
    if (cat == 'Zs' or cat == 'Zl' or cat == 'Zp') and \
        unicodedata.name(u) != 'SPACE':
      banned_whitespace_characters.append({'name': unicodedata.name(u),
        'char': u})
  banned_whitespace_characters += [
      {'name': 'CHARACTER TABULATION', 'char': '\x09'},
      {'name': 'LINE FEED (LF)', 'char': '\x0A'},
      {'name': 'LINE TABULATION', 'char': '\x0B'},
      {'name': 'FORM FEED (FF)', 'char': '\x0C'},
      {'name': 'CARRIAGE RETURN (CR)', 'char': '\x0D'},
      ]
  lines = [l.rstrip() for l in f.ReadFileLines()]
  line_num = 1
  for line in lines:
    for character in banned_whitespace_characters:
      if character['char'] in line:
        errors.append(_ReportErrorFileAndLine(f.LocalPath(), line_num,
          'Contains %s' % character['name']))
    line_num += 1
  if errors:
    msg = 'Aside from the line terminator sequence, the ASCII horizontal ' \
        + 'space character (0x20) is the only whitespace character that ' \
        + 'appears anywhere in a source file.'
    return [output_api.PresubmitPromptWarning(msg, items=errors)]
  else:
    return []

def _CheckSpecialEscapeSequences(input_api, output_api, f):
  """2.3.2 Special escape sequences

  For any character that has a special escape sequence ( \b, \t, \n, \f, \r,
  \", \', and \\ ), that sequence is used rather than the corresponding octal
  (e.g. \012 ) or Unicode (e.g. \u000a) escape.
  """
  errors = []
  special_escape_sequences = [
      {'correct': 'b', 'octal': '010', 'unicode': 'u0008'},
      {'correct': 't', 'octal': '011', 'unicode': 'u0009'},
      {'correct': 'n', 'octal': '012', 'unicode': 'u000a'},
      {'correct': 'f', 'octal': '014', 'unicode': 'u000c'},
      {'correct': 'r', 'octal': '015', 'unicode': 'u000d'},
      {'correct': '"', 'octal': '042', 'unicode': 'u0022'},
      {'correct': '\'', 'octal': '047', 'unicode': 'u0027'},
      {'correct': '\\', 'octal': '0134', 'unicode': 'u005c'},
      ]
  lines = [l.rstrip() for l in f.ReadFileLines()]
  line_num = 1
  for line in lines:
    for index in range(len(line) - 1):
      if line[index] == '\\':
        sequence = line[index + 1:]
        for seq in special_escape_sequences:
          if sequence.startswith(seq['octal']):
            errors.append(_ReportErrorFileAndLine(f.LocalPath(), line_num,
              'Should have used \\%s instead of the octal \\%s'
              % (seq['correct'], seq['octal'])))
          if sequence.lower().startswith(seq['unicode']):
            errors.append(_ReportErrorFileAndLine(f.LocalPath(), line_num,
              'Should have used \\%s instead of the unicode \\%s'
              % (seq['correct'], seq['unicode'])))
    line_num += 1
  if errors:
    msg = 'For any character that has a special escape sequence ( \\b, \\t, ' \
        + '\\n, \\f, \\r, \\", \\\', \\\\ ), that sequence is used rather ' \
        + 'than the corresponding octal (e.g. \\012) or Unicode (e.g. ' \
        + '\\u000a ) escape.'
    return [output_api.PresubmitPromptWarning(msg, items=errors)]
  else:
    return []

def _CheckLineLength(input_api, output_api, f):
  lines = [l.rstrip() for l in f.ReadFileLines()]
  line_num = 1
  errors = []
  for line in lines:
    if len(line) > COLUMN_LIMIT:
      errors.append(_ReportErrorFileAndLine(f.LocalPath(), line_num))
    line_num += 1
  if errors:
    msg = 'Found lines longer than %s characters.' % COLUMN_LIMIT
    return [output_api.PresubmitPromptWarning(msg, items=errors)]
  else:
    return []

def _PrintItems(items):
  for item in items:
    print item

def _ReportErrorFileAndLine(filename, line_num, msg=''):
  """Default error formatter"""
  if msg != '':
    return '%s:%s MSG: %s' % (filename, line_num, msg)
  else:
    return '%s:%s' % (filename, line_num)

