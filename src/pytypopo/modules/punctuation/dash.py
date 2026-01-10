"""
Dash fixes: hyphens to en/em dashes, spacing around dashes.

Port of src/modules/punctuation/dash.js from typopo.

Handles:
- Dashes between words (locale-specific em/en dash with appropriate spacing)
- Dashes before punctuation marks
- Dashes around brackets
- Dashes between cardinal numbers (number ranges)
- Dashes between percentage ranges
- Dashes between ordinal numbers (locale-specific)
"""

import re

from pytypopo.const import (
    ALL_CHARS,
    CLOSING_BRACKETS,
    EM_DASH,
    EN_DASH,
    HYPHEN,
    OPENING_BRACKETS,
    PERCENT,
    PERMILLE,
    PERMYRIAD,
    SENTENCE_PUNCTUATION,
    SPACES,
)
from pytypopo.locale.base import get_locale
from pytypopo.utils.regex_overlap import replace_with_overlap_handling


def _get_locale_obj(locale):
    """Convert locale string to Locale object if needed."""
    if isinstance(locale, str):
        return get_locale(locale)
    return locale


def fix_dashes_between_words(text, locale):
    """
    Fix dashes between words or between a word and a number.

    Identifies improperly used hyphens with spaces around them, or
    improperly used/spaced en/em dashes between words, and replaces
    with locale-specific dash and spacing.

    Args:
        text: Input text to process
        locale: Locale identifier or Locale object

    Returns:
        Text with fixed dashes between words
    """
    loc = _get_locale_obj(locale)

    # Pattern matches:
    # - Word/digit followed by
    # - Dash(es) with optional spaces (but hyphen requires spaces on both sides)
    # - Word/digit
    #
    # Two alternatives:
    # 1. Any spaces + en/em dash(es) + any spaces
    # 2. Required spaces + hyphen(s) + required spaces
    pattern = re.compile(
        rf"([{ALL_CHARS}\d])"
        rf"("
        rf"[{SPACES}]*[{EN_DASH}{EM_DASH}]{{1,3}}[{SPACES}]*"
        rf"|"
        rf"[{SPACES}]+[{HYPHEN}]{{1,3}}[{SPACES}]+"
        rf")"
        rf"([{ALL_CHARS}\d])"
    )

    replacement = rf"\1{loc.dash_space_before}{loc.dash_char}{loc.dash_space_after}\3"
    return pattern.sub(replacement, text)


def fix_dash_between_word_and_punctuation(text, locale):
    """
    Fix dashes between words and punctuation marks or at end of paragraph.

    Replaces hyphen or dash placed between a word and punctuation,
    or at the end of a paragraph, with locale-specific dash and spacing.

    Args:
        text: Input text to process
        locale: Locale identifier or Locale object

    Returns:
        Text with fixed dashes before punctuation
    """
    loc = _get_locale_obj(locale)

    # Pattern matches:
    # - Letter followed by
    # - Optional space, 1-3 dashes, optional space
    # - Punctuation mark or newline
    pattern = re.compile(
        rf"([{ALL_CHARS}])"
        rf"([{SPACES}]?)"
        rf"([{HYPHEN}{EN_DASH}{EM_DASH}]{{1,3}})"
        rf"([{SPACES}]?)"
        rf"([{SENTENCE_PUNCTUATION}]|\n|\r)"
    )

    replacement = rf"\1{loc.dash_space_before}{loc.dash_char}\5"
    return pattern.sub(replacement, text)


def fix_dash_between_word_and_brackets(text, locale):
    """
    Fix dashes between words and brackets.

    Handles various patterns:
    - Word + dash + opening bracket
    - Closing bracket + dash + word
    - Opening bracket + dash + word
    - Word + dash + closing bracket
    - Closing bracket + dash + opening bracket
    - Dashes within brackets (only removes spaces, preserves dash type)

    Args:
        text: Input text to process
        locale: Locale identifier or Locale object

    Returns:
        Text with fixed dashes around brackets
    """
    loc = _get_locale_obj(locale)
    dash_replacement = f"{loc.dash_space_before}{loc.dash_char}{loc.dash_space_after}"

    # 1. Dashes entirely within brackets - preserve dash type, only remove spaces
    pattern_within = re.compile(
        rf"([{OPENING_BRACKETS}])"
        rf"[{SPACES}]*"
        rf"([{HYPHEN}{EN_DASH}{EM_DASH}]+)"
        rf"[{SPACES}]*"
        rf"([{CLOSING_BRACKETS}])"
    )
    text = pattern_within.sub(r"\1\2\3", text)

    # 2. Word followed by dash followed by opening bracket
    pattern_word_open = re.compile(
        rf"([{ALL_CHARS}])"
        rf"[{SPACES}]*"
        rf"[{HYPHEN}{EN_DASH}{EM_DASH}]{{1,3}}"
        rf"[{SPACES}]*"
        rf"([{OPENING_BRACKETS}])"
    )
    text = pattern_word_open.sub(rf"\1{dash_replacement}\2", text)

    # 3. Closing bracket followed by dash followed by word
    pattern_close_word = re.compile(
        rf"([{CLOSING_BRACKETS}])"
        rf"[{SPACES}]*"
        rf"[{HYPHEN}{EN_DASH}{EM_DASH}]{{1,3}}"
        rf"[{SPACES}]*"
        rf"([{ALL_CHARS}])"
    )
    text = pattern_close_word.sub(rf"\1{dash_replacement}\2", text)

    # 4. Word followed by dash followed by closing bracket
    pattern_word_close = re.compile(
        rf"([{ALL_CHARS}])"
        rf"[{SPACES}]*"
        rf"[{HYPHEN}{EN_DASH}{EM_DASH}]{{1,3}}"
        rf"[{SPACES}]*"
        rf"([{CLOSING_BRACKETS}])"
    )
    text = pattern_word_close.sub(rf"\1{dash_replacement}\2", text)

    # 5. Opening bracket followed by dash followed by word
    pattern_open_word = re.compile(
        rf"([{OPENING_BRACKETS}])"
        rf"[{SPACES}]*"
        rf"[{HYPHEN}{EN_DASH}{EM_DASH}]{{1,3}}"
        rf"[{SPACES}]*"
        rf"([{ALL_CHARS}])"
    )
    text = pattern_open_word.sub(rf"\1{dash_replacement}\2", text)

    # 6. Closing bracket followed by dash followed by opening bracket
    pattern_close_open = re.compile(
        rf"([{CLOSING_BRACKETS}])"
        rf"[{SPACES}]*"
        rf"[{HYPHEN}{EN_DASH}{EM_DASH}]"
        rf"[{SPACES}]*"
        rf"([{OPENING_BRACKETS}])"
    )
    text = pattern_close_open.sub(rf"\1{dash_replacement}\2", text)

    return text


def fix_dash_between_cardinal_numbers(text):
    """
    Fix dashes between cardinal numbers (number ranges).

    Replaces hyphen or dash between two numbers with an en dash.
    Uses two-pass algorithm with overlap handling to prevent missing
    matches in sequences like "1-2-3".

    Args:
        text: Input text to process

    Returns:
        Text with en dashes between numbers
    """
    # Pattern matches: digit + optional space + 1-3 dashes + optional space + digit
    pattern = re.compile(
        rf"(\d)"
        rf"([{SPACES}]?"
        rf"[{HYPHEN}{EN_DASH}{EM_DASH}]{{1,3}}"
        rf"[{SPACES}]?)"
        rf"(\d)"
    )

    # Pass 1: Replace with placeholder to handle overlapping matches
    text = replace_with_overlap_handling(text, pattern, r"\1{{typopo__endash}}\3")

    # Pass 2: Replace placeholder with actual en dash
    text = text.replace("{{typopo__endash}}", EN_DASH)

    return text


def fix_dash_between_percentage_range(text):
    """
    Fix dashes between percentage ranges.

    Replaces dash between percent/permille/permyriad symbols and numbers
    with an en dash.

    Args:
        text: Input text to process

    Returns:
        Text with en dashes between percentage ranges
    """
    pattern = re.compile(
        rf"([{PERCENT}{PERMILLE}{PERMYRIAD}])"
        rf"([{SPACES}]?[{HYPHEN}{EN_DASH}{EM_DASH}]{{1,3}}[{SPACES}]?)"
        rf"(\d)"
    )
    return pattern.sub(rf"\1{EN_DASH}\3", text)


def fix_dash_between_ordinal_numbers(text, locale):
    """
    Fix dashes between ordinal numbers.

    Replaces dash between ordinal number pairs with an en dash.
    Uses locale-specific ordinal indicators (e.g., "st/nd/rd/th" for English,
    "." for German/Czech/Slovak/Rusyn).

    Args:
        text: Input text to process
        locale: Locale identifier or Locale object

    Returns:
        Text with en dashes between ordinal number ranges
    """
    loc = _get_locale_obj(locale)

    # Get ordinal indicator pattern for this locale
    ordinal = loc.ordinal_indicator

    # Pattern matches: digit + ordinal + optional space + dashes + optional space + digit + ordinal
    pattern = re.compile(
        rf"(\d)"
        rf"({ordinal})"
        rf"([{SPACES}]?[{HYPHEN}{EN_DASH}{EM_DASH}]{{1,3}}[{SPACES}]?)"
        rf"(\d)"
        rf"({ordinal})",
        re.IGNORECASE,
    )
    return pattern.sub(rf"\1\2{EN_DASH}\4\5", text)


def fix_dash(text, locale):
    """
    Fix all dash-related typography issues.

    Applies all dash fixes in sequence:
    1. Dashes between words
    2. Dashes before punctuation
    3. Dashes around brackets
    4. Dashes between cardinal numbers
    5. Dashes between percentage ranges
    6. Dashes between ordinal numbers

    Args:
        text: Input text to process
        locale: Locale identifier (en-us, de-de, cs, sk, rue)

    Returns:
        Text with all dash fixes applied
    """
    text = fix_dashes_between_words(text, locale)
    text = fix_dash_between_word_and_punctuation(text, locale)
    text = fix_dash_between_word_and_brackets(text, locale)
    text = fix_dash_between_cardinal_numbers(text)
    text = fix_dash_between_percentage_range(text)
    text = fix_dash_between_ordinal_numbers(text, locale)
    return text
