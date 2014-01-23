#!/usr/bin/env python
#123456789.123456789.123456789.123456789.123456789.123456789.123456789.123456789
#
# Tests.


import unittest

from common import app


class ProxyParsedArgsTest(unittest.TestCase):

  def testWhenArgsNotDefined(self):
    self.assertTrue(app.ARGS.PARSER is not None)
    self.assertTrue(app.ARGS.ARGS is None)
    app._setup_parsed_args()
    self.assertTrue(app.ARGS.PARSER is not None)
    self.assertTrue(app.ARGS.ARGS is not None)


if __name__ == '__main__':
    unittest.main()
