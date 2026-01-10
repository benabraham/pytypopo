"""
Ellipsis fixes: normalizes ellipsis characters and spacing.

Port of src/modules/punctuation/ellipsis.js from typopo.

Handles:
- Three dots (...) -> ellipsis character
- Spacing around ellipsis
- Aposiopesis (trailing off mid-thought) patterns
"""

import re

from pytypopo.const import (
    ALL_CHARS,
    CLOSING_BRACKETS,
    ELLIPSIS,
    LOWERCASE_CHARS,
    SENTENCE_PUNCTUATION,
    SPACE,
    SPACES,
    UPPERCASE_CHARS,
)
from pytypopo.locale import get_locale


def replace_three_chars_with_ellipsis(text, locale=None):
    """
    Replace three or more periods/ellipses with single ellipsis.

    Handles: ..., ...., ....., mixed periods and ellipses

    Args:
        text: Input text to process
        locale: Locale identifier (unused, for API consistency)

    Returns:
        Text with three+ periods/ellipses collapsed to single ellipsis
    """
    # Pattern: 3 or more periods and/or ellipsis characters
    pattern = re.compile(rf"[{ELLIPSIS}\.]{{3,}}")
    return pattern.sub(ELLIPSIS, text)


def replace_two_chars_with_ellipsis(text, locale=None):
    """
    Replace two-char ellipsis combinations with single ellipsis.

    Handles: .ellipsis, ellipsis., multiple ellipses

    Args:
        text: Input text to process
        locale: Locale identifier (unused, for API consistency)

    Returns:
        Text with two-char ellipsis combinations collapsed
    """
    # Pattern: period+ellipsis, multiple ellipses, ellipsis+period
    pattern = re.compile(
        rf"\.{ELLIPSIS}|"
        rf"{ELLIPSIS}{{2,}}|"
        rf"{ELLIPSIS}\."
    )
    return pattern.sub(ELLIPSIS, text)


def replace_two_periods_with_ellipsis(text, locale=None):
    """
    Replace two periods surrounded by spaces with ellipsis.

    Handles: " .. " -> " ellipsis "

    Args:
        text: Input text to process
        locale: Locale identifier (unused, for API consistency)

    Returns:
        Text with spaced double periods converted to ellipsis
    """
    # Pattern: space + two periods + space
    pattern = re.compile(rf"[{SPACES}]\.{{2}}[{SPACES}]")
    return pattern.sub(f"{SPACE}{ELLIPSIS}{SPACE}", text)


def fix_ellipsis_spacing_around_commas(text, locale=None):
    """
    Fix spacing for ellipsis between commas.

    Handles: ", ellipsis ," -> ", ellipsis,"

    Args:
        text: Input text to process
        locale: Locale identifier (unused, for API consistency)

    Returns:
        Text with proper spacing around ellipsis in comma contexts
    """
    # Pattern: comma + optional space + ellipsis + optional space + comma
    pattern = re.compile(
        rf"(,)"
        rf"([{SPACES}]?)"
        rf"({ELLIPSIS})"
        rf"([{SPACES}]?)"
        rf"(,)"
    )
    return pattern.sub(rf"\1 {ELLIPSIS}\5", text)


def fix_ellipsis_as_last_item(text, locale=None):
    """
    Fix ellipsis as the last item in a list.

    Handles: ", ellipsis" at end -> ",ellipsis" (remove space)

    Args:
        text: Input text to process
        locale: Locale identifier (unused, for API consistency)

    Returns:
        Text with proper ellipsis as last list item
    """
    # Pattern: comma + optional space + ellipsis + optional space +
    # (word boundary or closing bracket) + (not comma or end)
    pattern = re.compile(
        rf"(,)"
        rf"([{SPACES}]?)"
        rf"({ELLIPSIS})"
        rf"([{SPACES}]?)"
        rf"(\B|[{CLOSING_BRACKETS}])"
        rf"([^,]|$)"
    )
    return pattern.sub(r"\1\3\5\6", text)


def fix_aposiopesis_starting_paragraph(text, locale=None):
    """
    Fix aposiopesis (ellipsis) at paragraph start.

    Handles: "^ellipsis word" -> "^ellipsis_word" (remove space after)

    Args:
        text: Input text to process
        locale: Locale identifier (unused, for API consistency)

    Returns:
        Text with proper aposiopesis at paragraph start
    """
    # Pattern: line start + ellipsis + space + letter
    pattern = re.compile(
        rf"(^{ELLIPSIS})"
        rf"([{SPACES}])"
        rf"([{LOWERCASE_CHARS}{UPPERCASE_CHARS}])",
        re.MULTILINE,
    )
    return pattern.sub(r"\1\3", text)


def fix_aposiopesis_starting_sentence(text, locale=None):
    """
    Fix aposiopesis at start of sentence (after punctuation).

    Handles: ". ellipsis word" -> ". ellipsis_word" (space before, none after)

    Args:
        text: Input text to process
        locale: Locale identifier

    Returns:
        Text with proper aposiopesis after sentence ending
    """
    loc = get_locale(locale)

    # Pattern: not closing quote + sentence punctuation + optional space +
    # ellipsis + optional space + lowercase letter
    pattern = re.compile(
        rf"([^{loc.terminal_quotes}])"
        rf"([{SENTENCE_PUNCTUATION}])"
        rf"([{SPACES}]?)"
        rf"([{ELLIPSIS}])"
        rf"([{SPACES}]?)"
        rf"([{LOWERCASE_CHARS}])"
    )
    return pattern.sub(r"\1\2 \4\6", text)


def fix_aposiopesis_between_sentences(text, locale=None):
    """
    Fix aposiopesis between sentences (lowercase ... Uppercase).

    Handles: "word ellipsis Word" -> "word_ellipsis Word" (no space before)

    Args:
        text: Input text to process
        locale: Locale identifier (unused, for API consistency)

    Returns:
        Text with proper aposiopesis between sentences
    """
    # Pattern: lowercase + space + ellipsis + optional space + uppercase
    pattern = re.compile(
        rf"([{LOWERCASE_CHARS}])"
        rf"([{SPACES}])"
        rf"([{ELLIPSIS}])"
        rf"([{SPACES}]?)"
        rf"([{UPPERCASE_CHARS}])"
    )
    return pattern.sub(r"\1\3 \5", text)


def fix_aposiopesis_between_words(text, locale=None):
    """
    Fix aposiopesis between words.

    Handles: "word_ellipsis_word" -> "word_ellipsis word" (space after)

    Args:
        text: Input text to process
        locale: Locale identifier (unused, for API consistency)

    Returns:
        Text with proper spacing for ellipsis between words
    """
    # Pattern: letter + ellipsis + letter
    pattern = re.compile(
        rf"([{ALL_CHARS}])"
        rf"([{ELLIPSIS}])"
        rf"([{ALL_CHARS}])"
    )
    return pattern.sub(r"\1\2 \3", text)


def fix_ellipsis_between_sentences(text, locale=None):
    """
    Fix ellipsis between sentences (after punctuation/quote, before uppercase).

    Handles: ".ellipsis_Word" -> ". ellipsis Word" (spaces around)

    Args:
        text: Input text to process
        locale: Locale identifier

    Returns:
        Text with proper ellipsis spacing between sentences
    """
    loc = get_locale(locale)

    # Pattern: sentence punctuation or closing quote + optional space +
    # ellipsis + optional space + uppercase letter
    pattern = re.compile(
        rf"([{SENTENCE_PUNCTUATION}{loc.terminal_quotes}])"
        rf"([{SPACES}]?)"
        rf"({ELLIPSIS})"
        rf"([{SPACES}]?)"
        rf"([{UPPERCASE_CHARS}])"
    )
    return pattern.sub(r"\1 \3 \5", text)


def fix_aposiopesis_ending_paragraph(text, locale=None):
    """
    Fix aposiopesis at paragraph end.

    Handles: "word ellipsis$" -> "word_ellipsis$" (remove space before)

    Args:
        text: Input text to process
        locale: Locale identifier

    Returns:
        Text with proper aposiopesis at paragraph end
    """
    loc = get_locale(locale)

    # Build pattern for ellipsis optionally followed by closing quote at end
    closing_quotes = f"[{loc.double_quote_close}{loc.single_quote_close}]"

    # Pattern: lowercase + spaces + ellipsis (optionally with closing quote) + end
    pattern = re.compile(
        rf"([{LOWERCASE_CHARS}])"
        rf"([{SPACES}])+"
        rf"({ELLIPSIS}{closing_quotes}?$)",
        re.MULTILINE,
    )
    return pattern.sub(r"\1\3", text)


def fix_ellipsis(text, locale=None):
    """
    Fix all ellipsis-related typography issues.

    Processing order matters to prevent re-matching corrected patterns.

    Args:
        text: Input text to process
        locale: Locale identifier

    Returns:
        Text with all ellipsis fixes applied
    """
    # First normalize multiple periods/ellipses to single ellipsis
    text = replace_three_chars_with_ellipsis(text, locale)

    # Fix spacing in specific contexts
    text = fix_ellipsis_spacing_around_commas(text, locale)
    text = fix_ellipsis_as_last_item(text, locale)

    # Fix aposiopesis patterns
    text = fix_aposiopesis_starting_paragraph(text, locale)
    text = fix_aposiopesis_starting_sentence(text, locale)
    text = fix_aposiopesis_between_sentences(text, locale)
    text = fix_aposiopesis_between_words(text, locale)

    # Fix ellipsis between sentences
    text = fix_ellipsis_between_sentences(text, locale)

    # Fix aposiopesis at paragraph end
    text = fix_aposiopesis_ending_paragraph(text, locale)

    # Final cleanup of remaining two-char combinations
    text = replace_two_chars_with_ellipsis(text, locale)
    text = replace_two_periods_with_ellipsis(text, locale)

    return text
