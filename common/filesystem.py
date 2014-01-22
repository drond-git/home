#!/usr/bin/env python
#123456789.123456789.123456789.123456789.123456789.123456789.123456789.123456789
#
# Utilities for working with filesystem items.


import logging
import os
import re
import time


def GetFileContents(filename):
  """Return contents of an existing filename."""
  with open(filename, 'r') as f:
    return f.read()


def WriteFileContents(filename, contents):
  """Writes contents string to filename."""
  with open(filename, 'w') as f:
    f.write(contents)


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


# This can probably be replaced by something from datetime library.
def _GenerateMmMap(months):
  """Returns a dict e.g. with 'february' or 'feb' mapped to '02'."""
  mm_by_month_map = {}
  for i, month in enumerate(months):
    mm_by_month_map[month] = '%02d' % (i + 1)
  return mm_by_month_map


class Transformation(object):
  """Encapsulates transforming strings from one format to another.

  A string gets parsed according to some expected format, and then
  transformed to a different string according to defined rules.
  """

  def __init__(self, match_re, transformation_rule):
    """Records transormation rules this instance will use."""
    # Consider whether testing compatibility of these two reduces risk of bugs.
    self._match_re = match_re
    self._transformation_rule = transformation_rule

  def __repr__(self):
    return (
        '%s(%s,%s)' % (
            self.__class__.__name__, self._match_re, self._transformation_rule))

  def Transform(self, string_):
    """Return transformation result for string_, or None if it didn't match."""
    string_to_match = string_.lower()
    if string_to_match == string_:
      logging.debug('Transforming %r via %r.', string_to_match, self)
    else:
      logging.debug(
          'Transforming %r (original %r) via %r.',
          string_to_match, string_, self)
    match = re.search(self._match_re, string_to_match)
    if match:
      transformation_result = (
          self._transformation_rule % self._CreateLexicon(match.groupdict()))
      logging.debug('Transformed %r to %r.', string_, transformation_result)
      return transformation_result
    logging.debug('No match to transform.')

  _MONTHS_SORTED = (
      'january', 'february', 'march', 'april', 'may', 'june',
      'july', 'august', 'september', 'october', 'november', 'december')
  _MM_BY_MONTH_MAP = _GenerateMmMap(_MONTHS_SORTED)
  _MONS_SORTED = (
      'jan', 'feb', 'mar', 'apr', 'may', 'jun',
      'jul', 'aug', 'sep', 'oct', 'nov', 'dec')
  _MM_BY_MON_MAP = _GenerateMmMap(_MONS_SORTED)

  RE_EXT = r'(?P<ext>\..+)'  # .pdf
  RE_YYYY = r'(?P<yyyy>20[0-2]\d|YYYY)'  # 2000-2029 or YYYY
  RE_YY = r'(?P<yy>[0-2]\d|YYYY)'  # 00-29
  RE_MM = r'(?P<mm>0\d|1[0-2]|MM)'  # 00-12 or MM
  RE_DD = r'(?P<dd>[012]\d|3[01]|DD)'  # 00-31 or DD
  RE_MONTH = r'(?P<month>%s)' % '|'.join(_MONTHS_SORTED)  # january-december
  RE_MON = r'(?P<mon>%s)' % '|'.join(_MONS_SORTED)  # jan-dec
  RE_ORDINAL_0000 = r'(?P<ordinal_0000>\d{1,4})'  # Range 0000-9999.

  def _CreateLexicon(self, tr_dict):
    """Returns a dict from a regexp groups match, modified if needed."""
    if 'ext' in tr_dict:
      # Always lower the extension (this may be redundant now).
      tr_dict['ext'] = tr_dict['ext'].lower()
    if 'yyyy' not in tr_dict:
      # First see if other sources of YYYY are available.
      if 'yy' in tr_dict:
        tr_dict['yyyy'] = '20%s' % tr_dict['yy']
      else:
        # Put something visibly wrong in the YYYY field, if absent.
        tr_dict['yyyy'] = 'YYYY'
    if 'mm' not in tr_dict:
      # First see if other sources of MM are available.
      if 'month' in tr_dict:
        tr_dict['mm'] = self._MM_BY_MONTH_MAP[tr_dict['month'].lower()]
      elif 'mon' in tr_dict:
        tr_dict['mm'] = self._MM_BY_MON_MAP[tr_dict['mon'].lower()]
      else:
        # Put something visibly wrong in the MM field, if absent.
        tr_dict['mm'] = 'MM'
    if 'dd' not in tr_dict:
      # Put something visibly wrong in the DD field, if absent.
      tr_dict['dd'] = 'DD'
    if 'ordinal_0000' in tr_dict:
      tr_dict['ordinal_0000'] = '%04d' % int(tr_dict['ordinal_0000'])
    return tr_dict


class DownloadDirectoryWatcher(object):

    class Error(Exception):
        pass

    class DeadlineExceededError(Error):
        pass

    class WatchNotStartedError(Error):
        pass

    class TooManyNewFilesError(Error):
        pass

    def __init__(self, dirpath, interval_seconds, deadline_seconds=60.0):
        self._dirpath = dirpath
        self._interval_seconds = interval_seconds
        self._deadline_seconds = deadline_seconds
        self._dirlist_last = set()
        self._watch_started = False

    @staticmethod
    def _ListDirectory(dirpath):
        return set(os.listdir(dirpath))

    def StartWatch(self):
        self._dirlist_last = self._ListDirectory(self._dirpath)
        self._watch_started = True
        return self

    def WaitForNewFile(self):
        wait_started_time = time.time()
        if not self._watch_started:
            raise self.WatchNotStartedError()
        while True:
            logging.debug('Watch cycle starting.')
            if time.time() - wait_started_time > self._deadline_seconds:
                raise self.DeadlineExceededError()
            time.sleep(self._interval_seconds)
            added = self._ListDirectory(self._dirpath) - self._dirlist_last
            # Filter out transient files.
            transient = set()
            for filename in added:
                if (re.search('^\..+', filename) or  # Hidden file.
                    filename.endswith('.crdownload')):  # Chrome downloading.
                    transient.add(filename)
            added -= transient
            if len(added) > 1:
                raise self.TooManyNewFilesError()
            if len(added) == 1:
                filename = added.pop()
                logging.debug("Watch returning %r", filename)
                return filename
