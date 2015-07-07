#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015 Sean Kirmani <sean@kirmani.io>
#
# Distributed under terms of the MIT license.
"""Enables directory-specific presubmit checks to run.

TODO(Sean Kirmani): DO NOT SUBMIT without a detailed description of test.
"""
import sys, os, traceback, optparse
import types
import time
import re
import xml.etree.ElementTree as ET

PRESUBMIT_PREF_FILE = "presubmit.xml"
PRESUBMIT_PREF_FILE_PATH = os.path.dirname(os.path.realpath(__file__))

def main():
  global options, args
  # TODO(Sean Kirmani): Do something more interesting here...
  DoPresubmitChecks(verbose=True, output_stream=sys.stdout,
      input_stream=sys.stdin, default_presubmit=None, may_prompt=True)

class PresubmitFailure(Exception):
  pass

def normpath(path):
  """Version of os.path.normpath that also changes backward slashes to forward
  slashes when not running on Windows.
  """
  path = path.replace(os.sep, '/')
  return os.path.normpath(path)

class PresubmitOutput(object):
  def __init__(self, input_stream=None, output_stream=None):
    self.input_stream = input_stream
    self.output_stream = output_stream
    self.written_output = []
    self.error_count = 0

  def prompt_yes_no(self, prompt_string):
    self.write(prompt_string)
    if self.input_stream:
      response = self.input_stream.readline().strip().lower()
      if response not in ('y', 'yes'):
        self.fail()
    else:
      self.fail()

  def fail(self):
    self.error_count += 1

  def should_continue(self):
    return not self.error_count

  def write(self, s):
    self.written_output.append(s)
    if self.output_stream:
      self.output_stream.write(s)

  def getvalue(self):
    return ''.join(self.writting_output)

class PresubmitExecuter(object):
  def __init__(self, verbose):
    self.verbose = verbose

  def ExecPresubmitScript(self, script_text, presubmit_path):
    """Executes a single presubmit script.

    Args:
      script_text: The text of the presubmit script.
      presubmit_path: The path to the presubmit file (this will be reported via
        input_api.PresubmitLocalPath()).

    Return:
      A list of result objects, empty if no problems.
    """
    # Change to the presubmit file's directory to support local imports.
    main_path = os.getcwd()
    os.chdir(os.path.dirname(presubmit_path))

    # Load the presubmit script into context.
    # TODO: write InputApi
    input_api = InputApi(presubmit_path, self.verbose)

    context = {}
    try:
      exec script_text in context
    except Exception, e:
      raise PresubmitFailure('"%s" has an exception.\n%s' % (presubmit_path, e))

    function_name = 'CheckChangeOnUpload'
    if function_name in context:
      # TODO: write OutputApi
      context['__args'] = (input_api, OutputApi())
      print('Running %s in %s' % (function_name, presubmit_path))
      result = eval(function_name + '(*__args)', context)
      print('Running %s done.' % function_name)
      if not (isinstance(result, types.TupleType) or
          isinstance(result, types.ListType)):
        raise PresubmitFailure(
            'Presubmit functions must return a tuple or list')
      for item in result:
        if not isinstance(item, OutputApi.PresubmitResult):
          raise PresubmitFailure(
              'All presubmit results must be of types derived from '
              'output_api.PresubmitResult')
    else:
      result = () # no error since the script doesn't care about current event.

    # Return the process to the original working directory
    os.chdir(main_path)
    return result


def DoPresubmitChecks(verbose,
    output_stream,
    input_stream,
    default_presubmit,
    may_prompt):
  """Runs all presubmit checks that apply to the files in the change.

  This finds all PRESUBMIT.py files in all directories enclosing the files in
  the change (up to the repository root) and calls the relevant entrypoint
  function depending on whether the change is being committed or uploaded.

  Prints errors, warnings, and notifications. Prompts the user for warnings
  when needed.

  Args:
    change: The Change object.
    verbose: Prints debug info.
    output_stream: A stream to write output from presubmit tests to.
    input_stream: A stream to read input from the user.
    default_presubmit: A default presubmit script to execute in any case.
    may_prompt: Enable (y/n) questions on warning or error.

  Return:
    A PresubmitOutput object. Use output.should_continue() to figure out if
    there were errors or warnings and the caller should abort.
  """
  old_environ = os.environ
  try:
    # Make sure python subprocesses won't generate .pyc files.
    os.environ = os.environ.copy()
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

    output = PresubmitOutput(input_stream, output_stream)
    start_time = time.time()
    base_dir = _GetBaseDir()
    presubmit_files = ListRelevantPresubmitFiles(
        _AbsoluteLocalPaths(base_dir),
        base_dir)
    if not presubmit_files and verbose:
      output.write("Warning, no PRESUBMIT.py found.\n")
    results = []
    # TODO: write PresubmitExcecuter
    executer = PresubmitExecuter(verbose)
    if default_presubmit:
      if verbose:
        output.write("Running default presubmit script.\n")
      fake_path = os.path.join(base_dir, 'PRESUBMIT.py')
      results += executer.ExecPresubmitScript(default_presubmit, fake_path)
    for filename in presubmit_files:
      filename = os.path.abspath(filename)
      if verbose:
        output.write("Running %s\n" % filename)
      #Accept CRLF presubmit script.
      presubmit_script = file(filename).read()
      results += executer.ExecPresubmitScript(presubmit_script, filename)

    errors = []
    notifications = []
    warnings = []
    for result in results:
      if result.fatal:
        errors.append(result)
      elif result.should_prompt:
        warnings.append(result)
      else:
        notifications.append(result)

    output.write('\n')
    for name, items, in (('Messages', notifications),
        ('Warnings', warnings),
        ('ERRORS', errors)):
      if items:
        output.write('** Presubmit %s **\n' % name)
        for item in items:
          item.handle(output)
          output.write('\n')

    total_time = time.time() - start_time
    if total_time > 1.0:
      output.write("Presubmit checks took %.1fs to calculate.\n\n"
          % total_time)

    if not errors:
      if not warnings:
        output.write('Presubmit checks passed.\n')
      elif may_prompt:
        output.prompt_yes_no('There were presubmit warnings. '
            'Are you sure you wish to continue? (y/N): ')
      else:
        output.fail()

    return output
    # TODO: finish
  finally:
    os.environ = old_environ

def ListRelevantPresubmitFiles(files, root):
  """Finds all presubmit files that apply to a given set of source files.

  Args:
    files: An iterable container containing file paths.
    root: Path where to stop searching.

  Return:
    List of absolute paths of the existing PRESUBMIT.py scripts.
  """
  files = [normpath(os.path.join(root, f)) for f in files]

  # List all the individual directories containing files.
  directories = set([os.path.dirname(f) for f in files])

  # Collect all unique directories that may contain PRESUBMIT.py.
  candidates = set()
  for directory in directories:
    while True:
      if directory in candidates:
        break
      candidates.add(directory)
      if directory == root:
        break
      parent_dir = os.path.dirname(directory)
      if parent_dir == directory:
        # We hit the system root directory.
        break
      directory = parent_dir

    # Look for PRESUBMIT.py in all candidate directories.
    results = []
    for directory in sorted(list(candidates)):
      p = os.path.join(directory, 'PRESUBMIT.py')
      if os.path.isfile(p):
        results.append(p)

    print('Presubmit files: %s' % ','.join(results))
    return results;

def _AbsoluteLocalPaths(root):
  """Finds all files in given source directroy with absolute path.

  Args:
    root: Path to find enclosing files.

  Return:
    List of absolute paths of all enclosing files.
  """
  results = []
  for r, dirs, files in os.walk(root):
    for f in files:
      results.append(os.path.join(r, f))
  return results

def _LocalPaths(root):
  """Finds all files in given source directroy.

  Args:
    root: Path to find enclosing files.

  Return:
    List of absolute paths of all enclosing files.
  """
  results = []
  for r, dirs, files in os.walk(root):
    for f in files:
      results.append(os.path.join(os.path.relpath(r, root), f))
  return results

class _PresubmitResult(object):
  """Base class for result objects."""
  fatal = False
  should_prompt = False

  def __init__(self, message, items=None, long_text=''):
    """
    message: A short one-line message to indicate errors.
    items: A list of short strings to indicate where errors occurred.
    long_text: multi-line text output, e.g. from another tool
    """
    self._message = message
    self._items = items or []
    if items:
      self._items = items
    self._long_text = long_text.rstrip()

  def handle(self, output):
    output.write(self._message)
    output.write('\n')
    for index, item in enumerate(self._items):
      output.write('  ')
      # Write separately in case it's unicode.
      output.write(str(item))
      if index < len(self._items) -1:
        output.write(' \\')
      output.write('\n')
    if self._long_text:
      output.write('\n***************\n')
      # Write separately in case it's unicode.
      output.write(self._long_text)
      output.write('\n***************\n')
    if self.fatal:
      output.fail()

class _PresubmitError(_PresubmitResult):
  """A hard presubmit error."""
  fatal = True

class _PresubmitPromptWarning(_PresubmitResult):
  """A warning that prompts the user if they want to continue."""
  should_prompt = True

class OutputApi(object):
  """An instance of OutputApi gets passed to presubmit scripts so that they can
  output various types of results.
  """
  PresubmitResult = _PresubmitResult
  PresubmitError = _PresubmitError
  PresubmitPromptWarning = _PresubmitPromptWarning

class InputApi(object):
  """An instance of this object is passed to presubmit scripts so they can know
  stuff about the change they're looking at.
  """
  DEFAULT_WHITE_LIST = ()
  DEFAULT_BLACK_LIST = ()

  def __init__(self, presubmit_path, verbose):
    """Builds an InputApi object.

    Args:
      presubmit_path: The path to the presubmit script being processed.
    """
    # The local path of the currently-being-processed presubmit script.
    self._repository_root = _GetBaseDir()
    self._current_presubmit_path = os.path.dirname(presubmit_path)
    self._local_paths = _LocalPaths(self._repository_root)
    self.verbose = verbose

  def GetAffectedFiles(self):
    return [AffectedFile(f, self._repository_root) for f in self._local_paths]


class AffectedFile(object):
  """Representation of a file in a change."""

  def __init__(self, path, repository_root):
    self._path = path
    self._local_root = repository_root

  def LocalPath(self):
    """Returns the path of the file on the local disk relative to the client
    root.
    """
    return normpath(self._path)

  def AbsoluteLocalPath(self):
    """Returns the absolute path of this file on the local disk.
    """
    return os.path.abspath(os.path.join(self._local_root, self.LocalPath()))

  def GetFile(self):
    return open(self.AbsoluteLocalPath())

  def ReadFile(self):
    return open(self.AbsoluteLocalPath()).read()

  def ReadFileLines(self):
    return open(self.AbsoluteLocalPath()).readlines()

def _GetPresubmitPrefTree():
  return ET.parse(PRESUBMIT_PREF_FILE)

def _GetBaseDir():
  tree = _GetPresubmitPrefTree()
  root = tree.getroot()
  if root.tag != 'presubmit':
    raise Exception("presubmit tag not found in root")
  attributes = root.attrib
  if 'basedir' not in attributes:
    return '.'
  return os.path.abspath(attributes['basedir'])

if __name__ == '__main__':
  try:
    start_time = time.time()
    parser = optparse.OptionParser(formatter=optparse.TitledHelpFormatter(), \
        usage=globals()['__doc__'], version='$Id$')
    parser.add_option('-v','--verbose', action='store_true', default=False, \
        help='verbose output')
    (options, args) = parser.parse_args()
    # if len(args) < 1:
    #   parser.error('missing argument')
    if options.verbose: print(time.asctime())
    main()
    if options.verbose: print(time.asctime())
    if options.verbose: print('TOTAL TIME IN MINUTES:')
    if options.verbose: print(time.time() - start_time) / 60.0
    sys.exit(0)
  except KeyboardInterrupt, e: # Ctrl-C
    raise e
  except SystemExit, e: # sys.exit()
    raise e
  except Exception, e:
    print('ERROR, UNEXPECTED EXCEPTION')
    print(str(e))
    traceback.print_exc()
    os._exit(1)
