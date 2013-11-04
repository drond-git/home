#!/usr/bin/env python
#123456789.123456789.123456789.123456789.123456789.123456789.123456789.123456789
#
# Utilities for working with filesystem items.


import logging
import os


def ListFilesRecursively(directory, filter_func=None):
  """Yields tuple (dirpath, filename) for not-filtered files below directory."""
  logging.debug('Listing files in %r.', directory)
  for (dirpath, unused_dirnames, filenames) in os.walk(directory):
    for filename in filenames:
      filepath = os.path.join(dirpath, filename)
      if os.path.isfile(filepath):
        if filter_func:
          if filter_func(filepath):
            continue
        yield dirpath, filename


def GetRelativeDirpath(dirpath, dirpath_root):
  """Returns the trailing part of dirpath with dirpath_root/ omitted."""
  # Defend against double or trailing slash. Could pull this up, to optimize.
  norm_dirpath = os.path.normpath(dirpath)
  norm_dirpath_root = os.path.normpath(dirpath_root)
  # Get the relative dirpath.
  assert norm_dirpath.startswith(norm_dirpath_root)
  relative_dirpath = norm_dirpath.replace(norm_dirpath_root, '')
  # Remove its leading slash.
  if relative_dirpath.startswith('/'):
    relative_dirpath = relative_dirpath[1:]
  return relative_dirpath  # This may be an empty string.
