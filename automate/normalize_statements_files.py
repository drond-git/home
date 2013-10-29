#!/usr/bin/env python
#
# All statements files should be named consistently. Rename statements
# files in all directories, and list files that were not recognized.
#
#123456789.123456789.123456789.123456789.123456789.123456789.123456789.123456789

import re
import logging
import os

logging.basicConfig(level=logging.WARNING)
#logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.DEBUG)


# The directory where to look for statements files.
STATEMENTS_ROOT_DIR = (
    '/Users/vsh/Personal/Google Drive/drond-cloud/gtd/refs/finances/'
    'statements')


MONTHS_SORTED = (
    'january', 'february', 'march', 'april', 'may', 'june',
    'july', 'august', 'september', 'october', 'november', 'december')
MONS_SORTED = (
    'jan', 'feb', 'mar', 'apr', 'may', 'jun',
    'jul', 'aug', 'sep', 'oct', 'nov', 'dec')


RE_YYYY = r'(?P<yyyy>20[0-2]\d|YYYY)'  # 2000-2029 or YYYY
RE_YY = r'(?P<yy>[0-2]\d|YYYY)'  # 00-29
RE_MM = r'(?P<mm>0\d|1[0-2]|MM)'  # 00-12 or MM
RE_DD = r'(?P<dd>[012]\d|3[01]|DD)'  # 00-31 or DD
RE_EXT = r'(?P<ext>\..+)'  # .pdf
RE_MONTH = r'(?P<month>%s)' % '|'.join(MONTHS_SORTED)  # january-december
RE_MON = r'(?P<mon>%s)' % '|'.join(MONS_SORTED)  # jan-dec

# Various formats for presenting less fundamental patterns.
RE_ACCOUNT_ID = r'(?P<account_id>\d{4,7}|[a-z0-9]{4,7})'
RE_CHECK_NUMBER = r'(?P<check_number>\d{1,4})'

def GenerateDateRangeRegexp(re_yyyy, re_mm, re_dd):
  """Compose a matcher for YYYYMMDD-YYYYMMDD from YYYY, MM, DD regexps."""

  def AddSuffix(re_with_p, suffix):
    """Returns re_with_p copy with "?P<name>" --> "?P<namesuffix>"."""
    return re.sub(r'>', '%s>' % suffix, re_with_p, count=1)

  # This is necessary to be able to reuse the RE_YYYY that are defined
  # with ?P<name> attributes. Each RE_* has to be used twice, so we have
  # to edit re definitions.
  re_yyyy_lower = AddSuffix(re_yyyy, '_lower')
  re_yyyy_upper = AddSuffix(re_yyyy, '_upper')
  re_mm_lower = AddSuffix(re_mm, '_lower')
  re_mm_upper = AddSuffix(re_mm, '_upper')
  re_dd_lower = AddSuffix(re_dd, '_lower')
  re_dd_upper = AddSuffix(re_dd, '_upper')
  re_date_range = '%s%s%s-%s%s%s' % (
      re_yyyy_lower, re_mm_lower, re_dd_lower,
      re_yyyy_upper, re_mm_upper, re_dd_upper)
  logging.debug('RE_DATE_RANGE: %r', re_date_range)
  return re_date_range


RE_DATE_RANGE = GenerateDateRangeRegexp(RE_YYYY, RE_MM, RE_DD)


def GenerateMmByMonthMap(months):
  mm_by_month_map = {}
  for i, month in enumerate(months):
      mm_by_month_map[month] = '%02d' % (i + 1)
  return mm_by_month_map


MM_BY_MONTH_MAP = GenerateMmByMonthMap(MONTHS_SORTED)
MM_BY_MON_MAP = GenerateMmByMonthMap(MONS_SORTED)


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
    elif 'mon' in input:
      input['mm'] = MM_BY_MON_MAP[input['mon'].lower()]
    else:
      # Put something visibly wrong in the MM field, if absent.
      input['mm'] = 'MM'
  if 'dd' not in input:
    # Put something visibly wrong in the DD field, if absent.
    input['dd'] = 'DD'
  if 'check_number' in input:
    input['check_number'] = '%04d' % int(input['check_number'])
  return input


# Define the conversions for use by various accounts directories.
# WARNING: Filename regexp will not match anything fi it expects
# uppercase letters -- we match against filename.lower().
C_YYYYMMDD = (  # 20120930.pdf
   '^%s%s%s%s$' % (RE_YYYY, RE_MM, RE_DD, RE_EXT),
   '%(yyyy)s%(mm)s%(dd)s%(ext)s')
C_YYYY_MM_DD = (  # 2012_09_30.pdf
   '^%s_%s_%s%s$' % (RE_YYYY, RE_MM, RE_DD, RE_EXT),
   '%(yyyy)s%(mm)s%(dd)s%(ext)s')
C_MMDDYYYY = (  # 09302012.pdf
   '^%s%s%s%s$' % (RE_MM, RE_DD, RE_YYYY, RE_EXT),
   '%(yyyy)s%(mm)s%(dd)s%(ext)s')
C_YYYY_MM = (  # 2012_11.pdf
   '^%s%s%s$' % (RE_YYYY, RE_MM, RE_EXT),
   '%(yyyy)s%(mm)s%(dd)s%(ext)s')
C_eStmt_YYYY_MM_DD = (  # eStmt_2012-09-27.pdf
   '^estmt_%s-%s-%s%s$' % (RE_YYYY, RE_MM, RE_DD, RE_EXT),
   '%(yyyy)s%(mm)s%(dd)s_estmt%(ext)s')
C_eStmt_MM_DD_YYYY = (  # eStmt_09_27_2012.pdf
   '^estmt_%s_%s_%s%s$' % (RE_MM, RE_DD, RE_YYYY, RE_EXT),
   '%(yyyy)s%(mm)s%(dd)s_estmt%(ext)s')
C_MM_DD_YYYY_AccountId = (  # 12_30_2001_2345.pdf
   '^%s_%s_%s_%s%s' % (RE_MM, RE_DD, RE_YYYY, RE_ACCOUNT_ID, RE_EXT),
   '%(yyyy)s%(mm)s%(dd)s_%(account_id)s%(ext)s')
C_YYYY_MM = (  # 2012_09.pdf
   '^%s_%s%s$' % (RE_YYYY, RE_MM, RE_EXT),
   '%(yyyy)s%(mm)s%(dd)s%(ext)s')
C_MonthYYYY_AccountId = (  # November2012_7257.qfx
   '^%s%s_%s%s' % (RE_MONTH, RE_YYYY, RE_ACCOUNT_ID, RE_EXT),
   '%(yyyy)s%(mm)s%(dd)s_%(account_id)s%(ext)s')
C_vanguard_AccountId_YYYYMMDD = (  # vanguard-093926-20110322.pdf
   '^vanguard-%s-%s%s%s%s' % (RE_ACCOUNT_ID, RE_YYYY, RE_MM, RE_DD, RE_EXT),
   '%(yyyy)s%(mm)s%(dd)s_%(account_id)s%(ext)s')
C_etrade_AccountId_YYYYMMDD = (  # etrade-9433-20110322.pdf
   '^etrade-%s-%s%s%s%s' % (RE_ACCOUNT_ID, RE_YYYY, RE_MM, RE_DD, RE_EXT),
   '%(yyyy)s%(mm)s%(dd)s_%(account_id)s%(ext)s')
C_etrade_AccountId_YYYY_MM_DD = (  # etrade-9433-2011_03-22.pdf
   '^etrade-%s-%s_%s-%s%s' % (RE_ACCOUNT_ID, RE_YYYY, RE_MM, RE_DD, RE_EXT),
   '%(yyyy)s%(mm)s%(dd)s_%(account_id)s%(ext)s')
C_ing_AccountId_YYYYMMDD = (  # ing-vf2245-20040930.pdf
   '^ing-%s-%s%s%s%s' % (RE_ACCOUNT_ID, RE_YYYY, RE_MM, RE_DD, RE_EXT),
   '%(yyyy)s%(mm)s%(dd)s_%(account_id)s%(ext)s')
C_Statement_MM_DD_YY_AccountId = (  # Statement_03-31-13_7356.pdf
   '^statement_%s-%s-%s_%s%s' % (RE_MM, RE_DD, RE_YY, RE_ACCOUNT_ID, RE_EXT),
   '%(yyyy)s%(mm)s%(dd)s_%(account_id)s%(ext)s')
C_Statement_MON_YYYY = (  # Statement_Feb 2013.pdf
   r'^statement_%s %s%s' % (RE_MON, RE_YYYY, RE_EXT),
   '%(yyyy)s%(mm)s%(dd)s%(ext)s')
C_check_CHECK_NUMBER = (  # check-1002.jpg
   r'^check-%s%s' % (RE_CHECK_NUMBER, RE_EXT),
   'check-%(check_number)s%(ext)s')
C_YYYY_year_end = (  # 2012-Year End Statement.pdf
   r'^%s(?:.*[Yy]ear.*[Ee]nd.*)%s' % (RE_YYYY, RE_EXT),
   '%(yyyy)s_year_end%(ext)s')


# Map account subdirectories to conversions that should apply inside each.
# We can't rely on regexp matching alone and have to be explicit, because
# file timestamps for MMDDYYYY and DDMMYYYY cannot always be distinguished.
# Consider 01022000; is it Jan 2 or Feb 1 od 2000?
ACCOUNT_REGEXP_TO_CONVERSIONS = {
  '^amex-inla': [C_Statement_MON_YYYY, C_YYYY_MM_DD],
  '^boa-(aaa|checking|quixtar)': [
      C_YYYYMMDD, C_MM_DD_YYYY_AccountId, C_MonthYYYY_AccountId,
      C_eStmt_YYYY_MM_DD, C_eStmt_MM_DD_YYYY, C_check_CHECK_NUMBER,
      C_YYYY_year_end],
  '^charles-invest': [C_Statement_MM_DD_YY_AccountId],
  '^chase-loan-subaru': [C_YYYY_MM],
  '^etrade-bank': [C_YYYY_MM, C_MMDDYYYY],
  '^etrade-invest': [
      C_etrade_AccountId_YYYYMMDD, C_etrade_AccountId_YYYY_MM_DD],
  '^ing-retirement': [C_ing_AccountId_YYYYMMDD],
  '^ladwp': [C_YYYYMMDD],
  '^paypal-sarah': [C_YYYY_MM],
  '^paypal-vitaliy': [C_YYYY_MM],
  '^vanguard-retirement': [C_vanguard_AccountId_YYYYMMDD],
  '^wellsfargo-mortgage': [C_YYYYMMDD],
  '^morgan-invest': [C_YYYY_year_end],
  'inactive/': [
      C_YYYYMMDD, C_MM_DD_YYYY_AccountId, C_eStmt_YYYY_MM_DD,
      C_check_CHECK_NUMBER],
}


def IsFileIgnored(filepath):
  """Returns True is the filepath should be ignored for processing."""
  is_ignored = False
  for regexp in [
      '/Icon\r$',
      '/desktop.ini$',
      '/.DS_Store$',
      '%s%s' % (RE_DATE_RANGE, RE_EXT)]:
    if re.search(regexp, filepath):
      is_ignored = True
      break
  if is_ignored:
    logging.debug('Ignored: %r', filepath)
  return is_ignored


def TryNormalize(filename, conversions, dry_run=True):
  """If necessary, normalize the file. Returns new filename or None."""
  logging.debug('Trying to normalize %r via %r.', filename, conversions)
  # TODO(drond-git): Add renaming for filenames that we want sortable even
  # though they don't involve timestamps.
  for regexp, template in conversions:
    match_value = filename.lower()
    logging.debug(
        'Matching %r against %r, for template %r',
      match_value, regexp, template)
    match = re.search(regexp, match_value)
    logging.debug('Match is %r', match)
    if match:
      return template % MakeKeywords(match.groupdict())
  return None  # None if not matched any renamer expression.


def ListFilesRecursively(directory, filter_func=None):
  """Yields tuple (dirname, basename) for every file below directory."""
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


def NormalizeStatementsFiles(statements_root):
  # Find all the files that could possibly be renamed.
  fileset_initial = ListFilesRecursively(
      statements_root, filter_func=IsFileIgnored)
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
