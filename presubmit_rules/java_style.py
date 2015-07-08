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
import operator
import sys
import unicodedata

from parsers import java_parser

COLUMN_LIMIT = 100

def DoJavaChecks(input_api, output_api, files):
  results = []
  for f in files:
    results +=  _DoJavaCheck(input_api, output_api, f)
  return results

def _DoJavaCheck(input_api, output_api, f):
  results = []
  results += _CheckFileName(input_api, output_api, f)
  results += _CheckWhiteSpaceCharacter(input_api, output_api, f)
  results += _CheckSpecialEscapeSequences(input_api, output_api, f)
  results += _CheckNonAsciiCharacters(input_api, output_api, f)
  results += _CheckLicense(input_api, output_api, f)
  results += _CheckWildcardImports(input_api, output_api, f)
  results += _CheckColumnLimit(input_api, output_api, f)
  results += _CheckImportOrderingAndSpacing(input_api, output_api, f)

  # DEBUG
  lexer = java_parser.JavaLexer(f.File())
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
  return _GenerateWarnings('The source file name consists of the '
      'case-sensitive name of the top-level class is contains, plus the .java '
      'extension.', errors, output_api)

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
  return _GenerateWarnings('Aside from the line terminator sequence, the '
      'ASCII horizontal space character (0x20) is the only whitespace '
      'character that appears anywhere in a source file.', errors, output_api)

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
  return _GenerateWarnings('For any character that has a special escape '
      'sequence ( \\b, \\t, \\n, \\f. \\r. \\". \\\', \\\\ ), that sequence '
      'is used rather than the corresponding octal (e.g. \\012 ) or Unicode '
      '(e.g. \\u000a ) escape.', errors, output_api)

def _CheckNonAsciiCharacters(input_api, output_api, f):
  """2.3.3 Non-ASCII characters

  For the remaining non-ASCII characters, either the actual Unicode character
  (e.g. ∞ ) or the equivalent Unicode escape (e.g. \u221e is used, depending
  only on which makes the code easier to read and understand.
  """
  errors = []
  # TODO: write this (kirmani)
  return _GenerateWarnings('For the remaining non-ASCII characters, either '
      'the actual Unicode character (e.g. ∞ ) or the equivalent Unicode '
      'escape (e.g. \\u221e ) is used, depending only on which makes the code '
      'easier to read and understand.', errors, output_api)

def _CheckLicense(input_api, output_api, f):
  """3.1 License or copyright information, if present

  If license or copyright information belongs in a file, it belongs here.
  """
  errors = []
  if not f.ReadFile().startswith(input_api.License()):
    errors.append("Beginning of file does not match the following:\n%s"
        % input_api.License())
  return _GenerateWarnings('If license or copyright information belongs in a '
      'file, it belongs here', errors, output_api)

def _CheckWildcardImports(input_api, output_api, f):
  """3.3.1 No wildcard imports

  Wildcard imports, static or otherwise, are not used.
  """
  errors = []
  lines = [l.rstrip() for l in f.ReadFileLines()]
  line_num = 1
  for line in lines:
    if line.startswith('import '):
      if '*' in line:
        errors.append(_ReportErrorFileAndLine(f.LocalPath(), line_num,
          line))
  return _GenerateWarnings('Wildcard imports, static or otherwise, are not '
      'used.', errors, output_api)

def _CheckImportOrderingAndSpacing(input_api, output_api, f):
  """3.3.3 Ordering and spacing

  Import statements are divided into the following groups, in this order, with
  each group separated by a single line:

  1. All static imports in a single group.
  2. com.google imports (only if this source file is in the com.google pacakge
     space)
  3. Third-party imports, one group per top-level package, in ASCII sort order
     - for example: android, com, junit, org, sun
  4. java imports
  5. javax imports

  Within a group there are no blank lines, and the imported names appear in
  ASCII sort order. (Note: this is not the same as import statements being in
  ASCII sort order; the presence of semicolons warps the result.)
  """
  class ImportLine(object):
    def __init__(self, text, line_num):
      self.text = text
      self.line_num = line_num

    def TextWithoutImport(self):
      return self.text[7:]

  def _GenerateImports(imports):
    result = ""
    for imp in imports['static']:
      result += imp.text + '\n'
    if len(imports['static']) > 0:
      result += '\n'
    for imp in imports['com_google']:
      result += imp.text + '\n'
    if len(imports['com_google']) > 0:
      result += '\n'
    for imp in imports['third_party']:
      result += imp.text + '\n'
    if len(imports['third_party']) > 0:
      result += '\n'
    for imp in imports['java']:
      result += imp.text + '\n';
    if len(imports['java']) > 0:
      result += '\n'
    for imp in imports['javax']:
      result += imp.text + '\n'
    return result.strip()

  def _IndentedString(string, num_spaces):
    if num_spaces == 0:
      return string
    return _IndentedString(' '.join((' ' + string).splitlines(True)),
        num_spaces - 1)

  def _SortedImports(import_lines):
    imports = {
        'static': [],
        'com_google': [],
        'third_party': [],
        'java': [],
        'javax': [],
        }
    for line in import_lines:
      if 'static' in line.text:
        imports['static'].append(line)
      elif line.TextWithoutImport().startswith('com.google'):
        imports['com_google'].append(line)
      elif line.TextWithoutImport().startswith('javax'):
        imports['javax'].append(line)
      elif line.TextWithoutImport().startswith('java'):
        imports['java'].append(line)
      else:
        imports['third_party'].append(line)
    sorted_imports_dict = {imp : sorted(imports[imp],
      key=operator.attrgetter('text')) for imp in imports}
    return _GenerateImports(sorted_imports_dict)

  def _OriginalImports(import_lines):
    if len(import_lines) == 0:
      return ''
    result = ''
    previous_line = import_lines[0]
    for line in import_lines:
      for i in range(previous_line.line_num, line.line_num):
        result += '\n'
      result += line.text
      previous_line = line
    return result

  errors = []
  lines = [l.rstrip() for l in f.ReadFileLines()]
  line_num = 1
  import_lines = []
  for line in lines:
    if line.startswith('import '):
      import_lines.append(ImportLine(line, line_num))
    line_num += 1

  original_imports = _OriginalImports(import_lines)
  sorted_imports = _SortedImports(import_lines)

  if original_imports != sorted_imports:
    errors.append(_ReportErrorFileAndLine(f.LocalPath(),
      import_lines[0].line_num, 'Imports were not in correct format. Change '
        'the imports to the following sorted import format:\n%s' %
        _IndentedString(sorted_imports, 4)))

  return _GenerateWarnings('Import statements are divided into the following '
      'groups, in this order, with each group separated by a single line: '
      'static imports, com.google imports, third-party imports, java imports, '
      'javax imports.', errors, output_api)

def _CheckColumnLimit(input_api, output_api, f):
  """4.4 Column limit: 80 or 100

  Projects are free to choose a column limit of either 80 or 100 characters.
  Except as not below, any line that would exceed this limit must be
  line-wrapped, as explained in Section 4.5, Line-wrapping.

  Exceptions:
  1. Lines where obeying the column limit is not possible (for example, a long
     URL in Javadoc, or a long JSNI method reference).
  2. package or import statements (see Section 3.2 Package statement and 3.3
     Import statements).
  3. Command lines in a commant that may be cut-and-pasted into a shell.
  """
  lines = [l.rstrip() for l in f.ReadFileLines()]
  line_num = 1
  errors = []
  for line in lines:
    if not line.startswith('package ') and not line.startswith('import '):
      if len(line) > COLUMN_LIMIT:
        errors.append(_ReportErrorFileAndLine(f.LocalPath(), line_num,
          'Line is %s characters, the limit is %s characters.' %
          (len(line), COLUMN_LIMIT)))
    line_num += 1
  return _GenerateWarnings('Projects are free to choose a column limit of '
      'either 80 or 100 characters. By default, it is 100 characters.',
      errors, output_api)

def _ReportErrorFileAndLine(filename, line_num, msg=''):
  """Default error formatter"""
  if msg != '':
    return '%s:%s MSG: %s' % (filename, line_num, msg)
  else:
    return '%s:%s' % (filename, line_num)

def _GenerateWarnings(msg, errors, output_api):
  if errors:
    return [output_api.PresubmitPromptWarning(msg, items=errors)]
  return []
