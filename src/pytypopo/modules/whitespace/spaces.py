"""
Space handling: multiple spaces, tabs, leading/trailing whitespace.

Port of src/modules/whitespace/spaces.js from typopo.
"""

import re

from pytypopo.const import (
    CLOSING_BRACKETS,
    DEGREE,
    ELLIPSIS,
    LOWERCASE_CHARS,
    OPENING_BRACKETS,
    SENTENCE_PAUSE_PUNCTUATION,
    SPACE,
    SPACES,
    TERMINAL_PUNCTUATION,
    UPPERCASE_CHARS,
)


def remove_multiple_spaces(text, locale):
    """
    Remove multiple consecutive spaces between words.

    Collapses any sequence of 2+ spaces/nbsp/hair-spaces to a single space.

    Args:
        text: Input text to fix
        locale: Language locale (unused, behavior is universal)

    Returns:
        Text with multiple spaces collapsed to single space
    """
    # Match non-whitespace + 2+ spaces + non-whitespace
    pattern = re.compile(rf"(\S)[{SPACES}]{{2,}}(\S)")
    return pattern.sub(r"\1 \2", text)


def remove_spaces_at_paragraph_beginning(text, locale, config=None):
    """
    Remove extra spaces and tabs at the beginning of each paragraph.

    Unless configured to keep spaces before markdown lists.

    Args:
        text: Input text to fix
        locale: Language locale (unused)
        config: Configuration dict with 'remove_whitespaces_before_markdown_list' key

    Returns:
        Text with leading whitespace removed
    """
    if config is None:
        config = {"remove_whitespaces_before_markdown_list": True}

    remove_md_whitespace = config.get("remove_whitespaces_before_markdown_list", True)

    # Split into lines and process each
    lines = text.split("\n")

    # Pattern to identify whitespace and markdown list indicators
    pattern = re.compile(r"^(\s+)([-*+>]*)")

    result_lines = []
    for line in lines:

        def replacer(match):
            whitespace = match.group(1)
            md_indicator = match.group(2)

            # If configured to keep markdown indentation and there's a markdown indicator
            if not remove_md_whitespace and md_indicator:
                return whitespace + md_indicator
            # Otherwise, just return the markdown indicator (removing whitespace)
            return md_indicator

        result_lines.append(pattern.sub(replacer, line))

    return "\n".join(result_lines)


def remove_spaces_at_paragraph_end(text, locale):
    """
    Remove extra spaces and tabs at the end of each paragraph.

    Args:
        text: Input text to fix
        locale: Language locale (unused)

    Returns:
        Text with trailing whitespace removed from each line
    """
    lines = text.split("\n")
    result_lines = [re.sub(r"\s+$", "", line) for line in lines]
    return "\n".join(result_lines)


def remove_space_before_sentence_pause_punctuation(text, locale):
    """
    Remove space before sentence pause punctuation (, : ;).

    Preserves emoticons like :) :-)

    Args:
        text: Input text to fix
        locale: Language locale (unused)

    Returns:
        Text with spaces removed before , : ;
    """
    # Match space + punctuation + (not followed by hyphen or closing paren - emoticons)
    pattern = re.compile(rf"[{SPACES}]([{SENTENCE_PAUSE_PUNCTUATION}])([^\-\)]|$)")
    return pattern.sub(r"\1\2", text)


def remove_space_before_terminal_punctuation(text, locale):
    """
    Remove space before terminal punctuation (. ! ?), closing brackets, and degree symbol.

    Does not remove space from empty brackets like ( ) or [ ].

    Args:
        text: Input text to fix
        locale: Language locale (unused)

    Returns:
        Text with spaces removed before terminal punctuation
    """
    # Match non-opening-bracket + space + terminal punctuation/closing bracket/degree
    pattern = re.compile(rf"([^{OPENING_BRACKETS}])[{SPACES}]([{TERMINAL_PUNCTUATION}{CLOSING_BRACKETS}{DEGREE}])")
    return pattern.sub(r"\1\2", text)


def remove_space_before_ordinal_indicator(text, locale):
    """
    Remove space before ordinal indicator.

    En-US: 1st, 2nd, 3rd, 4th
    Other locales: 1., 2., 3.

    Args:
        text: Input text to fix
        locale: Locale instance with ordinal_indicator pattern

    Returns:
        Text with spaces removed before ordinal indicators
    """
    ordinal_pattern = locale.ordinal_indicator
    # Match digit + optional space + ordinal indicator + (space or word boundary)
    # The word boundary check avoids catching "4 th" in "4 there"
    pattern = re.compile(rf"(\d)[{SPACES}]?({ordinal_pattern})([{SPACES}]|\b)")
    return pattern.sub(r"\1\2\3", text)


def remove_space_after_opening_brackets(text, locale):
    """
    Remove space after opening brackets.

    Does not affect empty brackets like ( ) or [ ].

    Args:
        text: Input text to fix
        locale: Language locale (unused)

    Returns:
        Text with spaces removed after opening brackets
    """
    # Match opening bracket + space + non-closing-bracket
    pattern = re.compile(rf"([{OPENING_BRACKETS}])[{SPACES}]([^{CLOSING_BRACKETS}])")
    return pattern.sub(r"\1\2", text)


def add_space_before_opening_brackets(text, locale):
    """
    Add space before opening brackets between words.

    Excludes plural indicators like name(s) or mass(es).

    Args:
        text: Input text to fix
        locale: Language locale (unused)

    Returns:
        Text with space added before opening brackets
    """
    # Match letter + bracket + letter + (letter or closing bracket)
    pattern = re.compile(
        rf"([{LOWERCASE_CHARS}{UPPERCASE_CHARS}])([{OPENING_BRACKETS}])([{LOWERCASE_CHARS}{UPPERCASE_CHARS}{ELLIPSIS}])([{LOWERCASE_CHARS}{UPPERCASE_CHARS}{ELLIPSIS}{CLOSING_BRACKETS}])"
    )

    def replacer(match):
        char1 = match.group(1)
        bracket = match.group(2)
        char3 = match.group(3)
        char4 = match.group(4)

        # Check for plural indicators: (s) or (es) or (S) or (ES)
        if char3 in "sS" or (char3 + char4) in ("es", "ES"):
            return f"{char1}{bracket}{char3}{char4}"

        return f"{char1}{SPACE}{bracket}{char3}{char4}"

    return pattern.sub(replacer, text)


def add_space_after_terminal_punctuation(text, locale):
    """
    Add space after terminal punctuation when followed by uppercase letter.

    Does not affect abbreviations like U.S. or filenames.

    Args:
        text: Input text to fix
        locale: Language locale (unused)

    Returns:
        Text with space added after terminal punctuation
    """
    # Match 2+ letters or ellipsis + terminal punctuation + uppercase letter
    pattern = re.compile(
        rf"([{LOWERCASE_CHARS}{UPPERCASE_CHARS}]{{2,}}|[{ELLIPSIS}])([{TERMINAL_PUNCTUATION}])([{UPPERCASE_CHARS}])"
    )
    return pattern.sub(r"\1\2 \3", text)


def add_space_after_sentence_pause(text, locale):
    """
    Add space after sentence pause punctuation (, : ;) when followed by a letter.

    Does not affect abbreviations or filenames.

    Args:
        text: Input text to fix
        locale: Language locale (unused)

    Returns:
        Text with space added after pause punctuation
    """
    # Match 2+ letters or ellipsis + pause punctuation + letter
    pattern = re.compile(
        rf"([{LOWERCASE_CHARS}{UPPERCASE_CHARS}]{{2,}}|[{ELLIPSIS}])([{SENTENCE_PAUSE_PUNCTUATION}])([{LOWERCASE_CHARS}{UPPERCASE_CHARS}])"
    )
    return pattern.sub(r"\1\2 \3", text)


def add_space_after_closing_brackets(text, locale):
    """
    Add space after closing brackets when followed by a letter.

    Args:
        text: Input text to fix
        locale: Language locale (unused)

    Returns:
        Text with space added after closing brackets
    """
    # Match closing bracket + letter
    pattern = re.compile(rf"([{CLOSING_BRACKETS}])([{LOWERCASE_CHARS}{UPPERCASE_CHARS}])")
    return pattern.sub(r"\1 \2", text)


def add_space_before_symbol(text, symbol, locale):
    """
    Add space before a symbol when not preceded by space or opening bracket.

    Args:
        text: Input text to fix
        symbol: The symbol to add space before (e.g., copyright)
        locale: Language locale (unused)

    Returns:
        Text with space added before symbol
    """
    # Escape the symbol for regex
    escaped_symbol = re.escape(symbol)
    # Match anything except space/opening-bracket/the-symbol + the symbol
    pattern = re.compile(rf"([^{SPACES}{OPENING_BRACKETS}{escaped_symbol}])({escaped_symbol})")
    return pattern.sub(rf"\1{SPACE}\2", text)


def fix_spaces(text, locale, config=None):
    """
    Apply all space fixes to text.

    Args:
        text: Input text to fix
        locale: Locale instance or locale string
        config: Configuration dict

    Returns:
        Text with all space issues fixed
    """
    if config is None:
        config = {"remove_whitespaces_before_markdown_list": True}

    # Import here to avoid circular imports
    from pytypopo.locale import Locale

    # Convert string locale to Locale instance if needed
    if isinstance(locale, str):
        locale = Locale(locale)

    text = remove_multiple_spaces(text, locale)
    text = remove_spaces_at_paragraph_beginning(text, locale, config)
    text = remove_spaces_at_paragraph_end(text, locale)
    text = remove_space_before_sentence_pause_punctuation(text, locale)
    text = remove_space_before_terminal_punctuation(text, locale)
    text = remove_space_before_ordinal_indicator(text, locale)
    text = remove_space_after_opening_brackets(text, locale)
    text = add_space_before_opening_brackets(text, locale)
    text = add_space_after_terminal_punctuation(text, locale)
    text = add_space_after_closing_brackets(text, locale)
    text = add_space_after_sentence_pause(text, locale)

    return text
