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


if __name__ == '__main__':
    unittest.main()
