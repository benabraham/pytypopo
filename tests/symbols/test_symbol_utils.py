"""
Tests for symbol spacing utility function.

Port of tests/symbols/symbol-utils.test.js from typopo.
Tests the fix_spacing_around_symbol() helper function.
"""

import pytest

from pytypopo.const import (
    COPYRIGHT,
    NBSP,
    NUMERO_SIGN,
    PARAGRAPH_SIGN,
    SECTION_SIGN,
    SOUND_RECORDING_COPYRIGHT,
)
from pytypopo.locale import get_locale
from pytypopo.modules.symbols.section_sign import fix_spacing_around_symbol

# All supported locales
ALL_LOCALES = ["en-us", "de-de", "cs", "sk", "rue"]

# Test symbols and their locale attribute names
SYMBOLS = [
    (COPYRIGHT, "space_after_copyright"),
    (SOUND_RECORDING_COPYRIGHT, "space_after_sound_recording_copyright"),
    (SECTION_SIGN, "space_after_section_sign"),
    (PARAGRAPH_SIGN, "space_after_paragraph_sign"),
    (NUMERO_SIGN, "space_after_numero_sign"),
]


def get_symbol_test_cases(symbol, space):
    """Generate test cases for a symbol with given space_after character."""
    s = symbol
    sp = space
    return {
        # Spaces around the symbol
        f"Company{s} 2017": f"Company {s}{sp}2017",
        f"Company {s} 2017": f"Company {s}{sp}2017",
        f"Company {s}  2017": f"Company {s}{sp}2017",
        f"Company {s}   2017": f"Company {s}{sp}2017",
        f"Company {s}2017": f"Company {s}{sp}2017",
        f"Company {s}{s}2017": f"Company {s}{s}{sp}2017",
        # Punctuation contexts
        f"text.{s}1": f"text. {s}{sp}1",
        f"text,{s}1": f"text, {s}{sp}1",
        f"text;{s}1": f"text; {s}{sp}1",
        f"text:{s}1": f"text: {s}{sp}1",
        f"text!{s}1": f"text! {s}{sp}1",
        f"text?{s}1": f"text? {s}{sp}1",
        # Special character contexts
        f"#{s}1": f"# {s}{sp}1",
        f"@{s}section": f"@ {s}{sp}section",
        f"*{s}note": f"* {s}{sp}note",
        f"&{s}clause": f"& {s}{sp}clause",
        f"%{s}rate": f"% {s}{sp}rate",
        f"${s}cost": f"$ {s}{sp}cost",
        # Bracket edge cases
        f"({s}1)": f"({s}{sp}1)",
        f"[{s}1]": f"[{s}{sp}1]",
        f"{{{s}1}}": f"{{{s}{sp}1}}",
        f"({s}{s}1)": f"({s}{s}{sp}1)",
        # Start/end of string
        f"{s}text": f"{s}{sp}text",
        f"text {s}1": f"text {s}{sp}1",
        # Already correct
        f"Article {s}{sp}1": f"Article {s}{sp}1",
        f"Document {s}{sp}123": f"Document {s}{sp}123",
        # Quote contexts
        f'"text"{s}1': f'"text" {s}{sp}1',
        f"'text'{s}1": f"'text' {s}{sp}1",
        f"`code`{s}1": f"`code` {s}{sp}1",
    }


class TestFixSpacingAroundSymbol:
    """Tests for fix_spacing_around_symbol utility function."""

    @pytest.mark.parametrize("locale_name", ALL_LOCALES)
    @pytest.mark.parametrize(("symbol", "space_attr"), SYMBOLS)
    def test_symbol_spacing(self, locale_name, symbol, space_attr):
        """Test spacing fixes for various symbols across locales."""
        locale = get_locale(locale_name)
        space_after = getattr(locale, space_attr)
        test_cases = get_symbol_test_cases(symbol, space_after)

        for input_text, expected in test_cases.items():
            result = fix_spacing_around_symbol(input_text, symbol, space_after)
            assert result == expected, (
                f'{locale_name}, {symbol}: "{input_text}" -> expected "{expected}", got "{result}"'
            )


class TestFixSpacingAroundSymbolUnit:
    """Unit tests for fix_spacing_around_symbol with fixed NBSP."""

    @pytest.mark.parametrize(
        ("input_text", "expected"),
        [
            # Basic spacing
            (f"Company{SECTION_SIGN} 2017", f"Company {SECTION_SIGN}{NBSP}2017"),
            (f"Company {SECTION_SIGN}2017", f"Company {SECTION_SIGN}{NBSP}2017"),
            (f"{SECTION_SIGN}1", f"{SECTION_SIGN}{NBSP}1"),
            # Multiple symbols
            (f"{SECTION_SIGN}{SECTION_SIGN}1", f"{SECTION_SIGN}{SECTION_SIGN}{NBSP}1"),
            # Already correct
            (f"Article {SECTION_SIGN}{NBSP}1", f"Article {SECTION_SIGN}{NBSP}1"),
            # Brackets - should not add space before symbol after opening bracket
            (f"({SECTION_SIGN}1)", f"({SECTION_SIGN}{NBSP}1)"),
            (f"[{SECTION_SIGN}1]", f"[{SECTION_SIGN}{NBSP}1]"),
        ],
    )
    def test_section_sign_spacing(self, input_text, expected):
        """Test section sign spacing with NBSP."""
        result = fix_spacing_around_symbol(input_text, SECTION_SIGN, NBSP)
        assert result == expected
