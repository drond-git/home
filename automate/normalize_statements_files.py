#!/usr/bin/env python
#
# All statements files should be named consistently. Rename statements
# files in all directories, and list files that were not recognized.

import re
import logging
import os

logging.basicConfig(level=logging.INFO)


# The directory where to look for statements files.
STATEMENTS_ROOT_DIR = (
    '/Users/vsh/Personal/Google Drive/drond-cloud/gtd/refs/finances/'
    'statements')


def GenerateMmByMonthMap():
  mm_by_month_map = {}
  for i, month in enumerate((
       'january', 'february', 'march', 'april', 'may', 'june',
       'july', 'august', 'september', 'october', 'november', 'december')):
      mm_by_month_map[month] = '%02d' % (i + 1)
  return mm_by_month_map

MM_BY_MONTH_MAP = GenerateMmByMonthMap()


def ListFilesRecursively(directory):
  """Yields tuple (dirname, basename) for every file below directory."""
  logging.debug('Listing files in %r.', directory)
  for (dirpath, unused_dirnames, filenames) in os.walk(directory):
    for filename in filenames:
      if os.path.isfile(os.path.join(dirpath, filename)):
        yield dirpath, filename


def TryNormalize(dirpath, filename, dry_run=True):
  """If necessary, normalized the file. Returns a tuple."""
  logging.debug('Trying to normalize %r in %r.', filename, dirpath)
  # First try the cases where reordering extracted date values is enough.
  simple_conversions = [
    # eStmt_2012-09-07.pdf
    r'^eStmt_(?P<yyyy>\d\d\d\d)-(?P<mm>\d\d)-(?P<dd>\d\d)(?P<ext>\..+)$',
  ]
  for regexp in simple_conversions:
    match = re.search(regexp, filename)
    if match:
      return '%(yyyy)s%(mm)s%(dd)s-eStmt%(ext)s)' % match.groupdict()
  # Then try when custom computation is needed.
  # November2012_7257.qfx
  match = re.search(
      r'(?P<month>[a-zA-Z]+)(?P<yyyy>\d{4})_(?P<four>\d{4})(?P<ext>\.(?:qfx|QFX))',
      filename)
  if match:
    keywords = match.groupdict()
    keywords['mm'] = MM_BY_MONTH_MAP[keywords['month'].lower()]
    return '%(yyyy)s%(mm)s01%(ext)s)' % keywords
  
  return None  # None if not matched any renamer expression..


def NormalizeStatementsFiles():
  fileset_initial = ListFilesRecursively(STATEMENTS_ROOT_DIR)
  for dirpath, filename in fileset_initial:
    filename_new = TryNormalize(dirpath, filename, dry_run=True)
    dirpath_relative = dirpath[len(STATEMENTS_ROOT_DIR):]
    if not filename_new:
      print 'Unmatched: %r (%r)' % (filename, dirpath_relative)
    elif filename_new != filename:
      print 'Renamed: %r %r (%r)' % (filename, filename_new, dirpath_relative)

      
def main():
  NormalizeStatementsFiles()


if __name__ == '__main__':
  main()
