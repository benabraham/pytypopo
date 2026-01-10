"""
Double quotes and double primes handling.

Port of src/modules/punctuation/double-quotes.js from typopo.

Corrects improper use of double quotes and double primes by:
1. Identifying inches, arcseconds, seconds
2. Identifying double quote pairs
3. Replacing with locale-specific quotes
4. Fixing spacing around quotes
5. Fixing direct speech introduction
"""

import re

from pytypopo.const import (
    ALL_CHARS,
    CLOSING_BRACKETS,
    DOUBLE_PRIME,
    ELLIPSIS,
    EM_DASH,
    EN_DASH,
    HYPHEN,
    LOWERCASE_CHARS,
    ROMAN_NUMERALS,
    SENTENCE_PAUSE_PUNCTUATION,
    SENTENCE_PUNCTUATION,
    SPACES,
    TERMINAL_PUNCTUATION,
    UPPERCASE_CHARS,
)
from pytypopo.locale import Locale
from pytypopo.modules.whitespace.nbsp import add_nbsp_after_preposition
from pytypopo.utils.markdown import identify_markdown_code_ticks, place_markdown_code_ticks

# Quote adepts - various characters that might represent double quotes
# JS pattern: „|"|"|\"|«|»|″|,{2,}|‚{2,}|['''‹›′´`]{2,}
# Includes: " (straight), " " (curly), „ (low-9), « » (guillemets), ″ (double prime),
# ,, (two commas), ‚‚ (two single low-9), and 2+ of: ' ' ' ‹ › ′ ´ `
DOUBLE_QUOTE_ADEPTS = (
    r'"'  # straight quote
    r"|\u201c"  # left double quotation mark "
    r"|\u201d"  # right double quotation mark "
    r"|\u201e"  # double low-9 quotation mark „
    r"|\u00ab"  # left guillemet «
    r"|\u00bb"  # right guillemet »
    r"|\u2033"  # double prime ″
    r"|,{2,}"  # two or more commas
    r"|\u201a{2,}"  # two or more single low-9 quotes ‚
    r"|['\u2018\u2019\u2039\u203a\u2032\u00b4`]{2,}"  # 2+ of: ' ' ' ‹ › ′ ´ `
)


def _get_locale(locale):
    """Convert locale string to Locale instance if needed."""
    if isinstance(locale, str):
        return Locale(locale)
    return locale


def remove_extra_punctuation_before_quotes(text, locale):
    """
    Remove extra punctuation before double quotes.

    Example:
        "Hey!," she said -> "Hey!" she said

    Exceptions:
        (cs/sk) Byl to "Karel IV.", ktery - preserves roman numeral pattern
    """
    # Match: not-roman-numeral + sentence-punct + pause-punct + quote-adept
    # Removes the pause punctuation
    pattern = re.compile(
        rf"([^{ROMAN_NUMERALS}])"
        rf"([{SENTENCE_PUNCTUATION}])"
        rf"([{SENTENCE_PAUSE_PUNCTUATION}])"
        rf"({DOUBLE_QUOTE_ADEPTS})"
    )
    return pattern.sub(r"\1\2\4", text)


def remove_extra_punctuation_after_quotes(text, locale):
    """
    Remove extra punctuation after double quotes.

    Example:
        "We will continue tomorrow.". -> "We will continue tomorrow."

    Exceptions:
        (cs/sk) Byl to "Karel IV.", ktery - preserves roman numeral pattern
    """
    # Match: not-roman-numeral + sentence-punct + quote-adept + sentence-punct
    # Removes the trailing punctuation
    pattern = re.compile(
        rf"([^{ROMAN_NUMERALS}])"
        rf"([{SENTENCE_PUNCTUATION}])"
        rf"({DOUBLE_QUOTE_ADEPTS})"
        rf"([{SENTENCE_PUNCTUATION}])"
    )
    return pattern.sub(r"\1\2\3", text)


def identify_double_primes(text, locale):
    """
    Identify inches, arcseconds following 1-3 digit numbers.

    Algorithm:
    [1] Swap quote adepts at end of number with terminal punctuation
    [2] Identify inches following a number as double prime

    Example:
        12' 45" -> 12' 45{{typopo__double-prime}}
    """
    # [1] Swap quote adepts so they're not identified as double prime
    # Pattern: {quote} content {number}{quote}{punct} -> {quote} content {number}{punct}{quote}
    pattern1 = re.compile(
        rf"([^0-9]|^)"
        rf"({DOUBLE_QUOTE_ADEPTS})"
        rf"(.+?)"
        rf"(\d+)"
        rf"({DOUBLE_QUOTE_ADEPTS})"
        rf"([{TERMINAL_PUNCTUATION}{ELLIPSIS}])"
    )
    text = pattern1.sub(r"\1\2\3\4\6\5", text)

    # [2] Identify inches following a number (1-3 digits + optional space + quote adept)
    pattern2 = re.compile(
        rf"(\b\d{{1,3}})"
        rf"([{SPACES}]?)"
        rf"({DOUBLE_QUOTE_ADEPTS})"
    )
    text = pattern2.sub(r"\1\2{{typopo__double-prime}}", text)

    return text


def identify_double_quote_pairs(text, locale):
    """
    Identify double quote pairs.

    Example:
        "quoted material" -> {{typopo__ldq}}quoted material{{typopo__rdq}}

    Assumes double primes have been identified in previous run.
    """
    # Handle quotes around a number (to avoid confusion with primes)
    pattern1 = re.compile(
        rf"({DOUBLE_QUOTE_ADEPTS})"
        rf"(\d+)"
        rf"(\{{\{{typopo__double-prime\}}\}})"
    )
    text = pattern1.sub(r"{{typopo__ldq}}\2{{typopo__rdq}}", text)

    # Generic rule: match any quote pair
    pattern2 = re.compile(
        rf"({DOUBLE_QUOTE_ADEPTS})"
        rf"(.*?)"
        rf"({DOUBLE_QUOTE_ADEPTS})"
    )
    text = pattern2.sub(r"{{typopo__ldq}}\2{{typopo__rdq}}", text)

    return text


def identify_unpaired_left_double_quote(text, locale):
    """
    Identify unpaired left double quotes (followed by letter/number).

    Example:
        "unpaired left quote. -> {{typopo__ldq--unpaired}}unpaired left quote.
    """
    pattern = re.compile(
        rf"({DOUBLE_QUOTE_ADEPTS})"
        rf"([0-9{LOWERCASE_CHARS}{UPPERCASE_CHARS}])"
    )
    return pattern.sub(r"{{typopo__ldq--unpaired}}\2", text)


def identify_unpaired_right_double_quote(text, locale):
    """
    Identify unpaired right double quotes (preceded by letter/punctuation).

    Example:
        unpaired" right -> unpaired{{typopo__rdq--unpaired}} right
    """
    pattern = re.compile(
        rf"([{LOWERCASE_CHARS}{UPPERCASE_CHARS}{SENTENCE_PUNCTUATION}{ELLIPSIS}])"
        rf"({DOUBLE_QUOTE_ADEPTS})"
    )
    return pattern.sub(r"\1{{typopo__rdq--unpaired}}", text)


def remove_unidentified_double_quote(text, locale):
    """
    Remove double quotes that cannot be identified as left or right.

    Example:
        word " word -> word word
    """
    pattern = re.compile(
        rf"([{SPACES}])"
        rf"({DOUBLE_QUOTE_ADEPTS})"
        rf"([{SPACES}])"
    )
    return pattern.sub(r"\1", text)


def replace_double_prime_with_double_quote(text, locale):
    """
    Replace double prime & unpaired quote with quote pair.

    Handles cases like "Localhost 3000" where number looks like inches.
    """
    # Pattern: unpaired-left + content + double-prime -> quote pair
    pattern1 = re.compile(
        r"(\{\{typopo__ldq--unpaired\}\})"
        r"(.*?)"
        r"(\{\{typopo__double-prime\}\})"
    )
    text = pattern1.sub(r"{{typopo__ldq}}\2{{typopo__rdq}}", text)

    # Pattern: double-prime + content + unpaired-right -> quote pair
    pattern2 = re.compile(
        r"(\{\{typopo__double-prime\}\})"
        r"(.*?)"
        r"(\{\{typopo__rdq--unpaired\}\})"
    )
    text = pattern2.sub(r"{{typopo__ldq}}\2{{typopo__rdq}}", text)

    return text


def place_locale_double_quotes(text, locale):
    """
    Replace temporary labels with locale-specific quotes.

    Converts {{typopo__double-prime}} to actual double prime character,
    and {{typopo__ldq}}/{{typopo__rdq}} to locale quotes.
    """
    loc = _get_locale(locale)

    text = text.replace("{{typopo__double-prime}}", DOUBLE_PRIME)
    text = re.sub(r"(\{\{typopo__ldq\}\}|\{\{typopo__ldq--unpaired\}\})", loc.double_quote_open, text)
    text = re.sub(r"(\{\{typopo__rdq\}\}|\{\{typopo__rdq--unpaired\}\})", loc.double_quote_close, text)

    return text


def remove_extra_spaces_around_quotes(text, locale):
    """
    Remove extra spaces around quotes and primes.

    Examples:
        " English " -> "English"
        12' 45 " -> 12' 45"
    """
    loc = _get_locale(locale)
    left_quote = re.escape(loc.double_quote_open)
    right_quote = re.escape(loc.double_quote_close)

    # Remove space after left quote
    pattern1 = re.compile(rf"({left_quote})([{SPACES}])")
    text = pattern1.sub(r"\1", text)

    # Remove space before right quote
    pattern2 = re.compile(rf"([{SPACES}])({right_quote})")
    text = pattern2.sub(r"\2", text)

    # Remove space before double prime
    pattern3 = re.compile(rf"([{SPACES}])({re.escape(DOUBLE_PRIME)})")
    text = pattern3.sub(r"\2", text)

    return text


def add_space_before_left_double_quote(text, locale):
    """
    Add missing space before left double quote.

    Example:
        It's a"nice" saying. -> It's a "nice" saying.

    Also applies nbsp after preposition rule.
    """
    loc = _get_locale(locale)
    left_quote = re.escape(loc.double_quote_open)

    # Add space before left quote when preceded by letter or sentence punctuation
    pattern = re.compile(rf"([{SENTENCE_PUNCTUATION}{ALL_CHARS}])([{left_quote}])")
    text = pattern.sub(r"\1 \2", text)

    # Apply nbsp after preposition rule
    text = add_nbsp_after_preposition(text, loc)

    return text


def add_space_after_right_double_quote(text, locale):
    """
    Add missing space after right double quote.

    Example:
        It's a "nice"saying. -> It's a "nice" saying.
    """
    loc = _get_locale(locale)
    right_quote = re.escape(loc.double_quote_close)

    # Add space after right quote when followed by letter
    pattern = re.compile(rf"([{right_quote}])([{ALL_CHARS}])")
    return pattern.sub(r"\1 \2", text)


def swap_quotes_and_terminal_punctuation(text, locale):
    """
    Swap quotes and terminal punctuation for quoted parts.

    Rule: Terminal punctuation goes inside quotes for full sentences,
    outside for partial quotes.

    Examples:
        "quoted part." -> "quoted part".  (partial quote)
        "He was ok". -> "He was ok."  (full sentence at start)

    Exception:
        Byl to "Karel IV.", ktery - preserves roman numeral
    """
    loc = _get_locale(locale)
    left_quote = re.escape(loc.double_quote_open)
    right_quote = re.escape(loc.double_quote_close)

    # Case 1: Quoted part within a sentence - move punctuation outside
    # Match: not-sentence-punct + space + left-quote + content + not-roman + terminal-punct + right-quote
    pattern1 = re.compile(
        rf"([^{SENTENCE_PUNCTUATION}])"
        rf"([{SPACES}])"
        rf"({left_quote})"
        rf"([^{right_quote}]+?)"
        rf"([^{ROMAN_NUMERALS}{CLOSING_BRACKETS}])"
        rf"([{TERMINAL_PUNCTUATION}{ELLIPSIS}])"
        rf"({right_quote})"
    )
    text = pattern1.sub(r"\1\2\3\4\5\7\6", text)

    # Case 2: Quoted sentence within unquoted sentence - move punct inside
    # Match: not-sentence-punct + space + left-quote + content + not-roman + right-quote + terminal-punct + space + lowercase
    pattern2 = re.compile(
        rf"([^{SENTENCE_PUNCTUATION}])"
        rf"([{SPACES}])"
        rf"({left_quote})"
        rf"(.+?)"
        rf"([^{ROMAN_NUMERALS}])"
        rf"({right_quote})"
        rf"([{TERMINAL_PUNCTUATION}{ELLIPSIS}])"
        rf"([{SPACES}])"
        rf"([{LOWERCASE_CHARS}])"
    )
    text = pattern2.sub(r"\1\2\3\4\5\7\6\8\9", text)

    # Case 3: Whole quoted sentence at start of paragraph - move punct inside
    # Match: ^left-quote + content + not-roman + right-quote + terminal-punct + non-word-boundary
    pattern3 = re.compile(
        rf"(^{left_quote}"
        rf"[^{right_quote}]+?"
        rf"[^{ROMAN_NUMERALS}])"
        rf"({right_quote})"
        rf"([{TERMINAL_PUNCTUATION}{ELLIPSIS}])"
        rf"(\B)",
        re.MULTILINE,
    )
    text = pattern3.sub(r"\1\3\2\4", text)

    # Case 4: Whole quoted sentence after a sentence - move punct inside
    pattern4 = re.compile(
        rf"([{SENTENCE_PUNCTUATION}]"
        rf"[{SPACES}]"
        rf"{left_quote}"
        rf"[^{right_quote}]+?"
        rf"[^{ROMAN_NUMERALS}])"
        rf"({right_quote})"
        rf"([{TERMINAL_PUNCTUATION}{ELLIPSIS}])"
        rf"(\B)"
    )
    text = pattern4.sub(r"\1\3\2\4", text)

    # Case 5: Whole quoted sentence after another quoted sentence - move punct inside
    pattern5 = re.compile(
        rf"([{SENTENCE_PUNCTUATION}]"
        rf"[{right_quote}]"
        rf"[{SPACES}]"
        rf"{left_quote}"
        rf"[^{right_quote}]+?"
        rf"[^{ROMAN_NUMERALS}])"
        rf"({right_quote})"
        rf"([{TERMINAL_PUNCTUATION}{ELLIPSIS}])"
        rf"(\B)"
    )
    text = pattern5.sub(r"\1\3\2\4", text)

    return text


def fix_direct_speech_intro(text, locale):
    """
    Fix direct speech introduction.

    Converts various dash patterns to proper direct speech intro:
    - en-us: comma (She said, "Hello")
    - other locales: colon (She said: "Hello")

    Also removes trailing dashes after closing quotes.
    """
    loc = _get_locale(locale)
    left_quote = re.escape(loc.double_quote_open)
    right_quote = re.escape(loc.double_quote_close)

    # Direct speech intro character based on locale
    if loc.locale_id == "en-us":
        direct_speech_intro = ","
        direct_speech_intro_adepts = r",:;"
    else:
        direct_speech_intro = ":"
        direct_speech_intro_adepts = r",:;"

    dashes = f"{HYPHEN}{EN_DASH}{EM_DASH}"

    # 1. Consolidate dashes to direct speech intro
    pattern1 = re.compile(
        rf"([{ALL_CHARS}])"
        rf"[{direct_speech_intro_adepts}]?"
        rf"[{SPACES}]*"
        rf"[{dashes}]"
        rf"[{SPACES}]*"
        rf"([{left_quote}].+?[{right_quote}])"
    )
    text = pattern1.sub(rf"\1{direct_speech_intro} \2", text)

    # 2. Fix extra spacing between direct speech intro and opening quotes
    pattern2 = re.compile(
        rf"([{ALL_CHARS}])"
        rf"[{direct_speech_intro_adepts}]"
        rf"[{SPACES}]*"
        rf"([{left_quote}].+?[{right_quote}])"
    )
    text = pattern2.sub(rf"\1{direct_speech_intro} \2", text)

    # 3. Remove trailing dashes after closing quotes
    pattern3 = re.compile(
        rf"([{left_quote}].+?[{right_quote}])"
        rf"[{SPACES}]*"
        rf"[{dashes}]"
        rf"[{SPACES}]*"
        rf"([{ALL_CHARS}])"
    )
    text = pattern3.sub(r"\1 \2", text)

    # 4. At paragraph start, remove dashes before opening quotes
    pattern4 = re.compile(
        rf"^"
        rf"[{SPACES}]*"
        rf"[{dashes}]"
        rf"[{SPACES}]*"
        rf"([{left_quote}].+?[{right_quote}])"
    )
    text = pattern4.sub(r"\1", text)

    # 5. After terminal punctuation, remove dashes before opening quotes
    pattern5 = re.compile(
        rf"([{TERMINAL_PUNCTUATION}{ELLIPSIS}])"
        rf"[{SPACES}]+"
        rf"[{dashes}]"
        rf"[{SPACES}]*"
        rf"([{left_quote}].+?[{right_quote}])"
    )
    text = pattern5.sub(r"\1 \2", text)

    return text


def fix_double_quotes_and_primes(text, locale, keep_markdown_code_blocks=False):
    """
    Correct improper use of double quotes and double primes.

    Algorithm:
    [0] Identify markdown code ticks
    [1] Remove extra terminal punctuation around double quotes
    [2] Identify inches, arcseconds, seconds
    [3] Identify double quote pairs
    [4] Identify unpaired double quotes
    [5] Replace double quote & double prime with quote pair
    [6] Replace all identified punctuation with locale quotes
    [7] Consolidate spaces around quotes and primes
    [8] Fix direct speech introduction
    [9] Swap quotes and terminal punctuation

    Args:
        text: Input text to fix
        locale: Locale identifier or Locale instance
        keep_markdown_code_blocks: If True, preserve markdown backticks

    Returns:
        Text with proper double quotes and primes
    """
    loc = _get_locale(locale)

    # [0] Identify markdown code ticks
    text, markdown_blocks = identify_markdown_code_ticks(text, keep_markdown_code_blocks)

    # [1] Remove extra terminal punctuation around double quotes
    text = remove_extra_punctuation_before_quotes(text, loc)
    text = remove_extra_punctuation_after_quotes(text, loc)

    # [2] Identify inches, arcseconds, seconds
    text = identify_double_primes(text, loc)

    # [3] Identify double quote pairs
    text = identify_double_quote_pairs(text, loc)

    # [4] Identify unpaired double quotes
    text = identify_unpaired_left_double_quote(text, loc)
    text = identify_unpaired_right_double_quote(text, loc)
    text = remove_unidentified_double_quote(text, loc)

    # [5] Replace double quote & double prime with quote pair
    text = replace_double_prime_with_double_quote(text, loc)

    # [6] Replace all identified punctuation with locale quotes
    text = place_locale_double_quotes(text, loc)
    text = place_markdown_code_ticks(text, markdown_blocks, keep_markdown_code_blocks)

    # [7] Consolidate spaces around quotes and primes
    text = remove_extra_spaces_around_quotes(text, loc)
    text = add_space_before_left_double_quote(text, loc)
    text = add_space_after_right_double_quote(text, loc)

    # [8] Fix direct speech introduction
    text = fix_direct_speech_intro(text, loc)

    # [9] Swap quotes and terminal punctuation
    text = swap_quotes_and_terminal_punctuation(text, loc)

    return text
