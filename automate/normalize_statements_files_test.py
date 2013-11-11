#!/usr/bin/env python
#
# Tests.
#123456789.123456789.123456789.123456789.123456789.123456789.123456789.123456789

import unittest
import logging

from automate import normalize_statements_files


class ModuleTest(unittest.TestCase):

  def testIsIgnoredFile(self):
    self.assertTrue(normalize_statements_files.IsFileIgnored('./Icon\r'))
    self.assertTrue(normalize_statements_files.IsFileIgnored('./.DS_Store'))
    self.assertTrue(
        normalize_statements_files.IsFileIgnored('./20010101-20010101.myext'))
    self.assertFalse(normalize_statements_files.IsFileIgnored('./20010101.pdf'))
    self.assertFalse(normalize_statements_files.IsFileIgnored('./some-file'))

  def testTryNormalize(self):
    """Test various conditions for TryNormalize, using a sample conversion."""
    conversions = [normalize_statements_files.C_Statement_MM_DD_YY_AccountId]
    test_values = [
      ('Statement_03-25-11_ABC123.pdf', '20110325_abc123.pdf'),
      ('totally-different-filename.pdf', None),
      ('', None)]
    for filename, filename_new in test_values:
      self.assertEqual(
          filename_new,
          normalize_statements_files.TryNormalize(
              filename, conversions, dry_run=True))

  def testConversions(self):
    """Test all conversions defined in the tested module."""
    test_values = [
      (normalize_statements_files.C_YYYYMMDD,
       '20120901.PDF', '20120901.pdf'),
      (normalize_statements_files.C_YYYY_MM_DD,
       '2012_09_02.PDF', '20120902.pdf'),
      (normalize_statements_files.C_MMDDYYYY,
       '09032012.PDF', '20120903.pdf'),
      (normalize_statements_files.C_YYYY_MM,
       '2012_09.PDF', '201209DD.pdf'),
      (normalize_statements_files.C_eStmt_YYYY_MM_DD,
       'eStmt_2012-09-04.PDF', '20120904_estmt.pdf'),
      (normalize_statements_files.C_eStmt_MM_DD_YYYY,
       'eStmt_09_05_2012.PDF', '20120905_estmt.pdf'),
      (normalize_statements_files.C_MM_DD_YYYY_AccountId,
       '09_06_2012_2345.PDF', '20120906_2345.pdf'),
      (normalize_statements_files.C_MonthYYYY_AccountId,
       'November2012_7257.QFX', '201211DD_7257.qfx'),
      (normalize_statements_files.C_vanguard_AccountId_YYYYMMDD,
       'vanguard-093926-20120907.PDF', '20120907_093926.pdf'),
      (normalize_statements_files.C_etrade_AccountId_YYYYMMDD,
       'etrade-9433-20120908.PDF', '20120908_9433.pdf'),
      (normalize_statements_files.C_etrade_AccountId_YYYY_MM_DD,
       'etrade-9433-2012_09-10.PDF', '20120910_9433.pdf'),
      (normalize_statements_files.C_ing_AccountId_YYYYMMDD,
       'ing-vf2245-20120911.PDF', '20120911_vf2245.pdf'),
      (normalize_statements_files.C_Statement_MM_DD_YY_AccountId,
       'Statement_09-22-12_7356.PDF', '20120922_7356.pdf'),
      (normalize_statements_files.C_Statement_MON_YYYY,
       'Statement_Feb 2013.PDF', '201302DD.pdf'),
      (normalize_statements_files.C_check_CHECK_NUMBER,
       'check-12.JPG', 'check-0012.jpg'),
      (normalize_statements_files.C_YYYY_year_end,
       '2012-Year End Statement.pdf', '2012_year_end.pdf'),
    ]
    for conversion, filename, filename_new in test_values:
      self.assertEqual(
          filename_new,
          normalize_statements_files.TryNormalize(
              filename, [conversion], dry_run=True))


if __name__ == '__main__':
    unittest.main()
