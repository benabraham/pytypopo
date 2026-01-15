"""
Fix abbreviation spacing.

Handles three types of abbreviations:
1. Initials (e.g., J. K. Rowling) - nbsp between initial and name
2. Single-word abbreviations (e.g., str. 38, p. 5) - nbsp after
3. Multi-word abbreviations (e.g., e.g., i.e., v. Chr.) - proper spacing

Port of src/modules/words/abbreviations.js from typopo.
"""

import regex as re

from pytypopo.const import (
    ALL_CHARS,
    EM_DASH,
    EN_DASH,
    NBSP,
    SPACES,
    UPPERCASE_CHARS,
)
from pytypopo.locale.base import get_locale

# Locale-specific abbreviation lists
# Single-word abbreviations followed by nbsp
SINGLE_WORD_ABBREVIATIONS = {
    "en-us": ["p", "pp", "no", "vol"],
    "de-de": [
        "Bhf",
        "ca",
        "Di",
        "Do",
        "Fr",
        "geb",
        "gest",
        "Hbf",
        "Mi",
        "Mo",
        "Nr",
        "S",
        "Sa",
        "So",
        "St",
        "Stk",
        "u",
        "usw",
        "z",
    ],
    "cs": ["č", "fol", "např", "odst", "par", "r", "s", "str", "sv", "tj", "tzv"],
    "sk": ["č", "fol", "napr", "odst", "par", "r", "s", "str", "sv", "tj", "tzv"],
    "rue": ["ч", "с", "стр"],
}

# Multi-word abbreviations (stored without periods)
MULTI_WORD_ABBREVIATIONS = {
    "en-us": ["U S", "e g", "i e", "a m", "p m"],
    "de-de": [
        "b w",
        "d h",
        "d i",
        "e V",
        "Ges m b H",
        "n Chr",
        "n u Z",
        "s a",
        "s o",
        "s u",
        "u a m",
        "u a",
        "u ä",
        "u Ä",
        "u dgl",
        "u U",
        "u z",
        "u zw",
        "v a",
        "v Chr",
        "v u Z",
        "z B",
        "z T",
        "z Zt",
    ],
    "cs": ["hl m", "n l", "p n l", "př n l"],
    "sk": ["hl m", "n l", "p n l", "pr n l", "s a", "s l", "t č", "t j", "zodp red"],
    "rue": ["т зн"],
}


def _get_locale_obj(locale):
    """Get Locale object from string or object."""
    return get_locale(locale)


def fix_initials(text, locale):
    """
    Fix spacing around name initials.

    Handles up to 3 initials before a full name:
    - I. Name -> I.{nbsp}Name
    - I. I. Name -> I.{abbrSpace}I.{space}Name
    - I. I. I. Name -> I.{abbrSpace}I.{abbrSpace}I.{space}Name

    Args:
        text: Input text
        locale: Language locale (string or Locale object)

    Returns:
        Text with proper initial spacing
    """
    locale_obj = _get_locale_obj(locale)
    abbr_space = locale_obj.space_after_abbreviation

    # Pattern components matching JS implementation
    # Initial: uppercase letter + optional second letter + period + optional spaces
    initial_pattern = rf"([{UPPERCASE_CHARS}][{ALL_CHARS}]?\.)([{SPACES}]?)"
    # Full name: 2+ letters not ending with period
    full_name_pattern = rf"([{ALL_CHARS}]{{2,}}[^\.])"

    # Process patterns in order (as in JS - sequential replacement)
    patterns = [
        # Pattern 1: "I. FullName"
        {
            "pattern": rf"{initial_pattern}{full_name_pattern}",
            "replacement": rf"\1{NBSP}\3",
        },
        # Pattern 2: "I. I. FullName" - regular space before name (matches JS)
        {
            "pattern": rf"{initial_pattern}{initial_pattern}{full_name_pattern}",
            "replacement": rf"\1{abbr_space}\3 \5",
        },
        # Pattern 3: "I. I. I. FullName" - regular space before name (matches JS)
        {
            "pattern": rf"{initial_pattern}{initial_pattern}{initial_pattern}{full_name_pattern}",
            "replacement": rf"\1{abbr_space}\3{abbr_space}\5 \7",
        },
    ]

    for p in patterns:
        text = re.sub(p["pattern"], p["replacement"], text)

    return text


def fix_multiple_word_abbreviations(text, locale):
    """
    Fix spacing in multi-word abbreviations.

    Two-phase algorithm:
    1. Before following word: e.g. something -> e.{abbrSpace}g. something
    2. After word/standalone: Praha, hl. m. -> Praha, hl.{abbrSpace}m.

    Args:
        text: Input text
        locale: Language locale (string or Locale object)

    Returns:
        Text with proper abbreviation spacing
    """
    locale_obj = _get_locale_obj(locale)
    abbr_space = locale_obj.space_after_abbreviation

    # Collect all abbreviations from all locales
    all_abbreviations = []
    for abbr_list in MULTI_WORD_ABBREVIATIONS.values():
        all_abbreviations.extend(abbr_list)
    # Remove duplicates while preserving order
    all_abbreviations = list(dict.fromkeys(all_abbreviations))

    if not all_abbreviations:
        return text

    # Boundary patterns (matching JS implementation)
    # Preceding: not a letter, not en-dash, not em-dash (or start of string)
    preceding_non_latin_boundary = rf"([^{ALL_CHARS}{EN_DASH}{EM_DASH}]|^)"
    # Following word: a letter or digit (matches JS \D which includes digits, but we need letters/digits here)
    following_word = rf"([{ALL_CHARS}\d])"
    # Following non-word boundary (for end-of-phrase matching)
    # Not a letter, not digit, not opening quote, not backtick, not emoji (or end of string)
    left_double_quote = locale_obj.double_quote_open
    left_single_quote = locale_obj.single_quote_open
    # Use \p{Emoji} to exclude emoji characters (requires regex library)
    following_non_latin_boundary = rf"([^{ALL_CHARS}\d{left_double_quote}{left_single_quote}`\p{{Emoji}}]|$)"

    # Build abbreviation patterns for each multi-word abbreviation
    # Pattern structure: (word)(.)([spaces]?) for each word
    abbreviation_patterns = []
    for abbr in all_abbreviations:
        parts = abbr.split()
        if len(parts) < 2:
            continue

        # Build pattern: (word1)(\.)([spaces]?)(word2)(\.)([spaces]?)...
        pattern_parts = []
        for part in parts:
            pattern_parts.append(rf"({re.escape(part)})(\.)([{SPACES}]?)")
        abbreviation_patterns.append(("".join(pattern_parts), len(parts)))

    # Phase 1: Identify multi-word abbreviations BEFORE a following word
    # e.g. "e.g. something" -> "e.{abbrSpace}g.{nbsp}something"
    for abbr_pattern, abbr_count in abbreviation_patterns:
        pattern = rf"{preceding_non_latin_boundary}{abbr_pattern}{following_word}"

        def make_before_word_replacement(count, space):
            def replacer(match):
                # Group 1: preceding boundary
                result = match.group(1)
                # Groups 2,3,4 for first abbr word, 5,6,7 for second, etc.
                # Each abbreviation word has 3 groups: (word)(.)([spaces]?)
                for i in range(count - 1):
                    word_group = 2 + i * 3  # 2, 5, 8, ...
                    result += match.group(word_group) + "." + space
                # Last abbreviation word - followed by period and regular space before next word
                # (matches JS - regular space, not nbsp)
                last_word_group = 2 + (count - 1) * 3
                result += match.group(last_word_group) + ". "
                # Following word
                following_group = 2 + count * 3
                result += match.group(following_group)
                return result

            return replacer

        text = re.sub(pattern, make_before_word_replacement(abbr_count, abbr_space), text, flags=re.IGNORECASE)

    # Phase 2: Identify multi-word abbreviations AFTER a word or standalone
    # e.g. "Praha, hl. m." -> "Praha, hl.{abbrSpace}m."
    for abbr_pattern, abbr_count in abbreviation_patterns:
        pattern = rf"{preceding_non_latin_boundary}{abbr_pattern}{following_non_latin_boundary}"

        def make_after_word_replacement(count, space):
            def replacer(match):
                # Group 1: preceding boundary
                result = match.group(1)
                # Each abbreviation word has 3 groups: (word)(.)([spaces]?)
                for i in range(count - 1):
                    word_group = 2 + i * 3
                    result += match.group(word_group) + "." + space
                # Last abbreviation word - no space after
                last_word_group = 2 + (count - 1) * 3
                result += match.group(last_word_group) + "."
                # Following boundary
                following_group = 2 + count * 3
                result += match.group(following_group)
                return result

            return replacer

        text = re.sub(
            pattern, make_after_word_replacement(abbr_count, abbr_space), text, flags=re.IGNORECASE | re.UNICODE
        )

    return text


def fix_single_word_abbreviations(text, locale):  # noqa: ARG001
    """
    Fix spacing after single-word abbreviations.

    Two-phase algorithm:
    1. Before following word: str. 38 -> str.{nbsp}38
    2. After preceding word: 10 str. -> 10{nbsp}str.

    Args:
        text: Input text
        locale: Language locale (kept for API consistency, uses all locales)

    Returns:
        Text with proper abbreviation spacing
    """
    # Collect all abbreviations from all locales (not locale-specific per JS behavior)
    all_abbreviations = set()
    for abbr_list in SINGLE_WORD_ABBREVIATIONS.values():
        all_abbreviations.update(abbr_list)

    if not all_abbreviations:
        return text

    # Boundary patterns (matching JS implementation)
    # Preceding: not a letter, not en-dash, not em-dash, not nbsp, not period (or start of string)
    preceding_non_latin_boundary = rf"([^{ALL_CHARS}{EN_DASH}{EM_DASH}{NBSP}\.]|^)"
    # Following word: letters or digits, then not a period (or end of string)
    following_word = rf"([{ALL_CHARS}\d]+)([^\.]|$)"
    # Preceding word: letter or digit followed by spaces
    preceding_word = rf"([{ALL_CHARS}\d])([{SPACES}])"
    # Following non-word: not spaces, not letters, not digits (or end of string)
    following_non_latin_boundary = rf"([^{SPACES}{ALL_CHARS}\d]|$)"

    # Build abbreviation patterns
    # Pattern: (abbr)(\.)([spaces]?)
    abbreviation_patterns = []
    for abbr in sorted(all_abbreviations, key=len, reverse=True):
        abbreviation_patterns.append(rf"({re.escape(abbr)})(\.)([{SPACES}]?)")

    # Phase 1: Identify single-word abbreviations BEFORE a following word
    # e.g. "str. 38" -> "str.{nbsp}38"
    for abbr_pattern in abbreviation_patterns:
        pattern = rf"{preceding_non_latin_boundary}{abbr_pattern}{following_word}"
        # Groups: 1=preceding, 2=abbr, 3=period, 4=spaces, 5=following word, 6=following non-period
        replacement = rf"\1\2\3{NBSP}\5\6"
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    # Phase 2: Identify single-word abbreviations AFTER a preceding word
    # e.g. "10 str." -> "10{nbsp}str."
    for abbr_pattern in abbreviation_patterns:
        pattern = rf"{preceding_word}{abbr_pattern}{following_non_latin_boundary}"
        # Groups: 1=preceding char, 2=space, 3=abbr, 4=period, 5=spaces after, 6=following boundary
        replacement = rf"\1{NBSP}\3\4\5\6"
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    return text


def fix_abbreviations(text, locale):
    """
    Fix all abbreviation spacing issues.

    Applies fixes for initials, single-word, and multi-word abbreviations.

    Args:
        text: Input text
        locale: Language locale (string or Locale object)

    Returns:
        Text with proper abbreviation spacing
    """
    text = fix_initials(text, locale)
    text = fix_multiple_word_abbreviations(text, locale)
    text = fix_single_word_abbreviations(text, locale)
    return text
