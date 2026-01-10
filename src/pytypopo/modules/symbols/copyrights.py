"""
Fix copyright symbols: (c) -> (C), (p) -> (P)

Port of src/lib/symbols/copyrights.js from typopo.
"""

import re

from pytypopo.const import COPYRIGHT, SOUND_RECORDING_COPYRIGHT, SPACES


def _replace_copyright(text, letter, symbol):
    """
    Replace parenthesized letter with copyright symbol when followed by a digit.

    Pattern matches (letter) followed by optional spaces and a digit.
    This avoids false positives like "Section 7(c)" by requiring a digit after.

    Args:
        text: Input text
        letter: The letter to match (c or p)
        symbol: The symbol to replace with

    Returns:
        Text with replacements made
    """
    # Pattern: (letter) + optional spaces + digit
    # Must have a digit following to distinguish from section references
    pattern = re.compile(rf"\({letter}\)([{SPACES}]*)(\d)", re.IGNORECASE)
    return pattern.sub(rf"{symbol}\1\2", text)


def fix_copyrights(text, locale):
    """
    Fix copyright and sound recording copyright symbols.

    Converts:
    - (c) and (C) -> (C) (copyright)
    - (p) and (P) -> (P) (sound recording copyright)

    Args:
        text: Input text to fix
        locale: Language locale (unused, symbols are universal)

    Returns:
        Text with copyright symbols fixed
    """
    # Fix copyright symbol (c) -> (C)
    text = _replace_copyright(text, "c", COPYRIGHT)

    # Fix sound recording copyright (p) -> (P)
    text = _replace_copyright(text, "p", SOUND_RECORDING_COPYRIGHT)

    return text
