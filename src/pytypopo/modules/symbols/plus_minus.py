"""
Fix plus-minus symbol.

Port of src/lib/symbols/plus-minus.js from typopo.
"""

import re

from pytypopo.const import PLUS_MINUS

# Pattern matches +- or -+ combinations
# Chosen over simple string replace to handle all cases in one pass
PLUS_MINUS_PATTERN = re.compile(r"\+\-|\-\+")


def fix_plus_minus(text, locale):
    """
    Fix plus-minus symbol representation.

    Converts '+-' and '-+' to the proper plus-minus symbol (plus/minus).

    Args:
        text: Input text to fix
        locale: Language locale (unused, symbol is universal)

    Returns:
        Text with plus-minus symbols fixed
    """
    return PLUS_MINUS_PATTERN.sub(PLUS_MINUS, text)
