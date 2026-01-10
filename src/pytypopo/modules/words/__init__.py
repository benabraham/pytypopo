"""
Words module for pytypopo.

Provides functions for:
- Abbreviation spacing (e.g., "e.g.", "i.e.", initials)
- Accidental case correction (CAPSLOCK errors)
- Exception handling (URL, email, filename protection)
- Publication ID formatting (ISBN, ISSN)
"""

from pytypopo.modules.words.abbreviations import (
    fix_abbreviations,
    fix_initials,
    fix_multiple_word_abbreviations,
    fix_single_word_abbreviations,
)
from pytypopo.modules.words.case import fix_case
from pytypopo.modules.words.exceptions import (
    exclude_exceptions,
    place_exceptions,
)
from pytypopo.modules.words.pub_id import (
    fix_isbn10,
    fix_isbn13,
    fix_isbn_number,
    fix_issn,
    fix_pub_id,
)

__all__ = [
    # Abbreviations
    "fix_abbreviations",
    "fix_initials",
    "fix_single_word_abbreviations",
    "fix_multiple_word_abbreviations",
    # Case
    "fix_case",
    # Exceptions
    "exclude_exceptions",
    "place_exceptions",
    # Publication IDs
    "fix_pub_id",
    "fix_issn",
    "fix_isbn10",
    "fix_isbn13",
    "fix_isbn_number",
]
