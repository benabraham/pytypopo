"""
Line handling: remove excessive empty lines.

Port of src/modules/whitespace/lines.js from typopo.
"""

import re


def fix_lines(text, locale):
    """
    Remove excessive empty lines from text.

    Collapses two or more consecutive newlines (or carriage returns)
    into a single newline.

    Args:
        text: Input text to fix
        locale: Language locale (unused, behavior is universal)

    Returns:
        Text with excessive empty lines removed
    """
    # Pattern matches 2+ consecutive newlines or carriage returns
    # Uses multiline mode for line-by-line processing
    return re.sub(r"[\n\r]{2,}", "\n", text)
