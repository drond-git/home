#!/usr/bin/env python
#123456789.123456789.123456789.123456789.123456789.123456789.123456789.123456789
#
# All statements files should be named consistently. Rename statements
# files in all directories, and list files that were not recognized.
#

import re
import logging
import os

from common import timestamp
from common import filesystem


logging.basicConfig(level=logging.WARNING)
#logging.basicConfig(level=logging.INFO)
#logging.basicConfig(level=logging.DEBUG)


# The directory where to look for statements files.
STATEMENTS_ROOT_DIR = (
    '/Users/vsh/Personal/Google Drive/drond-cloud/gtd/refs/finances/'
    'statements')


# Various formats for presenting less fundamental patterns.
RE_ACCOUNT_ID = r'(?P<account_id>\d{4,7}|[a-z0-9]{4,7})'


T = filesystem.Transformation


RE_DATE_RANGE = timestamp.GenerateDateRangeRegexp(T.RE_YYYY, T.RE_MM, T.RE_DD)


# Define the conversions for use by various accounts directories.
# WARNING: Filename regexp will not match anything fi it expects
# uppercase letters -- we match against filename.lower().
C_YYYYMMDD = T(  # 20120930.pdf
   '^%s%s%s%s$' % (T.RE_YYYY, T.RE_MM, T.RE_DD, T.RE_EXT),
   '%(yyyy)s%(mm)s%(dd)s%(ext)s')
C_YYYY_MM_DD = T(  # 2012_09_30.pdf
   '^%s_%s_%s%s$' % (T.RE_YYYY, T.RE_MM, T.RE_DD, T.RE_EXT),
   '%(yyyy)s%(mm)s%(dd)s%(ext)s')
C_MMDDYYYY = T(  # 09302012.pdf
   '^%s%s%s%s$' % (T.RE_MM, T.RE_DD, T.RE_YYYY, T.RE_EXT),
   '%(yyyy)s%(mm)s%(dd)s%(ext)s')
C_YYYY_MM = T(  # 2012_11.pdf
   '^%s%s%s$' % (T.RE_YYYY, T.RE_MM, T.RE_EXT),
   '%(yyyy)s%(mm)s%(dd)s%(ext)s')
C_eStmt_YYYY_MM_DD = T(  # eStmt_2012-09-27.pdf
   '^estmt_%s-%s-%s%s$' % (T.RE_YYYY, T.RE_MM, T.RE_DD, T.RE_EXT),
   '%(yyyy)s%(mm)s%(dd)s_estmt%(ext)s')
C_eStmt_MM_DD_YYYY = T(  # eStmt_09_27_2012.pdf
   '^estmt_%s_%s_%s%s$' % (T.RE_MM, T.RE_DD, T.RE_YYYY, T.RE_EXT),
   '%(yyyy)s%(mm)s%(dd)s_estmt%(ext)s')
C_MM_DD_YYYY_AccountId = T(  # 12_30_2001_2345.pdf
   '^%s_%s_%s_%s%s' % (T.RE_MM, T.RE_DD, T.RE_YYYY, RE_ACCOUNT_ID, T.RE_EXT),
   '%(yyyy)s%(mm)s%(dd)s_%(account_id)s%(ext)s')
C_YYYY_MM = T(  # 2012_09.pdf
   '^%s_%s%s$' % (T.RE_YYYY, T.RE_MM, T.RE_EXT),
   '%(yyyy)s%(mm)s%(dd)s%(ext)s')
C_MonthYYYY_AccountId = T(  # November2012_7257.qfx
   '^%s%s_%s%s' % (T.RE_MONTH, T.RE_YYYY, RE_ACCOUNT_ID, T.RE_EXT),
   '%(yyyy)s%(mm)s%(dd)s_%(account_id)s%(ext)s')
C_vanguard_AccountId_YYYYMMDD = T(  # vanguard-093926-20110322.pdf
   '^vanguard-%s-%s%s%s%s' % (RE_ACCOUNT_ID, T.RE_YYYY, T.RE_MM, T.RE_DD, T.RE_EXT),
   '%(yyyy)s%(mm)s%(dd)s_%(account_id)s%(ext)s')
C_etrade_AccountId_YYYYMMDD = T(  # etrade-9433-20110322.pdf
   '^etrade-%s-%s%s%s%s' % (RE_ACCOUNT_ID, T.RE_YYYY, T.RE_MM, T.RE_DD, T.RE_EXT),
   '%(yyyy)s%(mm)s%(dd)s_%(account_id)s%(ext)s')
C_etrade_AccountId_YYYY_MM_DD = T(  # etrade-9433-2011_03-22.pdf
   '^etrade-%s-%s_%s-%s%s' % (RE_ACCOUNT_ID, T.RE_YYYY, T.RE_MM, T.RE_DD, T.RE_EXT),
   '%(yyyy)s%(mm)s%(dd)s_%(account_id)s%(ext)s')
C_ing_AccountId_YYYYMMDD = T(  # ing-vf2245-20040930.pdf
   '^ing-%s-%s%s%s%s' % (RE_ACCOUNT_ID, T.RE_YYYY, T.RE_MM, T.RE_DD, T.RE_EXT),
   '%(yyyy)s%(mm)s%(dd)s_%(account_id)s%(ext)s')
C_Statement_MM_DD_YY_AccountId = T(  # Statement_03-31-13_7356.pdf
   '^statement_%s-%s-%s_%s%s' % (T.RE_MM, T.RE_DD, T.RE_YY, RE_ACCOUNT_ID, T.RE_EXT),
   '%(yyyy)s%(mm)s%(dd)s_%(account_id)s%(ext)s')
C_Statement_MON_YYYY = T(  # Statement_Feb 2013.pdf
   r'^statement_%s %s%s' % (T.RE_MON, T.RE_YYYY, T.RE_EXT),
   '%(yyyy)s%(mm)s%(dd)s%(ext)s')
C_check_CHECK_NUMBER = T(  # check-1002.jpg
   r'^check-%s%s' % (T.RE_ORDINAL_0000, T.RE_EXT),
   'check-%(ordinal_0000)s%(ext)s')
C_YYYY_year_end = T(  # 2012-Year End Statement.pdf
   r'^%s(?:.*[Yy]ear.*[Ee]nd.*)%s' % (T.RE_YYYY, T.RE_EXT),
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
      '%s%s' % (RE_DATE_RANGE, T.RE_EXT)]:
    if re.search(regexp, filepath):
      is_ignored = True
      break
  if is_ignored:
    logging.debug('Ignored: %r', filepath)
  return is_ignored


def TryNormalize(filename, transformations, dry_run=True):
  """If necessary, normalize the file. Returns new filename or None."""
  logging.debug('Trying to normalize %r via %r.', filename, transformations)
  # TODO(drond-git): Add renaming for filenames that we want sortable even
  # though they don't involve timestamps.
  for t in transformations:
    name = t.Transform(filename)
    if name is not None:
      return name
  return None  # None if not matched any renamer expression.


def NormalizeStatementsFiles(statements_root):
  # Find all the files that could possibly be renamed.
  fileset_initial = filesystem.ListFilesRecursively(
      statements_root, filter_func=IsFileIgnored)
  # Partition all files by account directory.
  relative_dirpaths_seen = set()
  relative_dirpath_partitions = {}
  for dirpath, filename in fileset_initial:
    relative_dirpath = filesystem.GetRelativeDirpath(dirpath, statements_root)
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
      filename_new = None
      for transformation in conversions:
        filename_new = transformation.Transform(filename)
        if filename_new:
          break
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
