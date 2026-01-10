"""
Tests for section sign (section) and paragraph sign (paragraph) spacing.

Port of tests/symbols/section-sign.test.js from typopo.
"""

import pytest

from pytypopo.const import NARROW_NBSP, PARAGRAPH_SIGN, SECTION_SIGN
from pytypopo.modules.symbols.section_sign import fix_section_sign, fix_spacing_around_symbol
from tests.conftest import ALL_LOCALES
from tests.symbols.conftest import (
    SYMBOL_SET,
    expand_symbol_template,
)


def generate_section_sign_tests():
    """Generate test cases for section sign (section) for all locales."""
    test_cases = []

    for locale in ALL_LOCALES:
        for input_template, expected_template in SYMBOL_SET.items():
            input_text = expand_symbol_template(input_template, "sectionSign", locale)
            expected = expand_symbol_template(expected_template, "sectionSign", locale)
            test_cases.append(pytest.param(input_text, expected, locale, id=f"section-{locale}: {input_template[:25]}"))

    return test_cases


def generate_paragraph_sign_tests():
    """Generate test cases for paragraph sign (paragraph) for all locales."""
    test_cases = []

    for locale in ALL_LOCALES:
        for input_template, expected_template in SYMBOL_SET.items():
            input_text = expand_symbol_template(input_template, "paragraphSign", locale)
            expected = expand_symbol_template(expected_template, "paragraphSign", locale)
            test_cases.append(
                pytest.param(input_text, expected, locale, id=f"paragraph-{locale}: {input_template[:25]}")
            )

    return test_cases


@pytest.mark.parametrize(("input_text", "expected", "locale"), generate_section_sign_tests())
def test_fix_section_sign(input_text, expected, locale):
    """Test that section sign spacing is fixed correctly for all locales."""
    assert fix_section_sign(input_text, locale) == expected


@pytest.mark.parametrize(("input_text", "expected", "locale"), generate_paragraph_sign_tests())
def test_fix_paragraph_sign(input_text, expected, locale):
    """Test that paragraph sign spacing is fixed correctly for all locales."""
    # fix_section_sign handles both section and paragraph signs
    assert fix_section_sign(input_text, locale) == expected


# ============================================================================
# Helper function tests (unit tests for internal functions)
# ============================================================================


def generate_fix_spacing_around_symbol_tests(symbol_name, symbol):
    """Generate test cases for fix_spacing_around_symbol helper function."""
    test_cases = []

    for locale in ALL_LOCALES:
        for input_template, expected_template in SYMBOL_SET.items():
            input_text = expand_symbol_template(input_template, symbol_name, locale)
            expected = expand_symbol_template(expected_template, symbol_name, locale)
            test_cases.append(pytest.param(input_text, expected, id=f"{symbol_name}-{locale}: {input_template[:25]}"))

    return test_cases


class TestHelperFixSpacingAroundSymbol:
    """Unit tests for fix_spacing_around_symbol helper function."""

    @pytest.mark.parametrize(
        ("input_text", "expected"), generate_fix_spacing_around_symbol_tests("sectionSign", SECTION_SIGN)
    )
    def test_helper_fix_spacing_section_sign(self, input_text, expected):
        """Test fix_spacing_around_symbol directly with section sign."""
        result = fix_spacing_around_symbol(input_text, SECTION_SIGN, NARROW_NBSP)
        assert result == expected

    @pytest.mark.parametrize(
        ("input_text", "expected"), generate_fix_spacing_around_symbol_tests("paragraphSign", PARAGRAPH_SIGN)
    )
    def test_helper_fix_spacing_paragraph_sign(self, input_text, expected):
        """Test fix_spacing_around_symbol directly with paragraph sign."""
        result = fix_spacing_around_symbol(input_text, PARAGRAPH_SIGN, NARROW_NBSP)
        assert result == expected
