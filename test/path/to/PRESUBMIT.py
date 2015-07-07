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
  print 'Presubmit'

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
