#!/usr/bin/env python
#
# All statements files should be named consistently. Rename statements
# files in all directories, and list files that were not recognized.

import re
import logging
import os

logging.basicConfig(level=logging.DEBUG)


# The directory where to look for statements files.
STATEMENTS_ROOT_DIR = (
    '/Users/vsh/Personal/Google Drive/drond-cloud/gtd/refs/finances/'
    'statements')


MONTHS_SORTED = (
    'january', 'february', 'march', 'april', 'may', 'june',
    'july', 'august', 'september', 'october', 'november', 'december')


def GenerateMmByMonthMap():
  mm_by_month_map = {}
  for i, month in enumerate(MONTHS_SORTED):
      mm_by_month_map[month] = '%02d' % (i + 1)
  return mm_by_month_map


MM_BY_MONTH_MAP = GenerateMmByMonthMap()


RE_YYYY = r'(?P<yyyy>20[0-2]\d|YYYY)'  # 2000-2029 or YYYY
RE_MM = r'(?P<mm>0\d|1[0-2]|MM)'  # 00-12 or MM
RE_DD = r'(?P<dd>[012]\d|3[01]|DD)'  # 00-31 or DD
RE_EXT = r'(?P<ext>\..+)'  # .pdf
RE_MONTH = r'(?P<month>%s)' % '|'.join(MONTHS_SORTED)  # january-december

# Various formats for presenting account numbers, last four digits, etc.
RE_ACCOUNT_ID = (
    r'(?P<account_id>\d{4,7}|[a-z0-9]{4,7})')


def ListFilesRecursively(directory):
  """Yields tuple (dirname, basename) for every file below directory."""
  logging.debug('Listing files in %r.', directory)
  for (dirpath, unused_dirnames, filenames) in os.walk(directory):
    for filename in filenames:
      if os.path.isfile(os.path.join(dirpath, filename)):
        yield dirpath, filename


def MakeKeywords(input):
  """Returns the input dict with select key values adjusted."""
  if 'ext' in input:
    # Always lower the extension (this may be redundant now).
    input['ext'] = input['ext'].lower()
  if 'yyyy' not in input:
    # Put something visibly wrong in the YYYY field, if absent.
    input['yyyy'] = 'YYYY'
  if 'mm' not in input:
    # First see if other sources of MM are available.
    if 'month' in input:
      input['mm'] = MM_BY_MONTH_MAP[input['month'].lower()]
    else:
      # Put something visibly wrong in the MM field, if absent.
      input['mm'] = 'MM'
  if 'dd' not in input:
    # Put something visibly wrong in the DD field, if absent.
    input['dd'] = 'DD'
  return input


def TryNormalize(dirpath, filename, dry_run=True):
  """If necessary, normalized the file. Returns a tuple."""
  logging.debug('Trying to normalize %r in %r.', filename, dirpath)
  # No matter what RE_* are available in filename, the YYYY, MM, and DD
  # keywords will be set or made up if needed.
  conversions = [
    (  # 20120930.pdf
     '^%s%s%s%s$' % (RE_YYYY, RE_MM, RE_DD, RE_EXT),
     '%(yyyy)s%(mm)s%(dd)s%(ext)s)'),
    (  # 09302012.pdf
     '^%s%s%s%s$' % (RE_DD, RE_MM, RE_YYYY, RE_EXT),
     '%(yyyy)s%(mm)s%(dd)s%(ext)s)'),
    (  # 2012_09.pdf
     '^%s_%s%s$' % (RE_YYYY, RE_MM, RE_EXT),
     '%(yyyy)s%(mm)s%(dd)s%(ext)s)'),
    (  # eStmt_2012-09-27.pdf
     '^eStmt_%s-%s-%s%s$' % (RE_YYYY, RE_MM, RE_DD, RE_EXT),
     '%(yyyy)s%(mm)s%(dd)s_eStmt%(ext)s)'),
    (  # eStmt_09-27-2012.pdf
     '^eStmt_%s-%s-%s%s$' % (RE_MM, RE_DD, RE_YYYY, RE_EXT),
     '%(yyyy)s%(mm)s%(dd)s_eStmt%(ext)s)'),
    (  # November2012_7257.qfx
     '^%s%s_%s%s' % (RE_MONTH, RE_YYYY, RE_ACCOUNT_ID, RE_EXT),
     '%(yyyy)s%(mm)s%(dd)s_%(account_id)s%(ext)s)'),
    (  # vanguard-093926-20110322.pdf
     '^vanguard-%s-%s%s%s%s' % (RE_ACCOUNT_ID, RE_YYYY, RE_MM, RE_DD, RE_EXT),
     '%(yyyy)s%(mm)s%(dd)s_%(account_id)s%(ext)s)'),
    (  # etrade-9433-20110322.pdf
     '^etrade-%s-%s%s%s%s' % (RE_ACCOUNT_ID, RE_YYYY, RE_MM, RE_DD, RE_EXT),
     '%(yyyy)s%(mm)s%(dd)s_%(account_id)s%(ext)s)'),
    (  # etrade-9433-2011_03-22.pdf
     '^etrade-%s-%s_%s-%s%s' % (RE_ACCOUNT_ID, RE_YYYY, RE_MM, RE_DD, RE_EXT),
     '%(yyyy)s%(mm)s%(dd)s_%(account_id)s%(ext)s)'),
    (  # ing-vf2245-20040930.pdf
     '^ing-%s-%s%s%s%s' % (
         RE_ACCOUNT_ID, RE_YYYY, RE_MM, RE_DD, RE_EXT),
     '%(yyyy)s%(mm)s%(dd)s_%(account_id)s%(ext)s)'),
    # TODO(drond-git): Deal with DDMMYYYY and MMDDYYYY where we can't always
    # conclude which format a date is in (01022000 -- Jan 2 or Feb 1?).
    # This would require providing matching based on additional context we
    # know, like when we know that a statements subdirectory uses a specific
    # format.
    # TODO(drond-git): Warn and do nothing if two conversions apply to a file.
    # TODO(drond-git): Implement skipping, for random files we can ignore
    # and for YYYYMMDD-YYYYMMDD.ext that represent ranges.
    # TODO(drond-git): Add renaming for filenames that we want sortable even
    # though they don't involve timestamps.
  ]
  for regexp, template in conversions:
    match = re.search(regexp, filename.lower())
    if match:
      return template % MakeKeywords(match.groupdict())
  return None  # None if not matched any renamer expression.


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
