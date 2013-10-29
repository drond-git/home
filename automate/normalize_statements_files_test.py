#!/usr/bin/env python
#
# Tests.
#123456789.123456789.123456789.123456789.123456789.123456789.123456789.123456789

import unittest
import logging

import normalize_statements_files


class ModuleTest(unittest.TestCase):

  def testGenerateDateRangeRegexp(self):
    self.assertEqual(
        ('(P?<year_lower>.)(P?<month_lower>.)(P?<day_lower>.)-'
         '(P?<year_upper>.)(P?<month_upper>.)(P?<day_upper>.)'),
        normalize_statements_files.GenerateDateRangeRegexp(
          '(P?<year>.)', '(P?<month>.)', '(P?<day>.)'))

  def testMakeKeywordsExtOnly(self):
    self.assertEqual(
      {'ext': '.myext',
       'yyyy': 'YYYY',
       'mm': 'MM',
       'dd': 'DD'},
      normalize_statements_files.MakeKeywords({'ext': '.MyExt'}))
      
  def testMakeKeywordsYyyy(self):
    test_values = [
      ({'yyyy': '2000'}, '2000'),
      ({'yy': '13'}, '2013'),
      ({}, 'YYYY')]
    for input, expected_value in test_values:
      keywords = normalize_statements_files.MakeKeywords(input)
      self.assertEqual(keywords.get('yyyy'), expected_value)
      
  def testMakeKeywordsMm(self):
    test_values = [
      ({'mm': '10'}, '10'),
      ({'month': 'february'}, '02'),
      ({'mon': 'mar'}, '03'),
      ({}, 'MM')]
    for input, expected_value in test_values:
      keywords = normalize_statements_files.MakeKeywords(input)
      self.assertEqual(keywords.get('mm'), expected_value)
      
  def testMakeKeywordsDd(self):
    test_values = [
      ({'dd': '31'}, '31'),
      ({}, 'DD')]
    for input, expected_value in test_values:
      keywords = normalize_statements_files.MakeKeywords(input)
      self.assertEqual(keywords.get('dd'), expected_value)
      
  def testIsIgnoredFile(self):
    self.assertTrue(normalize_statements_files.IsFileIgnored('./Icon\r'))
    self.assertTrue(normalize_statements_files.IsFileIgnored('./.DS_Store'))
    self.assertTrue(
        normalize_statements_files.IsFileIgnored('./20010101-20010101.myext'))
    self.assertFalse(normalize_statements_files.IsFileIgnored('./20010101.pdf'))
    self.assertFalse(normalize_statements_files.IsFileIgnored('./some-file'))

  def testTryNormalize(self):
    conversions = [  # Select a sample set of conversions, for testing.
      normalize_statements_files.C_Statement_MM_DD_YY_AccountId,
      normalize_statements_files.C_MMDDYYYY]
    test_values = [
      ('03212011.PDF', '20110321.pdf'),
      ('03232011_extra.PDF', None),
      ('Statement_03-25-11_ABC123.pdf', '20110325_abc123.pdf'),
      ('', None)]
    for filename, filename_new in test_values:
      self.assertEqual(
          filename_new,
          normalize_statements_files.TryNormalize(
              filename, conversions, dry_run=True))

  def testGetRelativeDirpath(self):
    self.assertEqual(
        '', normalize_statements_files.GetRelativeDirpath('/', '/'))
    self.assertEqual(
        'foo', normalize_statements_files.GetRelativeDirpath('/foo', '/'))
    self.assertEqual(
        'baz',
        normalize_statements_files.GetRelativeDirpath(
            '/foo/bar/baz', '/foo/bar'))


if __name__ == '__main__':
    unittest.main()
