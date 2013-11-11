#!/usr/bin/env python
#123456789.123456789.123456789.123456789.123456789.123456789.123456789.123456789
#
# Tests.


import unittest
import logging

import common.filesystem as filesystem


class ModuleTest(unittest.TestCase):

  def testGetRelativeDirpath(self):
    self.assertEqual('', filesystem.GetRelativeDirpath('/', '/'))
    self.assertEqual('foo', filesystem.GetRelativeDirpath('/foo', '/'))
    self.assertEqual(
        'baz', filesystem.GetRelativeDirpath('/foo/bar/baz', '/foo/bar'))


class TransformationTest(unittest.TestCase):

  def setUp(self):
    self._t = filesystem.Transformation('unused', 'unused')

  def testTransform(self):
    t = filesystem.Transformation('(?P<foo>\d)(?P<bar>\d)', '%(bar)s%(foo)s')
    self.assertEqual('21', t.Transform('12'))
    self.assertEqual(None, t.Transform('1x'))
    self.assertEqual(None, t.Transform('x2'))
    self.assertEqual(None, t.Transform(''))

  def AssertLexiconConversion(self, name, test_values):
    for tr_dict, expected_value in test_values:
      tr_dict_updated = self._t._CreateLexicon(tr_dict)
      self.assertEqual(tr_dict_updated.get(name), expected_value)

  def testCreateLexiconEmpty(self):
    self.assertEqual(
        {'yyyy': 'YYYY', 'mm': 'MM', 'dd': 'DD'},
        self._t._CreateLexicon({}))

  def testCreateLexiconExt(self):
    test_values = [
        ({'ext': '.MyExt'}, '.myext'),
        ({}, None)]
    self.AssertLexiconConversion('ext', test_values)

  def testCreateLexiconYyyy(self):
    test_values = [
        ({'yyyy': '2000'}, '2000'),
        ({'yy': '13'}, '2013'),
        ({}, 'YYYY')]
    self.AssertLexiconConversion('yyyy', test_values)

  def testCreateLexiconMm(self):
    test_values = [
      ({'mm': '10'}, '10'),
      ({'month': 'february'}, '02'),
      ({'mon': 'mar'}, '03'),
      ({}, 'MM')]
    self.AssertLexiconConversion('mm', test_values)

  def testCreateLexiconDd(self):
    test_values = [
      ({'dd': '31'}, '31'),
      ({}, 'DD')]
    self.AssertLexiconConversion('dd', test_values)

  def testCreateLexiconCheckNumber(self):
    test_values = [
      ({'ordinal_0000': '21'}, '0021'),
      ({}, None)]
    self.AssertLexiconConversion('ordinal_0000', test_values)


if __name__ == '__main__':
    unittest.main()
