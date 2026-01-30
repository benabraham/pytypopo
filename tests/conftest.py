"""
pytest configuration and shared fixtures for pytypopo tests.

Port of tests/test-utils.js from typopo.
"""

import pytest

# All supported locales
ALL_LOCALES = ["en-us", "de-de", "cs", "sk", "rue"]


@pytest.fixture(params=ALL_LOCALES)
def locale(request):
    """Fixture that parametrizes tests across all supported locales."""
    return request.param


# Space constants
NBSP = "\u00a0"  # Non-breaking space
SPACE = " "  # Regular space

# Locale-specific tokens for test data substitution
# These will be replaced with actual locale values at test time
# Quote characters:
# en-us: U+201C (") U+201D (") U+2018 (') U+2019 (')
# de-de/cs/sk: U+201E (,,) U+201C (") U+201A (,) U+2019 (')
# rue: U+00AB (<<) U+00BB (>>) U+2039 (<) U+203A (>)
LOCALE_TOKENS = {
    "en-us": {
        "double_open": "\u201c",  # LEFT DOUBLE QUOTATION MARK
        "double_close": "\u201d",  # RIGHT DOUBLE QUOTATION MARK
        "single_open": "\u2018",  # LEFT SINGLE QUOTATION MARK
        "single_close": "\u2019",  # RIGHT SINGLE QUOTATION MARK
        "abbr_space": "",  # en-us: no space between abbreviated words
        "copyright_space": NBSP,  # en-us: nbsp after copyright symbols
    },
    "de-de": {
        "double_open": "\u201e",  # DOUBLE LOW-9 QUOTATION MARK
        "double_close": "\u201d",  # RIGHT DOUBLE QUOTATION MARK
        "single_open": "\u201a",  # SINGLE LOW-9 QUOTATION MARK
        "single_close": "\u2019",  # RIGHT SINGLE QUOTATION MARK
        "abbr_space": NBSP,  # de-de: nbsp between abbreviated words
        "copyright_space": NBSP,  # de-de: nbsp after copyright symbols
    },
    "cs": {
        "double_open": "\u201e",  # DOUBLE LOW-9 QUOTATION MARK
        "double_close": "\u201d",  # RIGHT DOUBLE QUOTATION MARK
        "single_open": "\u201a",  # SINGLE LOW-9 QUOTATION MARK
        "single_close": "\u2019",  # RIGHT SINGLE QUOTATION MARK
        "abbr_space": NBSP,  # cs: nbsp between abbreviated words
        "copyright_space": SPACE,  # cs: regular space after copyright symbols
    },
    "sk": {
        "double_open": "\u201e",  # DOUBLE LOW-9 QUOTATION MARK
        "double_close": "\u201d",  # RIGHT DOUBLE QUOTATION MARK
        "single_open": "\u201a",  # SINGLE LOW-9 QUOTATION MARK
        "single_close": "\u2019",  # RIGHT SINGLE QUOTATION MARK
        "abbr_space": NBSP,  # sk: nbsp between abbreviated words
        "copyright_space": NBSP,  # sk: nbsp after copyright symbols
    },
    "rue": {
        "double_open": "\u00ab",  # LEFT-POINTING DOUBLE ANGLE QUOTATION MARK
        "double_close": "\u00bb",  # RIGHT-POINTING DOUBLE ANGLE QUOTATION MARK
        "single_open": "\u2039",  # SINGLE LEFT-POINTING ANGLE QUOTATION MARK
        "single_close": "\u203a",  # SINGLE RIGHT-POINTING ANGLE QUOTATION MARK
        "abbr_space": NBSP,  # rue: nbsp between abbreviated words
        "copyright_space": NBSP,  # rue: nbsp after copyright symbols
    },
}


def transform_test_value(value, locale):
    """
    Replace locale-specific tokens in test values.

    Tokens like {double_open} are replaced with the actual
    quote characters for the given locale.
    """
    if not isinstance(value, str):
        return value

    tokens = LOCALE_TOKENS.get(locale, LOCALE_TOKENS["en-us"])
    result = value
    for token_name, token_value in tokens.items():
        result = result.replace(f"{{{token_name}}}", token_value)
    return result


def create_test_cases(test_data, locale=None):
    """
    Convert a test data dict to pytest parametrize format.

    Args:
        test_data: Dict of {input: expected_output}
        locale: Optional locale for token substitution

    Returns:
        List of (input, expected) tuples for parametrize
    """
    cases = []
    for input_text, expected in test_data.items():
        if locale:
            input_text = transform_test_value(input_text, locale)
            expected = transform_test_value(expected, locale)
        cases.append((input_text, expected))
    return cases
