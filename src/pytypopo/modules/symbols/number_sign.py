"""
Fix number sign (#) spacing.

Port of src/lib/symbols/number-sign.js from typopo.
"""

import re

from pytypopo.const import HAIR_SPACE, NARROW_NBSP, NBSP, NUMBER_SIGN, SPACE

# All space characters that can appear around the number sign
ALL_SPACES = SPACE + NBSP + HAIR_SPACE + NARROW_NBSP

# Pattern to remove extra spaces after # when preceded by a space
# Matches: (spaces before #)(#)(spaces after)(digit)
# Captures spaces before, the #, and the digit - skips spaces after
# Uses lookbehind (?<=...) to require preceding space without consuming it
# This preserves markdown headings at start of string/line
EXTRA_SPACES_PATTERN = re.compile(rf"([{ALL_SPACES}]+)({re.escape(NUMBER_SIGN)})[{ALL_SPACES}]+(\d)")


def remove_extra_spaces_after_number_sign(text, locale):
    """
    Remove extra spaces after the number sign (#).

    Converts '#  9' to '#9'.
    Only acts when # is preceded by space (not at start of line).

    Args:
        text: Input text to fix
        locale: Language locale (unused, behavior is universal)

    Returns:
        Text with extra spaces after number sign removed
    """
    # Replace groups: keep spaces before, keep #, skip middle spaces, keep digit
    return EXTRA_SPACES_PATTERN.sub(r"\1\2\3", text)


def fix_number_sign(text, locale):
    """
    Fix number sign spacing issues.

    Removes extra whitespace between # and the following number,
    while preserving markdown headings at the start of lines.

    Args:
        text: Input text to fix
        locale: Language locale (unused, behavior is universal)

    Returns:
        Text with number sign spacing fixed
    """
    return remove_extra_spaces_after_number_sign(text, locale)
