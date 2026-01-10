"""
Non-breaking space handling.

Port of src/modules/whitespace/nbsp.js from typopo.
"""

import re

from pytypopo.const import (
    ALL_CHARS,
    APOSTROPHE,
    CLOSING_BRACKETS,
    COPYRIGHT,
    ELLIPSIS,
    EM_DASH,
    EN_DASH,
    HAIR_SPACE,
    HYPHEN,
    LOWERCASE_CHARS,
    MINUS,
    MULTIPLICATION_SIGN,
    NARROW_NBSP,
    NBSP,
    PERCENT,
    PERMILLE,
    PERMYRIAD,
    PLUS,
    REGISTERED_TRADEMARK,
    ROMAN_NUMERALS,
    SENTENCE_PUNCTUATION,
    SOUND_RECORDING_COPYRIGHT,
    SPACE,
    SPACES,
    UPPERCASE_CHARS,
)
from pytypopo.utils.regex_overlap import replace_with_overlap_handling


def remove_nbsp_between_multi_char_words(text, locale):
    """
    Remove non-breaking space between multi-letter words.

    For example: "vo nbsp dvore" -> "vo dvore"

    Args:
        text: Input text to fix
        locale: Language locale (unused)

    Returns:
        Text with nbsp between multi-char words replaced with regular space
    """
    # Match 2+ letter word + nbsp/narrow-nbsp + 2+ letter word
    pattern = re.compile(
        rf"([{LOWERCASE_CHARS}{UPPERCASE_CHARS}]{{2,}})[{NBSP}{NARROW_NBSP}]([{LOWERCASE_CHARS}{UPPERCASE_CHARS}]{{2,}})"
    )
    return replace_with_overlap_handling(text, pattern, r"\1 \2")


def add_nbsp_after_preposition(text, locale):
    """
    Add nbsp after single-letter prepositions.

    Examples:
        V obchode -> V nbsp obchode
        Skace o tyci -> Skace o nbsp tyci

    English "I" is handled specially (always gets nbsp).

    Args:
        text: Input text to fix
        locale: Locale instance or locale string

    Returns:
        Text with nbsp after single-letter prepositions
    """
    # Get locale_id for special handling
    locale_id = locale.locale_id if hasattr(locale, "locale_id") else str(locale)

    # a) lowercase prepositions (can appear anywhere)
    # Match start/space/non-letter-or-digit + lowercase letter + space
    pattern_lower = re.compile(
        rf"(^|[{SPACE}]|[^{ALL_CHARS}\d{APOSTROPHE}{PLUS}{MINUS}{HYPHEN}])"
        rf"([{LOWERCASE_CHARS}])"
        rf"([{SPACE}])"
    )
    text = replace_with_overlap_handling(text, pattern_lower, rf"\1\2{NBSP}")

    # b) uppercase prepositions at beginning of sentence
    # After sentence punctuation, ellipsis, copyright symbols
    pattern_upper = re.compile(
        rf"(^|[{SENTENCE_PUNCTUATION}{ELLIPSIS}{COPYRIGHT}{REGISTERED_TRADEMARK}{SOUND_RECORDING_COPYRIGHT}])"
        rf"([{SPACES}]?)"
        rf"([{UPPERCASE_CHARS}])"
        rf"([{SPACES}])"
    )
    text = pattern_upper.sub(rf"\1\2\3{NBSP}", text)

    # c) English "I" special handling
    if locale_id == "en-us":
        pattern_i = re.compile(rf"(^|[{SPACES}])(I)([{SPACES}])")
        text = pattern_i.sub(rf"\1\2{NBSP}", text)

    return text


def add_nbsp_after_ampersand(text, locale):
    """
    Add nbsp after ampersand when surrounded by spaces.

    Example: "Bed & Breakfast" -> "Bed & nbsp Breakfast"

    Args:
        text: Input text to fix
        locale: Language locale (unused)

    Returns:
        Text with nbsp after ampersand
    """
    pattern = re.compile(rf"([{SPACES}])(&)([{SPACES}])")
    return pattern.sub(rf" \2{NBSP}", text)


def add_nbsp_after_cardinal_number(text, locale):
    """
    Add nbsp after cardinal numbers (1-99) when followed by a word.

    Only handles 1-2 digit numbers to avoid false positives.

    Args:
        text: Input text to fix
        locale: Language locale (unused)

    Returns:
        Text with nbsp after cardinal numbers
    """
    # Match non-nbsp-or-digit or start + 1-2 digits + space + letter
    pattern = re.compile(rf"([^{NBSP}\d]|^)(\d{{1,2}})([{SPACES}])([{ALL_CHARS}])")
    return pattern.sub(rf"\1\2{NBSP}\4", text)


def add_nbsp_after_ordinal_number(text, locale):
    """
    Add nbsp after ordinal numbers (1st, 2nd... or 1., 2...) when followed by a word.

    Only handles 1-2 digit numbers to avoid false positives.

    Args:
        text: Input text to fix
        locale: Locale instance or locale string with ordinal_indicator

    Returns:
        Text with nbsp after ordinal numbers
    """
    # Import here to avoid circular imports
    from pytypopo.locale import Locale as LocaleClass

    # Convert string locale to Locale instance if needed
    if isinstance(locale, str):
        locale = LocaleClass(locale)

    ordinal_indicator = locale.ordinal_indicator
    # Match non-nbsp-or-digit or start + 1-2 digits + ordinal indicator + optional space + letter
    pattern = re.compile(rf"([^{NBSP}\d_%\-]|^)(\d{{1,2}})({ordinal_indicator})([{SPACES}]?)([{ALL_CHARS}])")
    return pattern.sub(rf"\1\2\3{NBSP}\5", text)


def add_nbsp_within_ordinal_date(text, locale):
    """
    Add locale-specific spaces within ordinal dates.

    Example: "12. 1. 2017" -> "12.{firstSpace}1.{secondSpace}2017"

    German uses nbsp after day, regular space after month.
    Other locales use nbsp for both.

    Args:
        text: Input text to fix
        locale: Locale instance or locale string with ordinal_date spacing

    Returns:
        Text with proper spacing in ordinal dates
    """
    # Import here to avoid circular imports
    from pytypopo.locale import Locale as LocaleClass

    # Convert string locale to Locale instance if needed
    if isinstance(locale, str):
        locale = LocaleClass(locale)

    first_space = locale.ordinal_date_first_space
    second_space = locale.ordinal_date_second_space

    pattern = re.compile(
        rf"(\d)(\.)"
        rf"([{SPACES}]?)"
        rf"(\d)(\.)"
        rf"([{SPACES}]?)"
        rf"(\d)"
    )
    return pattern.sub(rf"\1\2{first_space}\4\5{second_space}\7", text)


def add_nbsp_after_roman_numeral(text, locale):
    """
    Add nbsp after roman numerals with ordinal indicator.

    Examples:
        I. kapitola -> I. nbsp kapitola
        8. V. 1945 -> 8. nbsp V. nbsp 1945

    Avoids false positives like person initials (G. D. Lambert).

    Args:
        text: Input text to fix
        locale: Locale instance or locale string with roman_ordinal_indicator

    Returns:
        Text with nbsp after roman numerals
    """
    # Import here to avoid circular imports
    from pytypopo.locale import Locale as LocaleClass

    # Convert string locale to Locale instance if needed
    if isinstance(locale, str):
        locale = LocaleClass(locale)

    roman_indicator = locale.roman_ordinal_indicator

    # Skip if locale doesn't use roman ordinal indicators (en-us)
    if not roman_indicator:
        return text

    # Pattern to match roman numerals, but avoid initials
    # First group optionally matches a preceding initial pattern to exclude
    pattern = re.compile(
        rf"(\b[{UPPERCASE_CHARS}][{ALL_CHARS}]?{roman_indicator}[{SPACES}]?)?"
        rf"(\b)"
        rf"([{ROMAN_NUMERALS}]+)"
        rf"({roman_indicator})"
        rf"([{SPACES}]?)"
        rf"([{ALL_CHARS}\d])"
    )

    def replacer(match):
        preceding = match.group(1)
        word_boundary = match.group(2)
        numeral = match.group(3)
        indicator = match.group(4)
        # match.group(5) is space, not used
        following = match.group(6)

        # If there's a preceding initial pattern, don't replace
        # This avoids false positives like "G. D. Lambert"
        if preceding:
            return match.group(0)

        return f"{word_boundary}{numeral}{indicator}{NBSP}{following}"

    return pattern.sub(replacer, text)


def fix_nbsp_for_name_with_regnal_number(text, locale):
    """
    Fix nbsp around names with regnal numbers.

    Examples:
        Karel IV. -> Karel nbsp IV.
        Karel IV. nbsp byl -> Karel nbsp IV. byl

    Args:
        text: Input text to fix
        locale: Locale instance or locale string with roman_ordinal_indicator

    Returns:
        Text with proper nbsp around regnal numbers
    """
    # Import here to avoid circular imports
    from pytypopo.locale import Locale as LocaleClass

    # Convert string locale to Locale instance if needed
    if isinstance(locale, str):
        locale = LocaleClass(locale)

    roman_indicator = locale.roman_ordinal_indicator

    # Skip if locale doesn't use roman ordinal indicators
    if not roman_indicator:
        return text

    # Match name + space + roman numeral + ordinal indicator + optional nbsp
    pattern = re.compile(
        rf"(\b[{UPPERCASE_CHARS}][{LOWERCASE_CHARS}]+?)"
        rf"([{SPACES}])"
        rf"([{ROMAN_NUMERALS}]+\b)"
        rf"({roman_indicator})"
        rf"([{NBSP}]?)"
    )

    def replacer(match):
        name = match.group(1)
        # match.group(2) is space, not used
        numeral = match.group(3)
        indicator = match.group(4)
        trailing_nbsp = match.group(5)

        # Special case: "I" alone might be English pronoun, not Roman numeral
        if numeral == "I":
            if trailing_nbsp == "":
                return f"{name}{SPACE}{numeral}{indicator}"
            else:
                return f"{name}{SPACE}{numeral}{indicator}{trailing_nbsp}"

        # Standard case: add nbsp before numeral, space after indicator
        if trailing_nbsp == "":
            return f"{name}{NBSP}{numeral}{indicator}"
        elif trailing_nbsp == NBSP:
            return f"{name}{NBSP}{numeral}{indicator}{SPACE}"
        else:
            return f"{name}{NBSP}{numeral}{indicator}{SPACE}"

    return pattern.sub(replacer, text)


def fix_space_before_percent(text, locale):
    """
    Fix space before percent, permille, and permyriad signs.

    Locale differences:
        - en-us: no space before %
        - de-de: narrow nbsp before %
        - cs, sk, rue: nbsp before %

    Args:
        text: Input text to fix
        locale: Locale instance or locale string with space_before_percent

    Returns:
        Text with proper spacing before percent signs
    """
    # Import here to avoid circular imports
    from pytypopo.locale import Locale as LocaleClass

    # Convert string locale to Locale instance if needed
    if isinstance(locale, str):
        locale = LocaleClass(locale)

    space_before = locale.space_before_percent

    # Match digit + space + percent/permille/permyriad
    pattern = re.compile(rf"(\d)([{SPACES}])([{PERCENT}{PERMILLE}{PERMYRIAD}])")
    return pattern.sub(rf"\1{space_before}\3", text)


def add_nbsp_before_single_letter(text, locale):
    """
    Add nbsp before single capital letter mid-sentence.

    Examples:
        The product X is -> The product nbsp X is
        Sputnik V -> Sputnik nbsp V

    Avoids:
        - After sentence punctuation (start of new sentence)
        - After certain quotes and brackets
        - English "I" is excluded in en-us locale

    Args:
        text: Input text to fix
        locale: Locale instance or locale string

    Returns:
        Text with nbsp before single capital letters
    """
    # Import here to avoid circular imports
    from pytypopo.locale import Locale as LocaleClass

    # Convert string locale to Locale instance if needed
    if isinstance(locale, str):
        locale = LocaleClass(locale)

    locale_id = locale.locale_id

    # Build uppercase pattern, excluding "I" for en-us
    uppercase_chars = UPPERCASE_CHARS
    if locale_id == "en-us":
        # Remove I from A-Z range for en-us
        uppercase_chars = uppercase_chars.replace("A-Z", "A-HJ-Z")

    # Get locale-specific quotes
    right_double_quote = locale.double_quote_close
    right_single_quote = locale.single_quote_close

    # Pattern: not-sentence-punct-or-brackets-or-quotes + space + uppercase + (space or end-of-word)
    pattern = re.compile(
        rf"([^{SENTENCE_PUNCTUATION}{ELLIPSIS}{CLOSING_BRACKETS}{right_double_quote}{right_single_quote}{APOSTROPHE}{MULTIPLICATION_SIGN}{EM_DASH}{EN_DASH}])"
        rf"([{SPACES}])"
        rf"([{uppercase_chars}])"
        rf"(([{SPACES}])|(\.?$|$))"
    )

    def replacer(match):
        before = match.group(1)
        # match.group(2) is space1, not used
        letter = match.group(3)
        after = match.group(4)
        space2 = match.group(5)

        # For non-en-us locales, replace nbsp after "I" with space
        if locale_id != "en-us" and letter == "I":
            if space2 in (NBSP, HAIR_SPACE, NARROW_NBSP):
                return f"{before}{NBSP}{letter}{SPACE}"

        return f"{before}{NBSP}{letter}{after}"

    return pattern.sub(replacer, text)


def add_nbsp_after_symbol(text, symbol, locale, space=None):
    """
    Add nbsp after a symbol when not followed by space.

    Args:
        text: Input text to fix
        symbol: The symbol to add space after
        locale: Language locale (unused)
        space: Space character to use (default: nbsp)

    Returns:
        Text with nbsp after symbol
    """
    if space is None:
        space = NBSP

    escaped_symbol = re.escape(symbol)
    pattern = re.compile(rf"({escaped_symbol})([^{SPACES}{escaped_symbol}])")
    return pattern.sub(rf"\1{space}\2", text)


def replace_spaces_with_nbsp_after_symbol(text, symbol, locale, space=None):
    """
    Replace various spaces with nbsp after a symbol.

    Args:
        text: Input text to fix
        symbol: The symbol
        locale: Language locale (unused)
        space: Space character to use (default: nbsp)

    Returns:
        Text with unified nbsp after symbol
    """
    if space is None:
        space = NBSP

    escaped_symbol = re.escape(symbol)
    pattern = re.compile(rf"({escaped_symbol})([{SPACES}]+)")
    return pattern.sub(rf"\1{space}", text)


def fix_nbsp(text, locale):
    """
    Apply all non-breaking space fixes to text.

    Args:
        text: Input text to fix
        locale: Locale instance or locale string

    Returns:
        Text with all nbsp rules applied
    """
    # Import here to avoid circular imports
    from pytypopo.locale import Locale as LocaleClass

    # Convert string locale to Locale instance if needed
    if isinstance(locale, str):
        locale = LocaleClass(locale)

    text = remove_nbsp_between_multi_char_words(text, locale)
    text = add_nbsp_after_preposition(text, locale)
    text = add_nbsp_after_ampersand(text, locale)
    text = add_nbsp_after_cardinal_number(text, locale)
    text = add_nbsp_after_ordinal_number(text, locale)
    text = add_nbsp_within_ordinal_date(text, locale)
    text = add_nbsp_after_roman_numeral(text, locale)
    text = add_nbsp_before_single_letter(text, locale)
    text = fix_nbsp_for_name_with_regnal_number(text, locale)
    text = fix_space_before_percent(text, locale)

    return text
