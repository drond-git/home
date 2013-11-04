#!/usr/bin/env python
#123456789.123456789.123456789.123456789.123456789.123456789.123456789.123456789
#
# Tests.


import unittest
import logging

import common.timestamp as timestamp


class ModuleTest(unittest.TestCase):

  def testGenerateDateRangeRegexp(self):
    self.assertEqual(
        ('(P?<year_lower>.)(P?<month_lower>.)(P?<day_lower>.)-'
         '(P?<year_upper>.)(P?<month_upper>.)(P?<day_upper>.)'),
        timestamp.GenerateDateRangeRegexp(
            '(P?<year>.)', '(P?<month>.)', '(P?<day>.)'))


if __name__ == '__main__':
    unittest.main()
