#!/usr/bin/env python
#
# All statements files should be named consistently. Rename statements
# files in all directories, and list files that were not recognized.
#
#123456789.123456789.123456789.123456789.123456789.123456789.123456789.123456789

import re
import logging
import os

#logging.basicConfig(level=logging.DEBUG)
#logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.WARNING)


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
RE_YY = r'(?P<yy>[0-2]\d|YYYY)'  # 00-29
RE_MM = r'(?P<mm>0\d|1[0-2]|MM)'  # 00-12 or MM
RE_DD = r'(?P<dd>[012]\d|3[01]|DD)'  # 00-31 or DD
RE_EXT = r'(?P<ext>\..+)'  # .pdf
RE_MONTH = r'(?P<month>%s)' % '|'.join(MONTHS_SORTED)  # january-december

# Various formats for presenting account numbers, last four digits, etc.
RE_ACCOUNT_ID = (
    r'(?P<account_id>\d{4,7}|[a-z0-9]{4,7})')


def MakeKeywords(input):
  """Returns the input dict with select key values adjusted."""
  if 'ext' in input:
    # Always lower the extension (this may be redundant now).
    input['ext'] = input['ext'].lower()
  if 'yyyy' not in input:
    # First see if other sources of YYYY are available.
    if 'yy' in input:
      input['yyyy'] = '20%s' % input['yy']
    else:
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


# Define the conversions for use by various accounts directories.
C_YYYYMMDD = (  # 20120930.pdf
   '^%s%s%s%s$' % (RE_YYYY, RE_MM, RE_DD, RE_EXT),
   '%(yyyy)s%(mm)s%(dd)s%(ext)s)')
C_YYYY_MM_DD = (  # 2012_09_30.pdf
   '^%s_%s_%s%s$' % (RE_YYYY, RE_MM, RE_DD, RE_EXT),
   '%(yyyy)s%(mm)s%(dd)s%(ext)s)')
C_MMDDYYYY = (  # 09302012.pdf
   '^%s%s%s%s$' % (RE_DD, RE_MM, RE_YYYY, RE_EXT),
   '%(yyyy)s%(mm)s%(dd)s%(ext)s)')
C_YYYY_MM = (  # 2012_11.pdf
   '^%s%s%s$' % (RE_YYYY, RE_MM, RE_EXT),
   '%(yyyy)s%(mm)s%(dd)s%(ext)s)')
C_eStmt_YYYY_MM_DD = (  # eStmt_2012-09-27.pdf
   '^eStmt_%s-%s-%s%s$' % (RE_YYYY, RE_MM, RE_DD, RE_EXT),
   '%(yyyy)s%(mm)s%(dd)s_eStmt%(ext)s)')
C_eStmt_MM_DD_YYYY = (  # eStmt_09-27-2012.pdf
   '^eStmt_%s-%s-%s%s$' % (RE_MM, RE_DD, RE_YYYY, RE_EXT),
   '%(yyyy)s%(mm)s%(dd)s_eStmt%(ext)s)')
C_MM_DD_YYYY_AccountId = (  # 12_30_2001_2345.pdf
   '^%s_%s_%s_%s%s' % (RE_MM, RE_DD, RE_YYYY, RE_ACCOUNT_ID, RE_EXT),
   '%(yyyy)s%(mm)s%(dd)s_%(account_id)s%(ext)s)')
C_YYYY_MM = (  # 2012_09.pdf
   '^%s_%s%s$' % (RE_YYYY, RE_MM, RE_EXT),
   '%(yyyy)s%(mm)s%(dd)s%(ext)s)')
C_MonthYYYY_AccountId = (  # November2012_7257.qfx
   '^%s%s_%s%s' % (RE_MONTH, RE_YYYY, RE_ACCOUNT_ID, RE_EXT),
   '%(yyyy)s%(mm)s%(dd)s_%(account_id)s%(ext)s)')
C_vanguard_AccountId_YYYYMMDD = (  # vanguard-093926-20110322.pdf
   '^vanguard-%s-%s%s%s%s' % (RE_ACCOUNT_ID, RE_YYYY, RE_MM, RE_DD, RE_EXT),
   '%(yyyy)s%(mm)s%(dd)s_%(account_id)s%(ext)s)')
C_etrade_AccountId_YYYYMMDD = (  # etrade-9433-20110322.pdf
   '^etrade-%s-%s%s%s%s' % (RE_ACCOUNT_ID, RE_YYYY, RE_MM, RE_DD, RE_EXT),
   '%(yyyy)s%(mm)s%(dd)s_%(account_id)s%(ext)s)')
C_etrade_AccountId_YYYY_MM_DD = (  # etrade-9433-2011_03-22.pdf
   '^etrade-%s-%s_%s-%s%s' % (RE_ACCOUNT_ID, RE_YYYY, RE_MM, RE_DD, RE_EXT),
   '%(yyyy)s%(mm)s%(dd)s_%(account_id)s%(ext)s)')
C_ing_AccountId_YYYYMMDD = (  # ing-vf2245-20040930.pdf
   '^ing-%s-%s%s%s%s' % (RE_ACCOUNT_ID, RE_YYYY, RE_MM, RE_DD, RE_EXT),
   '%(yyyy)s%(mm)s%(dd)s_%(account_id)s%(ext)s)')
C_Statement_MM_DD_YY_AccountId = (  # Statement_03-31-13_7356.pdf
   '^Statement_%s-%s-%s_%s%s' % (RE_MM, RE_DD, RE_YY, RE_ACCOUNT_ID, RE_EXT),
   '%(yyyy)s%(mm)s%(dd)s_%(account_id)s%(ext)s)')


# Map account subdirectories to conversions that should apply inside each.
# We can't rely on regexp matching alone and have to be explicit, because
# file timestamps for MMDDYYYY and DDMMYYYY cannot always be distinguished.
# Consider 01022000; is it Jan 2 or Feb 1 od 2000?
ACCOUNT_REGEXP_TO_CONVERSIONS = {
  '^amex-inla': [C_YYYY_MM_DD],
  '^boa-(aaa|checking|quixtar)': [
      C_YYYYMMDD,
      C_MM_DD_YYYY_AccountId,
      C_eStmt_YYYY_MM_DD,
      C_eStmt_MM_DD_YYYY,
      C_MonthYYYY_AccountId],
  '^charles-invest': [C_Statement_MM_DD_YY_AccountId],
  '^chase-loan-subaru': [C_YYYY_MM],
  '^etrade-bank': [
      C_YYYY_MM, C_MMDDYYYY],
  '^etrade-invest': [
      C_etrade_AccountId_YYYYMMDD,
      C_etrade_AccountId_YYYY_MM_DD],
  '^ing-retirement': [C_ing_AccountId_YYYYMMDD],
  '^ladwp': [C_YYYYMMDD],
  '^paypal-sarah': [C_YYYY_MM],
  '^paypal-vitaliy': [C_YYYY_MM],
  '^vanguard-retirement': [C_vanguard_AccountId_YYYYMMDD],
  '^wellsfargo-mortgage': [C_YYYYMMDD],
  'inactive/': [
      C_YYYYMMDD,
      C_MM_DD_YYYY_AccountId,
      ],
}


def TryNormalize(filename, conversions, dry_run=True):
  """If necessary, normalized the file. Returns a tuple."""
  logging.debug('Trying to normalize %r via %r.', filename, conversions)
  # TODO(drond-git): Implement skipping, for random files we can ignore
  # and for YYYYMMDD-YYYYMMDD.ext that represent ranges.
  # TODO(drond-git): Add renaming for filenames that we want sortable even
  # though they don't involve timestamps.
  for regexp, template in conversions:
    logging.debug(
        'Matching %r against %r, for template %r', regexp, filename, template)
    match = re.search(regexp, filename.lower())
    logging.debug('Match is %r', match)
    if match:
      return template % MakeKeywords(match.groupdict())
  return None  # None if not matched any renamer expression.


def ListFilesRecursively(directory):
  """Yields tuple (dirname, basename) for every file below directory."""
  logging.debug('Listing files in %r.', directory)
  for (dirpath, unused_dirnames, filenames) in os.walk(directory):
    for filename in filenames:
      if os.path.isfile(os.path.join(dirpath, filename)):
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


def NormalizeStatementsFiles(statements_root):
  # Find all the files that could possibly be renamed.
  fileset_initial = ListFilesRecursively(statements_root)
  # Partition all files by account directory.
  relative_dirpaths_seen = set()
  relative_dirpath_partitions = {}
  for dirpath, filename in fileset_initial:
    relative_dirpath = GetRelativeDirpath(dirpath, statements_root)
    relative_dirpaths_seen.add(relative_dirpath)
    if relative_dirpath not in relative_dirpath_partitions:
      relative_dirpath_partitions[relative_dirpath] = []
    relative_dirpath_partitions[relative_dirpath].append(filename)
  # Process each partition. Sort its files, get conversions for each.
  relative_dirpath_conversions = {}
  for relative_dirpath in relative_dirpath_partitions:
    relative_dirpath_partitions[relative_dirpath].sort()
    for account_regexp, conversions in (
        ACCOUNT_REGEXP_TO_CONVERSIONS.iteritems()):
      if re.search(account_regexp, relative_dirpath):
        if relative_dirpath not in relative_dirpath_conversions:
          relative_dirpath_conversions[relative_dirpath] = []
        relative_dirpath_conversions[relative_dirpath].append(conversions)
  # Report our current state.
  for relative_dirpath in sorted(relative_dirpaths_seen):
    filenames = relative_dirpath_partitions.get(relative_dirpath, [])
    logging.info('File count in %r: %r', relative_dirpath, len(filenames))
  for relative_dirpath in relative_dirpath_partitions:
    conversions_list = relative_dirpath_conversions.get(relative_dirpath, [])
    logging.info(
        'Conversions for %r: %r', relative_dirpath, len(conversions_list))
  # Now do something useful.
  for relative_dirpath in sorted(relative_dirpath_partitions):
    logging.debug('Processing partition %r', relative_dirpath)
    conversions_list = relative_dirpath_conversions.get(relative_dirpath, [])
    if len(conversions_list) != 1:
      logging.error(
          'Invalid conversions for %r: %r', relative_dirpath, conversions_list)
      conversions = []
    else:
      conversions = conversions_list[0]
    for filename in relative_dirpath_partitions[relative_dirpath]:
      filename_new = TryNormalize(filename, conversions, dry_run=True)
      if not filename_new:
        logging.warning('Unmatched: %r (in %r)', filename, relative_dirpath)
      elif filename_new != filename:
        logging.info(
            'Renamed: %r %r (in %r)',
            filename, filename_new, relative_dirpath)

      
def main():
  NormalizeStatementsFiles(STATEMENTS_ROOT_DIR)


if __name__ == '__main__':
  main()
