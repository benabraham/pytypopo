"""
Fix section sign (section) and paragraph sign (paragraph) spacing.

Port of src/lib/symbols/section-sign.js from typopo.
"""

import re

from pytypopo.const import (
    HAIR_SPACE,
    NARROW_NBSP,
    NBSP,
    PARAGRAPH_SIGN,
    SECTION_SIGN,
    SPACE,
)

# All space characters
ALL_SPACES = SPACE + NBSP + HAIR_SPACE + NARROW_NBSP


def fix_spacing_around_symbol(text, symbol, space_after):
    """
    Fix spacing around a symbol (section/paragraph/numero sign).

    Three transformations:
    1. Add space before symbol when preceded by non-space, non-opening-bracket
    2. Replace any spaces after symbol with the correct space_after character
    3. Add space_after when symbol directly followed by alphanumeric

    Args:
        text: Input text to fix
        symbol: The symbol to fix spacing around
        space_after: The space character to use after the symbol

    Returns:
        Text with spacing fixed around the symbol
    """
    escaped_symbol = re.escape(symbol)

    # Step 1: Add space before symbol when preceded by word/punctuation/closing chars
    # Matches: (letter, digit, punctuation, closing bracket, quote) directly followed by symbol(s)
    # Excludes: spaces and opening brackets before the symbol
    add_space_before = re.compile(rf"([^\s\(\[\{{{escaped_symbol}])({escaped_symbol}+)")
    text = add_space_before.sub(r"\1 \2", text)

    # Step 2: Replace any existing spaces after symbol with proper space_after
    # Matches: symbol(s) followed by one or more spaces
    replace_spaces_after = re.compile(rf"({escaped_symbol}+)[{ALL_SPACES}]+")
    text = replace_spaces_after.sub(rf"\1{space_after}", text)

    # Step 3: Add space_after when symbol directly followed by word char (letter/digit)
    # Matches: symbol(s) directly followed by alphanumeric
    add_space_after = re.compile(rf"({escaped_symbol}+)(\w)")
    text = add_space_after.sub(rf"\1{space_after}\2", text)

    return text


def fix_section_sign(text, locale):
    """
    Fix spacing around section (section) and paragraph (paragraph) signs.

    Ensures proper spacing before and after these symbols,
    using locale-appropriate spacing after the symbol.

    Args:
        text: Input text to fix
        locale: Language locale (determines spacing after symbol)

    Returns:
        Text with section and paragraph sign spacing fixed
    """
    # For all locales, use narrow nbsp after section/paragraph signs
    space_after = NARROW_NBSP

    text = fix_spacing_around_symbol(text, SECTION_SIGN, space_after)
    text = fix_spacing_around_symbol(text, PARAGRAPH_SIGN, space_after)

    return text
