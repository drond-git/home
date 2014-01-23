#!/usr/bin/env python
#123456789.123456789.123456789.123456789.123456789.123456789.123456789.123456789
#
# Common code for starting application programs.

import argparse
import sys


class Error(Exception):
  pass


class ParsedArgsProxy(object):
  """Redirects to attributes of a managed instance of argparse's parsed args.

  Attributes:
    PARSER: An argparse.ArgumentParser. A globally accessible instance that
        modules of the app can use to define relevant app args.
    ARGS: An instance of parsed args. Provide direct access to the instance,
        just in case attribute redirecting has a bug.
  """

  def __init__(self, argument_parser):
    self.PARSER = argument_parser
    self.ARGS = None
  
  def ProxyTheseArgs(self, parsed_args):
    """Sets the instance of argparse's parsed args to be proxied."""
    self.ARGS = parsed_args
    
  def __getattribute__(self, name):
    # Don't redirect to self.args this class' few members.
    if name in ('PARSER', 'ARGS', 'ProxyTheseArgs'):
      return object.__getattribute__(self, name)
    # Everything else is served from the parser args instance.
    if self.ARGS is not None:
      return getattr(self.ARGS, name)
    raise Error('The parsed args instance not yet initialized.')


# Globally accessible shortcut to the singleton instance, for readability.
ARGS = ParsedArgsProxy(argparse.ArgumentParser())


def _setup_parsed_args():
  """Enccapsulates parsing of app's args, for testability."""
  ARGS.ProxyTheseArgs(ARGS.PARSER.parse_args())


def run():
  """Wraps a call to caller's main(argv) with some useful code."""
  # Parse app's args and make them accessible. Note that it will exit
  # if there's a problem parsing the args.
  _setup_parsed_args()
  # Assuming everything else went well, run main.  
  main = sys.modules['__main__'].main
  exit(main(sys.argv))
