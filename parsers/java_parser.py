#!public  /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015 Sean Kirmani <sean@kirmani.io>
#
# Distributed under terms of the MIT license.
"""TODO(Sean Kirmani): DO NOT SUBMIT without one-line documentation for test

TODO(Sean Kirmani): DO NOT SUBMIT without a detailed description of test.
"""

SEMICOLON = ';'
OPEN_BRACE = '{'
CLOSE_BRACE = '}'
BRACES_SET = OPEN_BRACE + CLOSE_BRACE
OPEN_PAREN = '('
CLOSE_PAREN = ')'
COMMA = ','
COMMENT_BLOCK_BEGIN = '/**'
COMMENT_BLOCK_END = '*/'

PACKAGE_START_STRING = 'package '
IMPORT_START_STRING = 'import '

# Java Object Types
ROOT = 'root'
PACKAGE = 'package'
IMPORT = 'import'
CLASS = 'class'
METHOD = 'method'
VARIABLE = 'variable'
PARAMETERS = 'parameters'

class JavaLexer(object):
  def __init__(self, f):
    self._file = f
    self._file_lines = [l for l in f.readlines()]
    self.thing = ROOT
    self.children = _CreateTree(self._RemoveComments(self._RawText()))
    _PrintTree(self)

  def _RawText(self):
    return ''.join([l.strip() for l in self._file_lines])

  def _RemoveComments(self, text):
    result = ''
    in_comment = False
    for index in range(len(text)):
      if text[index : index + len(COMMENT_BLOCK_BEGIN)] == COMMENT_BLOCK_BEGIN:
        in_comment = True
      if not in_comment:
        result += text[index]
      if text[index + 1 - len(COMMENT_BLOCK_END) : index + 1] == \
          COMMENT_BLOCK_END:
        in_comment = False
    return result

  def Printable(self):
    return self.thing

class JavaPackage(object):
  def __init__(self, block):
    self.package = block[len(PACKAGE_START_STRING):][:-len(SEMICOLON)]
    self.thing = PACKAGE

  def Printable(self):
    return '%s: %s' % (self.thing, self.package)

class JavaImport(object):
  def __init__(self, block):
    self.imported = block[len(IMPORT_START_STRING):][:-len(SEMICOLON)]
    self.thing = IMPORT
    self.has_children = False

  def Printable(self):
    return '%s: %s' % (self.thing, self.imported)

class JavaClass(object):
  def __init__(self, block, leftover):
    self.qualifiers = self._GetQualifiers(block[:-len(BRACES_SET)])
    self.name = self._GetName(block[:-len(BRACES_SET)])
    self.children = _CreateTree(leftover)
    self.thing = CLASS

  def _GetQualifiers(self, block):
    result = []
    words = block.split()
    for word in words:
      if word == 'class':
        return result
      result.append(word)

  def _GetName(self, block):
    words = block.split()
    is_next = False
    for word in words:
      if is_next:
        return word
      if word == 'class':
        is_next = True

  def Printable(self):
    return '%s: %s %s' % (self.thing, self.qualifiers, self.name)

class JavaMethod(object):
  def __init__(self, block, leftover):
    leftside = block[:block.find(OPEN_PAREN)].rstrip()
    words = leftside.split()
    rightside = block[block.find(OPEN_PAREN) + len(OPEN_PAREN) :
        block.find(CLOSE_PAREN)]
    self.qualifiers = words[:len(words) - 1]
    self.name = words[len(words) - 1]
    parameters = JavaParameters(rightside)
    self.children = [parameters] if len(parameters.children) > 0 else []
    self.children += _CreateTree(leftover)
    self.thing = METHOD

  def Printable(self):
    return '%s: %s %s' % (self.thing, self.qualifiers, self.name)

class JavaVariable(object):
  def __init__(self, words):
    self.thing = VARIABLE
    if len(words) > 2:
      self.qualifiers = words[:len(words) - 2]
    else:
      self.qualifiers = []
    self.object_type = words[len(words) - 2]
    self.name = words[len(words) - 1]

  def Printable(self):
    return '%s: %s %s %s' % (self.thing, self.qualifiers, self.object_type,
        self.name)

class JavaParameters(object):
  def __init__(self, block):
    self.thing = PARAMETERS
    params = [param.split() for param in block.split(COMMA)]
    self.children = [JavaVariable(param) for param in params
        if len(param) >= 2]

  def Printable(self):
    return self.thing

def _GetTree(text):
  result = ''
  removed = ''
  stack = []
  for index in range(len(text)):
    if index - 1 > 0 and text[index - 1] == OPEN_BRACE:
      stack.append(OPEN_BRACE)
    if len(stack) == 0:
      result += text[index]
    else:
      removed += text[index]
    if index + 1 < len(text) and text[index + 1] == CLOSE_BRACE:
      if len(stack) > 0:
        stack.pop()
  return result, removed

def _GetBlocks(text):
  text, leftover = _GetTree(text)
  result = []
  current_block = ''
  for index in range(len(text)):
    current_block += text[index]
    if text[index] == ';' or text[index + 1 - len(BRACES_SET) : index + 1] == \
        BRACES_SET:
      result.append(current_block)
      current_block = ''
  return result, leftover

def _CreateTree(text):
    blocks, leftover = _GetBlocks(text)
    root = []
    for block in blocks:
      if block.startswith(PACKAGE_START_STRING) and block.endswith(SEMICOLON):
        root.append(JavaPackage(block))
      if block.startswith(IMPORT_START_STRING) and block.endswith(SEMICOLON):
        root.append(JavaImport(block))
      if 'class' in block and block.endswith(BRACES_SET):
        root.append(JavaClass(block, leftover))
      elif block.endswith(BRACES_SET):
        root.append(JavaMethod(block, leftover))
      if '=' in block and block.endswith(SEMICOLON):
        leftside = block[:block.find('=')].rstrip()
        words = leftside.split()
        if len(words) > 1:
          root.append(JavaVariable(words))
    return root

def _PrintTree(root, spaces=''):
  print(spaces + root.Printable())
  if hasattr(root, 'children'):
    for child in root.children:
      _PrintTree(child, spaces + '  ')
