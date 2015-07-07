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
import re

def main():
  global options, args
  # TODO(Sean Kirmani): Do something more interesting here...
  print 'Hello world!'

class Changelist(object):
  def __init__(self, branchref=None, issue=None, auth_config=None):
    pass

  def RunHook(self, may_prompt, verbose, change):
    """Calls sys.exit() if the hook fails; returns a HooksResults otherwise."""

    try:
      # TODO: create change
      # TODO: create verbose
      # TODO: create may_prompt
      return presubmit_support.DoPresubmitChecks(change, verbose=verbose,
          output_stream=sys.stdout, input_stream=sys.stdin,
          default_presubmit=None, may_prompt=may_prompt)
    # TODO: write presubmit_support.PresubmitFailure
    except presubmit_support.PresubmitFailure, e:
      DieWithError(e)

def DieWithError(message):
  print >> sys.stderr, message
  sys.exit(1)

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
