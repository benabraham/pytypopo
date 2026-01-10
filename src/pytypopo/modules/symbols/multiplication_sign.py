"""
Fix multiplication sign: x/X -> x in appropriate contexts.

Port of src/lib/symbols/multiplication-sign.js from typopo.
"""

import re

from pytypopo.const import (
    DOUBLE_PRIME,
    MULTIPLICATION_SIGN,
    SINGLE_PRIME,
    SPACES,
)

# For matching words with diacritics, we use a broad character class
# that includes common Latin letters with diacritics
# This covers most European languages without requiring the regex library
WORD_CHARS = (
    r"a-zA-Z"
    r"\u00C0-\u00D6"  # Latin extended A (upper): A-O with diacritics
    r"\u00D8-\u00F6"  # Latin extended (upper O-o): O with stroke to o with diaeresis
    r"\u00F8-\u00FF"  # Latin extended A (lower): o with stroke to y with diaeresis
    r"\u0100-\u017F"  # Latin Extended-A: various European letters
    r"\u0180-\u024F"  # Latin Extended-B: additional letters
)

# Lowercase only - same ranges but lowercase specific
LOWERCASE_WORD_CHARS = (
    r"a-z"
    r"\u00E0-\u00F6"  # Latin small letters with diacritics (a-o range)
    r"\u00F8-\u00FF"  # Latin small letters with diacritics (o-y range)
    r"\u0101\u0103\u0105\u0107\u0109\u010B\u010D\u010F"  # a, a, a, c, c, c, c, d with various marks
    r"\u0111\u0113\u0115\u0117\u0119\u011B\u011D\u011F"  # d, e, e, e, e, e, g, g
    r"\u0121\u0123\u0125\u0127\u0129\u012B\u012D\u012F"  # g, g, h, h, i, i, i, i
    r"\u0131\u0133\u0135\u0137\u013A\u013C\u013E\u0140"  # dotless i, ij, j, k, l, l, l, l
    r"\u0142\u0144\u0146\u0148\u014B\u014D\u014F\u0151"  # l, n, n, n, eng, o, o, o
    r"\u0153\u0155\u0157\u0159\u015B\u015D\u015F\u0161"  # oe, r, r, r, s, s, s, s
    r"\u0163\u0165\u0167\u0169\u016B\u016D\u016F\u0171"  # t, t, t, u, u, u, u, u
    r"\u0173\u0175\u0177\u017A\u017C\u017E"  # u, w, y, z, z, z
)


def _fix_multiplication_between_numbers(text):
    """
    Fix multiplication sign between numbers with optional units.

    Handles patterns like:
    - 5 x 4 -> 5 x 4
    - 5" x 4" -> 5" x 4"
    - 5 mm x 5 mm -> 5 mm x 5 mm

    Args:
        text: Input text

    Returns:
        Text with multiplication signs fixed
    """
    # Pattern: number + optional unit + space + x + space + number + optional unit
    # Optional unit includes lowercase chars and prime marks
    pattern = re.compile(
        rf"(\d+)"  # number
        rf"([{SPACES}]?[{LOWERCASE_WORD_CHARS}{SINGLE_PRIME}{DOUBLE_PRIME}]*)"  # optional unit
        rf"([{SPACES}][xX][{SPACES}])"  # x with spaces
        rf"(\d+)"  # number
        rf"([{SPACES}]?[{LOWERCASE_WORD_CHARS}{SINGLE_PRIME}{DOUBLE_PRIME}]*)"  # optional unit
    )

    # Apply repeatedly until no more matches (for multiple x in sequence)
    prev_text = None
    while prev_text != text:
        prev_text = text
        text = pattern.sub(rf"\1\2 {MULTIPLICATION_SIGN} \4\5", text)

    return text


def _fix_multiplication_between_words(text):
    """
    Fix multiplication sign between words/abbreviations.

    Handles patterns like:
    - s x v x h -> s x v x h (dimension abbreviations)
    - Marciano x Clay -> Marciano x Clay

    Args:
        text: Input text

    Returns:
        Text with multiplication signs fixed
    """
    # Pattern: word + space + x + space + word
    # Must NOT match if x is adjacent to a letter (avoid "light xenons")
    # Capital X preceded by space and followed by space + capital letter is a middle initial
    pattern = re.compile(
        rf"([{WORD_CHARS}]+)"  # word
        rf"([{SPACES}][xX][{SPACES}])"  # x with spaces
        rf"([{WORD_CHARS}]+)"  # word
    )

    def replace_word_x(match):
        word1 = match.group(1)
        x_part = match.group(2)
        word2 = match.group(3)

        # Check for middle initial pattern: "Name X Surname"
        # Both words start with uppercase and x is uppercase X
        if word1[0].isupper() and word2[0].isupper() and "X" in x_part and " X " in x_part:
            return match.group(0)  # Keep original

        return f"{word1} {MULTIPLICATION_SIGN} {word2}"

    # Apply repeatedly until no more matches (for multiple x in sequence)
    prev_text = None
    while prev_text != text:
        prev_text = text
        text = pattern.sub(replace_word_x, text)

    return text


def _fix_multiplication_number_and_word(text):
    """
    Fix multiplication sign between number and word.

    Handles patterns like:
    - 4 x object -> 4 x object
    - 4x object -> 4x object (without space before x)

    Args:
        text: Input text

    Returns:
        Text with multiplication signs fixed
    """
    # Pattern: digit + optional space + x + space + lowercase word
    # Avoid: words starting with x after digit (4 xenographs, 4xenographs)
    # Avoid: hex notation (0xd)
    pattern = re.compile(
        rf"(\d)"  # single digit
        rf"([{SPACES}]?)"  # optional space
        rf"([xX{MULTIPLICATION_SIGN}])"  # x or existing multiplication sign
        rf"([{SPACES}])"  # space required
        rf"([{LOWERCASE_WORD_CHARS}]+)"  # lowercase word
    )

    def replace_num_word(match):
        digit = match.group(1)
        space_before = match.group(2)
        # x_char = match.group(3)  # not used
        # space_after = match.group(4)  # not used
        word = match.group(5)

        # If there was space before x, output "digit x word"
        # If no space before x, output "digitx word"
        if space_before:
            return f"{digit} {MULTIPLICATION_SIGN} {word}"
        else:
            return f"{digit}{MULTIPLICATION_SIGN} {word}"

    return pattern.sub(replace_num_word, text)


def _fix_multiplication_spacing(text):
    """
    Fix spacing around multiplication sign between numbers.

    Handles patterns like:
    - 12x3 -> 12 x 3
    - 12x3 -> 12 x 3
    - 12"x3" -> 12" x 3"

    Args:
        text: Input text

    Returns:
        Text with proper spacing
    """
    # Pattern: number + optional prime + x + number + optional prime
    # No spaces around x
    pattern = re.compile(
        rf"(\d+)"  # number
        rf"([{SINGLE_PRIME}{DOUBLE_PRIME}])?"  # optional prime mark
        rf"([xX{MULTIPLICATION_SIGN}])"  # x or multiplication sign
        rf"(\d+)"  # number
        rf"([{SINGLE_PRIME}{DOUBLE_PRIME}])?"  # optional prime mark
    )

    def add_spacing(match):
        num1 = match.group(1)
        prime1 = match.group(2) or ""
        # x_char = match.group(3)  # not used, always replace with multiplication sign
        num2 = match.group(4)
        prime2 = match.group(5) or ""
        return f"{num1}{prime1} {MULTIPLICATION_SIGN} {num2}{prime2}"

    return pattern.sub(add_spacing, text)


def fix_multiplication_sign(text, locale):
    """
    Fix multiplication sign x/X to x symbol.

    Converts x/X to x when used as multiplication:
    - Between numbers: 5 x 4 -> 5 x 4
    - Between words: s x v x h -> s x v x h
    - Between number and word: 4x object -> 4x object
    - Fixes spacing: 12x3 -> 12 x 3

    Does NOT convert when:
    - Part of a word: xenographs, 4xenographs
    - Hexadecimal notation: 0xd

    Args:
        text: Input text to fix
        locale: Language locale (unused, symbols are universal)

    Returns:
        Text with multiplication signs fixed
    """
    # Order matters: fix spacing first to normalize, then fix symbols

    # Fix tight number x number patterns (add spacing)
    text = _fix_multiplication_spacing(text)

    # Fix x between numbers with units
    text = _fix_multiplication_between_numbers(text)

    # Fix x between words
    text = _fix_multiplication_between_words(text)

    # Fix x between number and word
    text = _fix_multiplication_number_and_word(text)

    return text
