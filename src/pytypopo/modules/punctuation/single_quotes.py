"""
Single quotes, primes, and apostrophes handling.

Port of src/modules/punctuation/single-quotes.js from typopo.

Corrects improper use of single quotes, single primes, and apostrophes by:
1. Identifying common apostrophe contractions ('n', 'cause, don't, etc.)
2. Identifying feet, arcminutes, minutes
3. Identifying single quote pairs
4. Replacing with locale-specific quotes
5. Swapping quotes and terminal punctuation
"""

import re

from pytypopo.const import (
    ALL_CHARS,
    APOSTROPHE,
    ELLIPSIS,
    EM_DASH,
    EN_DASH,
    LOWERCASE_CHARS,
    NBSP,
    ROMAN_NUMERALS,
    SENTENCE_PUNCTUATION,
    SINGLE_PRIME,
    SPACES,
    TERMINAL_PUNCTUATION,
)
from pytypopo.locale import Locale
from pytypopo.utils.markdown import identify_markdown_code_ticks, place_markdown_code_ticks

# Single quote adepts - various characters that might represent single quotes/apostrophes
# Includes: ' (straight), ' ' (curly), ‚ (low-9), ‹ › (single guillemets),
# ʼ (modifier letter), ‛ (high-reversed-9), ´ (acute), ` (grave), ′ (prime)
SINGLE_QUOTE_ADEPTS = (
    r"\u201a"  # ‚ single low-9 quotation mark
    r"|'"  # straight single quote
    r"|\u2018"  # ' left single quotation mark
    r"|\u2019"  # ' right single quotation mark
    r"|\u02bc"  # ʼ modifier letter apostrophe
    r"|\u201b"  # ‛ single high-reversed-9 quotation mark
    r"|\u00b4"  # ´ acute accent
    r"|`"  # grave accent / backtick
    r"|\u2032"  # ′ prime
    r"|\u2039"  # ‹ single left-pointing angle quotation mark
    r"|\u203a"  # › single right-pointing angle quotation mark
)


def _get_locale(locale):
    """Convert locale string to Locale instance if needed."""
    if isinstance(locale, str):
        return Locale(locale)
    return locale


def identify_contracted_and(text, locale):
    """
    Identify 'n' contractions as apostrophes.

    Example:
        rock 'n' roll -> rock 'n' roll
        fish 'n' chips -> fish 'n' chips

    Exceptions:
        Press 'N' to continue (should be identified as single quotes)
    """
    common_contractions = [
        ("dead", "buried"),
        ("drill", "bass"),
        ("drum", "bass"),
        ("rock", "roll"),
        ("pick", "mix"),
        ("fish", "chips"),
        ("salt", "shake"),
        ("mac", "cheese"),
        ("pork", "beans"),
        ("drag", "drop"),
        ("rake", "scrape"),
        ("hook", "kill"),
    ]

    for first, second in common_contractions:
        pattern = re.compile(
            rf"({first})"
            rf"([{SPACES}]?)"
            rf"({SINGLE_QUOTE_ADEPTS})"
            rf"(n)"
            rf"({SINGLE_QUOTE_ADEPTS})"
            rf"([{SPACES}]?)"
            rf"({second})",
            re.IGNORECASE,
        )
        text = pattern.sub(rf"\1{NBSP}{{{{typopo__apostrophe}}}}\4{{{{typopo__apostrophe}}}}{NBSP}\7", text)

    return text


def identify_contracted_beginnings(text, locale):
    """
    Identify common contractions at word beginning as apostrophes.

    Example:
        'em, 'cause, 'til, 'tis, etc.
    """
    contracted_words = (
        "cause|em|mid|midst|mongst|prentice|round|sblood|sdeath|sfoot|sheart|"
        "shun|slid|slife|slight|snails|strewth|til|tis|twas|tween|twere|twill|twixt|twould"
    )

    pattern = re.compile(
        rf"({SINGLE_QUOTE_ADEPTS})"
        rf"({contracted_words})",
        re.IGNORECASE,
    )
    return pattern.sub(r"{{typopo__apostrophe}}\2", text)


def identify_contracted_ends(text, locale):
    """
    Identify common contractions at word end as apostrophes.

    Example:
        contraction of an -ing form, e.g. nottin', gettin'
    """
    pattern = re.compile(
        rf"(\Bin)"
        rf"({SINGLE_QUOTE_ADEPTS})",
        re.IGNORECASE,
    )
    return pattern.sub(r"\1{{typopo__apostrophe}}", text)


def identify_in_word_contractions(text, locale):
    """
    Identify in-word contractions as apostrophes.

    Examples:
        Don't, I'm, O'Doole, 69'ers, iPhone6's
    """
    pattern = re.compile(
        rf"([\d{ALL_CHARS}])"
        rf"({SINGLE_QUOTE_ADEPTS})+"
        rf"([{ALL_CHARS}])"
    )
    return pattern.sub(r"\1{{typopo__apostrophe}}\3", text)


def identify_contracted_years(text, locale):
    """
    Identify contracted years.

    Example:
        in '70s, INCHEBA '89, Q1 '23

    Exceptions:
        12 '45" (wrongly spaced feet - not a year)
    """
    pattern = re.compile(
        rf"([^0-9]|[A-Z][0-9])"
        rf"([{SPACES}])"
        rf"({SINGLE_QUOTE_ADEPTS})"
        rf"([\d]{{2}})"
    )
    return pattern.sub(r"\1\2{{typopo__apostrophe}}\4", text)


def identify_single_prime_as_feet(text, locale):
    """
    Identify feet and arcminutes following 1-3 digit numbers.

    Example:
        12' 45" -> 12' 45"

    Single-quotes module impact:
    Function may falsely identify feet where we expect quotes, e.g.
    'Konference 2020' in quotes -> 'Konference 2020' in quotes
    This is corrected in replace_single_prime_with_single_quote
    """
    pattern = re.compile(
        rf"(\d)"
        rf"([{SPACES}]?)"
        rf"('|\u2018|\u2019|\u201b|\u2032)"
    )
    return pattern.sub(r"\1\2{{typopo__single-prime}}", text)


def identify_unpaired_left_single_quote(text, locale):
    """
    Identify unpaired left single quote.

    Algorithm:
    Find left single quotes:
    - following a space, en dash or em dash
    - preceding a word
    """
    pattern = re.compile(
        rf"(^|[{SPACES}{EM_DASH}{EN_DASH}])"
        rf"({SINGLE_QUOTE_ADEPTS}|,)"
        rf"([{ALL_CHARS}{ELLIPSIS}])"
    )
    return pattern.sub(r"\1{{typopo__lsq--unpaired}}\3", text)


def identify_unpaired_right_single_quote(text, locale):
    """
    Identify unpaired right single quote.

    Algorithm:
    Find right single quotes:
    - following a word
    - optionally, following a sentence punctuation
    - optionally, preceding a space or a sentence punctuation
    """
    pattern = re.compile(
        rf"([{ALL_CHARS}])"
        rf"([{SENTENCE_PUNCTUATION}{ELLIPSIS}])?"
        rf"({SINGLE_QUOTE_ADEPTS})"
        rf"([ {SENTENCE_PUNCTUATION}])?"
    )
    return pattern.sub(r"\1\2{{typopo__rsq--unpaired}}\4", text)


def identify_single_quotes_within_double_quotes(text, locale):
    """
    Identify single quotes within double quotes.

    Limitations:
    Since it's difficult to identify apostrophe contracting end of word (e.g. "jes'"),
    it's difficult to identify single quotes universally. Therefore we identify only
    single quotes and single quote pairs enclosed in double quote pairs.

    Algorithm:
    - find text in double quotes
    - in quoted text find:
      - unpaired left single quote
      - unpaired right single quote
      - single quote pairs
    """
    # Double quote adepts pattern
    double_quote_adepts = (
        r'"'  # straight quote
        r"|\u201c"  # left double quotation mark
        r"|\u201d"  # right double quotation mark
        r"|\u201e"  # double low-9 quotation mark
        r"|\u00ab"  # left guillemet
        r"|\u00bb"  # right guillemet
    )

    def process_inner(match):
        left_dq = match.group(1)
        content = match.group(2)
        right_dq = match.group(3)

        content = identify_unpaired_left_single_quote(content, locale)
        content = identify_unpaired_right_single_quote(content, locale)
        content = identify_single_quote_pairs(content, locale)

        return left_dq + content + right_dq

    pattern = re.compile(
        rf"({double_quote_adepts})"
        rf"(.*?)"
        rf"({double_quote_adepts})"
    )
    return pattern.sub(process_inner, text)


def identify_single_quote_pairs(text, locale):
    """
    Identify single quote pairs.

    Example:
        "a 'quoted material' here" -> "a 'quoted material' here"

    Assumptions and Limitations:
    - This function assumes apostrophes and unpaired single quotes were identified.
    - It is difficult to identify all contractions at the end of word, and thus
      it is difficult to identify single quote pairs.
    """
    pattern = re.compile(
        r"(\{\{typopo__lsq--unpaired\}\})"
        r"(.*)"
        r"(\{\{typopo__rsq--unpaired\}\})"
    )
    return pattern.sub(r"{{typopo__lsq}}\2{{typopo__rsq}}", text)


def identify_single_quote_pair_around_single_word(text, locale):
    """
    Identify single quote pair around a single word.

    Example:
        'word' -> 'word'
        Press 'N' to get started -> Press 'N' to get started
    """
    pattern = re.compile(
        rf"(\B)"
        rf"({SINGLE_QUOTE_ADEPTS})"
        rf"([{ALL_CHARS}]+)"
        rf"({SINGLE_QUOTE_ADEPTS})"
        rf"(\B)"
    )
    return pattern.sub(r"\1{{typopo__lsq}}\3{{typopo__rsq}}\5", text)


def identify_residual_apostrophes(text, locale):
    """
    Identify residual apostrophes.

    Finds remaining single quote adepts and changes them to apostrophes.
    Limitation: This function runs as last in the row of identification functions
    as it catches what's left.
    """
    pattern = re.compile(rf"({SINGLE_QUOTE_ADEPTS})")
    return pattern.sub(r"{{typopo__apostrophe}}", text)


def replace_single_prime_with_single_quote(text, locale):
    """
    Replace a single quote & a single prime with a single quote pair.

    Assumptions and Limitations:
    This function follows previous functions that identify single primes or
    unpaired single quotes. So it may happen that previous functions falsely
    identify a single quote pair around situations such as:
    - He said: "What about 'Localhost 3000', is that good?"

    Algorithm:
    Find unpaired single quote and single prime in pair and change them to
    a single quote pair.
    """
    # Pattern: unpaired-left + content + single-prime -> quote pair
    pattern1 = re.compile(
        r"(\{\{typopo__lsq--unpaired\}\})"
        r"(.*?)"
        r"(\{\{typopo__single-prime\}\})"
    )
    text = pattern1.sub(r"{{typopo__lsq}}\2{{typopo__rsq}}", text)

    # Pattern: single-prime + content + unpaired-right -> quote pair
    pattern2 = re.compile(
        r"(\{\{typopo__single-prime\}\})"
        r"(.*?)"
        r"(\{\{typopo__rsq--unpaired\}\})"
    )
    text = pattern2.sub(r"{{typopo__lsq}}\2{{typopo__rsq}}", text)

    return text


def swap_single_quotes_and_terminal_punctuation(text, locale):
    """
    Swap single quotes and terminal punctuation for a quoted part.

    There are two different rules to follow quotes:
    1. Quotes contain only quoted material:
       'Sometimes it can be a whole sentence.'
       Sometimes it can be only a 'quoted part'.
       The difference is where the terminal and sentence pause punctuation is.
    2. American editorial style:
       Similar as the first rule, but commas (,) and periods (.) go before
       closing quotation marks, regardless whether they are part of the material.

    The aim here is to support the first rule.

    Examples:
        'quoted part.' -> 'quoted part'.  (partial quote)
        'He was ok'. -> 'He was ok.'  (full sentence at start)

    Exception:
        Byl to 'Karel IV.', ktery - preserves roman numeral
    """
    loc = _get_locale(locale)
    left_quote = re.escape(loc.single_quote_open)
    right_quote = re.escape(loc.single_quote_close)

    # Case 1: Quoted part within a sentence - move punctuation outside
    # Match: not-sentence-punct + space + left-quote + content + not-roman + terminal-punct + right-quote
    pattern1 = re.compile(
        rf"([^{SENTENCE_PUNCTUATION}])"
        rf"([{SPACES}])"
        rf"({left_quote})"
        rf"([^{right_quote}]+?)"
        rf"([^{ROMAN_NUMERALS}])"
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
    # Match: start-of-line + left-quote + content + not-roman + right-quote + terminal-punct + non-word-boundary
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
        rf"{right_quote}"
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


def remove_extra_space_around_single_prime(text, locale):
    """
    Remove extra space around a single prime.

    Example:
        12 ' 45" -> 12' 45"

    Assumptions and Limitations:
    The function runs after all single quotes and single primes
    have been identified.
    """
    pattern = re.compile(
        rf"([{SPACES}])"
        rf"({re.escape(SINGLE_PRIME)})"
    )
    return pattern.sub(r"\2", text)


def place_locale_single_quotes(text, locale):
    """
    Replace all identified punctuation with appropriate punctuation in language.

    Context:
    In single-quotes module, we first identify single quote and single prime
    adepts, then replace them temporarily with labels as "{{typopo__single-prime}}".
    This is the function in the sequence to swap temporary labels to quotes.
    """
    loc = _get_locale(locale)

    # Replace single prime placeholder
    text = text.replace("{{typopo__single-prime}}", SINGLE_PRIME)

    # Replace apostrophe and unpaired quotes with apostrophe
    text = re.sub(
        r"\{\{typopo__apostrophe\}\}|\{\{typopo__lsq--unpaired\}\}|\{\{typopo__rsq--unpaired\}\}", APOSTROPHE, text
    )

    # Replace paired quotes with locale-specific quotes
    text = text.replace("{{typopo__lsq}}", loc.single_quote_open)
    text = text.replace("{{typopo__rsq}}", loc.single_quote_close)

    # Replace markdown syntax highlight placeholder (if present)
    text = text.replace("{{typopo__markdown_syntax_highlight}}", "```")

    return text


def fix_single_quotes_primes_and_apostrophes(text, locale, keep_markdown_code_blocks=True):
    """
    Correct improper use of single quotes, single primes and apostrophes.

    Assumptions and Limitations:
    This function assumes that double quotes are always used in pair,
    i.e. authors did not forget to close double quotes in their text.
    Further, single quotes are used as secondary and they're properly spaced,
    e.g. 'word or sentence portion' (and not like ' word ')

    Algorithm:
    [0] Identify markdown code ticks
    [1] Identify common apostrophe contractions
    [2] Identify feet, arcminutes, minutes
    [3] Identify single quote pair around a single word
    [4] Identify single quotes
    [5] Replace a single quote & a single prime with a single quote pair
    [6] Identify residual apostrophes
    [7] Replace all identified punctuation with appropriate punctuation
    [8] Swap quotes and terminal punctuation
    [9] Consolidate spaces around single primes

    Args:
        text: Input text to fix
        locale: Locale identifier or Locale instance
        keep_markdown_code_blocks: If True, preserve markdown backticks

    Returns:
        Text with proper single quotes, primes and apostrophes
    """
    loc = _get_locale(locale)

    # [0] Identify markdown code ticks
    text, markdown_blocks = identify_markdown_code_ticks(text, keep_markdown_code_blocks)

    # [1] Identify common apostrophe contractions
    text = identify_contracted_and(text, loc)
    text = identify_contracted_beginnings(text, loc)
    text = identify_in_word_contractions(text, loc)
    text = identify_contracted_years(text, loc)
    text = identify_contracted_ends(text, loc)

    # [2] Identify feet, arcminutes, minutes
    text = identify_single_prime_as_feet(text, loc)

    # [3] Identify single quote pair around a single word
    text = identify_single_quote_pair_around_single_word(text, loc)

    # [4] Identify single quotes within double quotes
    text = identify_single_quotes_within_double_quotes(text, loc)

    # [5] Replace a single quote & a single prime with a single quote pair
    text = replace_single_prime_with_single_quote(text, loc)

    # [6] Identify residual apostrophes
    text = identify_residual_apostrophes(text, loc)

    # [7] Replace all identified punctuation with appropriate punctuation
    text = place_locale_single_quotes(text, loc)
    text = place_markdown_code_ticks(text, markdown_blocks, keep_markdown_code_blocks)

    # [8] Swap quotes and terminal punctuation
    text = swap_single_quotes_and_terminal_punctuation(text, loc)

    # [9] Consolidate spaces around single primes
    text = remove_extra_space_around_single_prime(text, loc)

    return text


# Alias for consistency with typopo naming
fix_single_quotes = fix_single_quotes_primes_and_apostrophes
