"""
Fix exponent symbols: m2 -> m2, m3 -> m3

Port of src/lib/symbols/exponents.js from typopo.
"""

import re

from pytypopo.const import SLASH, SPACES

# Metric prefixes for metre units
# Larger: deca-, hecto-, kilo-, mega-, giga-, tera-, peta-, exa-, zetta-, yotta-
# Smaller: deci-, centi-, milli-, micro-, nano-, pico-, femto-, atto-, zepto-, yocto-
METRE_PREFIXES = (
    "m|"  # base metre
    "dam|hm|km|Mm|Gm|Tm|Pm|Em|Zm|Ym|"  # larger
    "dm|cm|mm|" + "\u00b5m|" + "nm|pm|fm|am|zm|ym"  # smaller (u00b5 = micro sign)
)


def _fix_exponent(text, original, replacement):
    """
    Replace exponent digit with superscript for metric units.

    Pattern requires a space or slash before the unit to prevent
    false positives within words like "Madam2".

    Args:
        text: Input text
        original: Original digit ('2' or '3')
        replacement: Superscript character to use

    Returns:
        Text with exponents fixed
    """
    # Pattern: (space or slash) + metric prefix + exponent digit
    # Word boundary is enforced by requiring space/slash before
    pattern = re.compile(rf"([{SPACES}{SLASH}])({METRE_PREFIXES})({original})\b")
    return pattern.sub(rf"\1\2{replacement}", text)


def fix_exponents(text, locale):
    """
    Fix square and cube exponent symbols for metric units.

    Converts:
    - m2, cm2, km2, etc. -> m2, cm2, km2, etc. (squares)
    - m3, cm3, km3, etc. -> m3, cm3, km3, etc. (cubes)

    Args:
        text: Input text to fix
        locale: Language locale (unused, symbols are universal)

    Returns:
        Text with exponent symbols fixed
    """
    # Fix squares: 2 -> 2
    text = _fix_exponent(text, "2", "\u00b2")

    # Fix cubes: 3 -> 3
    text = _fix_exponent(text, "3", "\u00b3")

    return text
