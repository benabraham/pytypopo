"""
Period fixes: removes double/multiple periods.

Port of src/modules/punctuation/period.js from typopo.
"""

import re

# Pattern to match two or more consecutive periods
# Excludes patterns followed by / or \ (file paths like ../ or ..\)
_EXTRA_PERIOD_PATTERN = re.compile(r"\.{2,}(?![/\\])")


def remove_extra_period(text, locale=None):
    """
    Replace multiple consecutive periods with a single period.

    Preserves relative path notations like ../ and ..\\

    Args:
        text: Input text to process
        locale: Locale identifier (unused, for API consistency)

    Returns:
        Text with multiple periods collapsed to single period
    """
    return _EXTRA_PERIOD_PATTERN.sub(".", text)


def fix_period(text, locale=None):
    """
    Fix period-related typography issues.

    Currently fixes:
    - Multiple consecutive periods → single period (except file paths)

    Args:
        text: Input text to process
        locale: Locale identifier (unused, for API consistency)

    Returns:
        Text with period fixes applied
    """
    return remove_extra_period(text, locale)
