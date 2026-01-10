"""
Fix publication identifiers: ISBN and ISSN formatting.

Normalizes spacing and hyphenation for:
- ISSN: International Standard Serial Number (8 digits)
- ISBN-10: 10-digit ISBN
- ISBN-13: 13-digit ISBN

Port of src/modules/words/pub-id.js from typopo.
"""

import re

from pytypopo.const import (
    EM_DASH,
    EN_DASH,
    HYPHEN,
    NBSP,
    SPACES,
)

# Pattern for spaces and dashes that may appear between digits
_DASHED_SPACE = rf"[{SPACES}]?[{HYPHEN}{EN_DASH}{EM_DASH}][{SPACES}]?"


def fix_issn(text):
    """
    Fix ISSN formatting.

    ISSN format: ISSN XXXX-XXXX (8 digits with hyphen in middle)

    Args:
        text: Input text

    Returns:
        Text with ISSN properly formatted
    """
    # Pattern: issn + optional colon + space + 4 digits + dash + 4 digits
    pattern = re.compile(
        r"(issn)"  # ISSN prefix (case insensitive)
        r"(:?)"  # Optional colon
        rf"([{SPACES}]?)"  # Optional space
        r"(\d{4})"  # First 4 digits
        rf"({_DASHED_SPACE})"  # Dash with optional spaces
        r"(\d{4})",  # Last 4 digits
        re.IGNORECASE,
    )

    return pattern.sub(rf"ISSN\2{NBSP}\4-\6", text)


def fix_isbn10(text):
    """
    Fix ISBN-10 formatting.

    ISBN-10 format: ISBN X-XXX-XXXXX-X (10 digits with 3 hyphens)
    Last digit can be X (representing 10 in check digit calculation)

    Args:
        text: Input text

    Returns:
        Text with ISBN-10 properly formatted
    """
    pattern = re.compile(
        r"(isbn)"  # ISBN prefix
        r"(:?)"  # Optional colon
        rf"([{SPACES}]?)"  # Optional space
        r"(\d+)"  # First group of digits
        rf"({_DASHED_SPACE})"  # Dash
        r"(\d+)"  # Second group
        rf"({_DASHED_SPACE})"  # Dash
        r"(\d+)"  # Third group
        rf"({_DASHED_SPACE})"  # Dash
        r"(X|\d+)",  # Last digit (can be X)
        re.IGNORECASE,
    )

    return pattern.sub(rf"ISBN\2{NBSP}\4-\6-\8-\10", text)


def fix_isbn13(text):
    """
    Fix ISBN-13 formatting.

    ISBN-13 format: ISBN XXX-X-XXX-XXXXX-X (13 digits with 4 hyphens)

    Args:
        text: Input text

    Returns:
        Text with ISBN-13 properly formatted
    """
    pattern = re.compile(
        r"(isbn)"  # ISBN prefix
        r"(:?)"  # Optional colon
        rf"([{SPACES}]?)"  # Optional space
        r"(\d+)"  # First group (978 or 979)
        rf"({_DASHED_SPACE})"  # Dash
        r"(\d+)"  # Second group
        rf"({_DASHED_SPACE})"  # Dash
        r"(\d+)"  # Third group
        rf"({_DASHED_SPACE})"  # Dash
        r"(\d+)"  # Fourth group
        rf"({_DASHED_SPACE})"  # Dash
        r"(X|\d+)",  # Last digit (can be X)
        re.IGNORECASE,
    )

    return pattern.sub(rf"ISBN\2{NBSP}\4-\6-\8-\10-\12", text)


def fix_isbn_number(text):
    """
    Fix bare ISBN numbers (without ISBN prefix).

    Normalizes hyphenation for standalone ISBN-like numbers.

    Args:
        text: Input text

    Returns:
        Text with ISBN numbers properly hyphenated
    """
    pattern = re.compile(
        r"(\d+)"  # First group
        rf"({_DASHED_SPACE})"  # Dash
        r"(\d+)"  # Second group
        rf"({_DASHED_SPACE})"  # Dash
        r"(\d+)"  # Third group
        rf"({_DASHED_SPACE})"  # Dash
        r"(\d+)"  # Fourth group
        rf"({_DASHED_SPACE})"  # Dash
        r"(X|\d+?)"  # Last digit (can be X)
    )

    return pattern.sub(r"\1-\3-\5-\7-\9", text)


def fix_pub_id(text):
    """
    Fix all publication identifier formatting.

    Applies fixes for ISSN, ISBN-10, and ISBN-13 formats.

    Args:
        text: Input text

    Returns:
        Text with publication identifiers properly formatted
    """
    text = fix_issn(text)
    text = fix_isbn10(text)
    text = fix_isbn13(text)
    text = fix_isbn_number(text)
    return text
