"""
Tests for numero sign (No) spacing.

Port of tests/symbols/numero-sign.test.js from typopo.
"""

import pytest

from pytypopo.modules.symbols.numero_sign import fix_numero_sign
from tests.conftest import ALL_LOCALES
from tests.symbols.conftest import (
    SYMBOL_SET,
    SYMBOL_SET_INCL_QUOTES,
    expand_symbol_template,
)


def generate_numero_sign_tests():
    """Generate test cases for all locales."""
    all_tests = {**SYMBOL_SET, **SYMBOL_SET_INCL_QUOTES}
    test_cases = []

    for locale in ALL_LOCALES:
        for input_template, expected_template in all_tests.items():
            input_text = expand_symbol_template(input_template, "numeroSign", locale)
            expected = expand_symbol_template(expected_template, "numeroSign", locale)
            test_cases.append(pytest.param(input_text, expected, locale, id=f"{locale}: {input_template[:30]}"))

    return test_cases


@pytest.mark.parametrize(("input_text", "expected", "locale"), generate_numero_sign_tests())
def test_fix_numero_sign(input_text, expected, locale):
    """Test that numero sign spacing is fixed correctly for all locales."""
    assert fix_numero_sign(input_text, locale) == expected
