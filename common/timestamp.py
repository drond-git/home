#!/usr/bin/env python
#123456789.123456789.123456789.123456789.123456789.123456789.123456789.123456789
#
# Utilities for working with timestamps and things related.


import logging
import re


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
