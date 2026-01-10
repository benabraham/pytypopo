"""
Fix trademark/service mark symbols: (r) -> (R), (tm) -> (TM), (sm) -> (SM)

Port of src/lib/symbols/marks.js from typopo.
"""

import re

from pytypopo.const import REGISTERED_TRADEMARK, SERVICE_MARK, SPACES, TRADEMARK


def _replace_mark(text, mark_pattern, symbol):
    """
    Replace parenthesized mark with symbol, removing preceding spaces.

    Pattern matches non-digit + optional spaces + (mark) or existing symbol.
    The non-digit requirement avoids false positives like "Section 7(r)".
    Spaces before the mark are removed.

    Args:
        text: Input text
        mark_pattern: Pattern to match in parentheses (r, tm, sm)
        symbol: The symbol to replace with

    Returns:
        Text with replacements made
    """
    # Pattern: (non-digit or start) + optional spaces + ((mark) or symbol)
    # [^0-9] avoids false positives after numbers (e.g., "Section 7(r)")
    # Also handles existing symbols that need spacing fixed
    pattern = re.compile(rf"([^0-9]|^)([{SPACES}]*)(\({mark_pattern}\)|{re.escape(symbol)})", re.IGNORECASE)
    return pattern.sub(rf"\1{symbol}", text)


def fix_marks(text, locale):
    """
    Fix trademark and service mark symbols.

    Converts:
    - (r) and (R) -> (R) (registered trademark)
    - (tm) and (TM) -> (TM) (trademark)
    - (sm) and (SM) -> (SM) (service mark)

    Also removes extra spaces before the mark symbol.

    Args:
        text: Input text to fix
        locale: Language locale (unused, symbols are universal)

    Returns:
        Text with mark symbols fixed
    """
    # Fix registered trademark (r) -> (R)
    text = _replace_mark(text, "r", REGISTERED_TRADEMARK)

    # Fix trademark (tm) -> (TM)
    text = _replace_mark(text, "tm", TRADEMARK)

    # Fix service mark (sm) -> (SM)
    text = _replace_mark(text, "sm", SERVICE_MARK)

    return text
