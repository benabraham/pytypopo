"""
Shared fixtures and utilities for symbol tests.

Port of tests/symbols/symbol-utils.test.js from typopo.
"""

from pytypopo.const import (
    NARROW_NBSP,
    NBSP,
    NUMERO_SIGN,
    PARAGRAPH_SIGN,
    SECTION_SIGN,
)


# Space to use after symbols - varies by locale
# For most locales, narrow non-breaking space is used
# (This matches typopo's locale.spaceAfter behavior)
def get_space_after_symbol(locale, symbol_name):
    """Get the space character to use after a symbol for a given locale."""
    # In typopo, this is determined by locale.spaceAfter[symbolName]
    # For now, we use narrow nbsp as that's the common case
    return NARROW_NBSP


# Symbol mapping for test template expansion
SYMBOLS = {
    "numeroSign": NUMERO_SIGN,
    "sectionSign": SECTION_SIGN,
    "paragraphSign": PARAGRAPH_SIGN,
}


def expand_symbol_template(template, symbol_name, locale):
    """
    Expand a symbol test template with actual symbol and space characters.

    Templates use ${symbol} and ${space} placeholders.

    Args:
        template: String with ${symbol} and ${space} placeholders
        symbol_name: Name of symbol ('numeroSign', 'sectionSign', 'paragraphSign')
        locale: Locale string for determining space character

    Returns:
        Expanded string with actual characters
    """
    symbol = SYMBOLS[symbol_name]
    space = get_space_after_symbol(locale, symbol_name)

    result = template.replace("${symbol}", symbol)
    result = result.replace("${space}", space)
    return result


def create_symbol_test_cases(symbol_set, symbol_name, locale):
    """
    Create test cases from a symbol set template.

    Args:
        symbol_set: Dict of {input_template: expected_template}
        symbol_name: Name of symbol to substitute
        locale: Locale string for determining space character

    Returns:
        List of (input, expected) tuples for parametrize
    """
    cases = []
    for input_template, expected_template in symbol_set.items():
        input_text = expand_symbol_template(input_template, symbol_name, locale)
        expected = expand_symbol_template(expected_template, symbol_name, locale)
        cases.append((input_text, expected))
    return cases


# Base symbol test set - templates for all symbol spacing tests
# These templates come from typopo's symbol-utils.test.js
SYMBOL_SET = {
    # Spaces around the symbol
    "Company${symbol} 2017": "Company ${symbol}${space}2017",
    "Company ${symbol} 2017": "Company ${symbol}${space}2017",
    "Company ${symbol}  2017": "Company ${symbol}${space}2017",
    "Company ${symbol}   2017": "Company ${symbol}${space}2017",
    f"Company ${{symbol}}{NBSP}2017": "Company ${symbol}${space}2017",
    "Company ${symbol}2017": "Company ${symbol}${space}2017",
    "Company ${symbol}${symbol}2017": "Company ${symbol}${symbol}${space}2017",
    # Punctuation contexts
    "text.${symbol}1": "text. ${symbol}${space}1",
    "text,${symbol}1": "text, ${symbol}${space}1",
    "text;${symbol}1": "text; ${symbol}${space}1",
    "text:${symbol}1": "text: ${symbol}${space}1",
    "text!${symbol}1": "text! ${symbol}${space}1",
    "text?${symbol}1": "text? ${symbol}${space}1",
    # Special character contexts
    "#${symbol}1": "# ${symbol}${space}1",
    "@${symbol}section": "@ ${symbol}${space}section",
    "*${symbol}note": "* ${symbol}${space}note",
    "&${symbol}clause": "& ${symbol}${space}clause",
    "%${symbol}rate": "% ${symbol}${space}rate",
    "$${symbol}cost": "$ ${symbol}${space}cost",
    # Bracket edge cases
    "(${symbol}1)": "(${symbol}${space}1)",
    "[${symbol}1]": "[${symbol}${space}1]",
    "{${symbol}1}": "{${symbol}${space}1}",
    "(${symbol}${symbol}1)": "(${symbol}${symbol}${space}1)",
    # Start/end of string
    "${symbol}text": "${symbol}${space}text",
    "text ${symbol}1": "text ${symbol}${space}1",
    # Already correct (narrow nbsp used)
    f"Article ${{symbol}}{NARROW_NBSP}1": f"Article ${{symbol}}{NARROW_NBSP}1",
    f"Document ${{symbol}}{NARROW_NBSP}123": f"Document ${{symbol}}{NARROW_NBSP}123",
}

# Additional tests with quotes
SYMBOL_SET_INCL_QUOTES = {
    '"text"${symbol}1': '"text" ${symbol}${space}1',
    "'text'${symbol}1": "'text' ${symbol}${space}1",
    "`code`${symbol}1": "`code` ${symbol}${space}1",
}
