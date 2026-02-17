"""
Tests for multiplication sign fixes: x/X → ×

Port of tests/symbols/multiplication-sign.test.js from typopo.
"""

import pytest

from pytypopo.const import NBSP
from pytypopo.modules.symbols.multiplication_sign import (
    _fix_multiplication_between_numbers,
    _fix_multiplication_between_words,
    _fix_multiplication_number_and_word,
    _fix_multiplication_spacing,
    fix_multiplication_sign,
)

# Test cases for multiplication sign between numbers
# Format: {input: expected_output}
BETWEEN_NUMBERS_TESTS = {
    # Basic number × number
    "5 x 4": f"5{NBSP}×{NBSP}4",
    "5 X 4": f"5{NBSP}×{NBSP}4",
    # With inch/foot marks
    "5″ x 4″": f"5″{NBSP}×{NBSP}4″",
    "5′ x 4′": f"5′{NBSP}×{NBSP}4′",
    # With units
    "5 mm x 5 mm": f"5 mm{NBSP}×{NBSP}5 mm",
    "5 žien X 5 žien": f"5 žien{NBSP}×{NBSP}5 žien",
    # Units attached to numbers
    "5cm x 5cm": f"5cm{NBSP}×{NBSP}5cm",
    # Multiple dimensions
    "5 x 4 x 3": f"5{NBSP}×{NBSP}4{NBSP}×{NBSP}3",
    "5″ x 4″ x 3″": f"5″{NBSP}×{NBSP}4″{NBSP}×{NBSP}3″",
    "5 mm x 5 mm x 5 mm": f"5 mm{NBSP}×{NBSP}5 mm{NBSP}×{NBSP}5 mm",
    # False positives - should NOT be replaced
    "4xenographs": "4xenographs",
    "0xd": "0xd",
}


# Test cases for multiplication sign between words
# Format: {input: expected_output}
BETWEEN_WORDS_TESTS = {
    # Dimension abbreviations
    "š x v x h": f"š{NBSP}×{NBSP}v{NBSP}×{NBSP}h",
    "mm x mm": f"mm{NBSP}×{NBSP}mm",
    # Names (sports matchups, etc.)
    "Marciano x Clay": f"Marciano{NBSP}×{NBSP}Clay",
    # Words with diacritics
    "žena x žena": f"žena{NBSP}×{NBSP}žena",
    # False positives - should NOT be replaced
    "light xenons": "light xenons",
    "František X Šalda": "František X Šalda",
}


# Test cases for multiplication sign between number and word
# Format: {input: expected_output}
NUMBER_AND_WORD_TESTS = {
    # With space
    "4 x object": f"4{NBSP}×{NBSP}object",
    # Without space before x
    "4x object": f"4×{NBSP}object",
    "4X object": f"4×{NBSP}object",
    # With diacritics
    "4X žena": f"4×{NBSP}žena",
    # False positives - should NOT be replaced
    "4 xenographs": "4 xenographs",
    "4xenographs": "4xenographs",
    "0xd": "0xd",
    # Pipe character is not multiplication
    "4 | object": "4 | object",
}


# Test cases for spacing around multiplication sign
# Format: {input: expected_output}
SPACING_TESTS = {
    # Missing spaces should be added
    "12x3": f"12{NBSP}×{NBSP}3",
    "12×3": f"12{NBSP}×{NBSP}3",
    # With inch marks
    "12″×3″": f"12″{NBSP}×{NBSP}3″",
    # With foot marks
    "12′×3′": f"12′{NBSP}×{NBSP}3′",
}


class TestFixMultiplicationSignBetweenNumbers:
    """Tests for fixing multiplication sign between numbers."""

    @pytest.mark.parametrize(("input_text", "expected"), BETWEEN_NUMBERS_TESTS.items())
    def test_fix_multiplication_between_numbers(self, input_text, expected, locale):
        """Multiplication x/X between numbers should be replaced with ×."""
        result = fix_multiplication_sign(input_text, locale)
        assert result == expected


class TestFixMultiplicationSignBetweenWords:
    """Tests for fixing multiplication sign between words."""

    @pytest.mark.parametrize(("input_text", "expected"), BETWEEN_WORDS_TESTS.items())
    def test_fix_multiplication_between_words(self, input_text, expected, locale):
        """Multiplication x/X between words should be replaced with ×."""
        result = fix_multiplication_sign(input_text, locale)
        assert result == expected


class TestFixMultiplicationSignBetweenNumberAndWord:
    """Tests for fixing multiplication sign between number and word."""

    @pytest.mark.parametrize(("input_text", "expected"), NUMBER_AND_WORD_TESTS.items())
    def test_fix_multiplication_between_number_and_word(self, input_text, expected, locale):
        """Multiplication x/X between number and word should be replaced with ×."""
        result = fix_multiplication_sign(input_text, locale)
        assert result == expected


class TestFixMultiplicationSignSpacing:
    """Tests for fixing spacing around multiplication sign."""

    @pytest.mark.parametrize(("input_text", "expected"), SPACING_TESTS.items())
    def test_fix_multiplication_spacing(self, input_text, expected, locale):
        """Spacing around multiplication sign should be normalized."""
        result = fix_multiplication_sign(input_text, locale)
        assert result == expected


# ============================================================================
# Helper function tests (unit tests for internal functions)
# ============================================================================


class TestHelperFixMultiplicationBetweenNumbers:
    """Unit tests for _fix_multiplication_between_numbers helper function."""

    @pytest.mark.parametrize(("input_text", "expected"), BETWEEN_NUMBERS_TESTS.items())
    def test_helper_between_numbers(self, input_text, expected):
        """Test _fix_multiplication_between_numbers directly."""
        result = _fix_multiplication_between_numbers(input_text)
        assert result == expected


class TestHelperFixMultiplicationBetweenWords:
    """Unit tests for _fix_multiplication_between_words helper function."""

    @pytest.mark.parametrize(("input_text", "expected"), BETWEEN_WORDS_TESTS.items())
    def test_helper_between_words(self, input_text, expected):
        """Test _fix_multiplication_between_words directly."""
        result = _fix_multiplication_between_words(input_text)
        assert result == expected


class TestHelperFixMultiplicationNumberAndWord:
    """Unit tests for _fix_multiplication_number_and_word helper function."""

    @pytest.mark.parametrize(("input_text", "expected"), NUMBER_AND_WORD_TESTS.items())
    def test_helper_number_and_word(self, input_text, expected):
        """Test _fix_multiplication_number_and_word directly."""
        result = _fix_multiplication_number_and_word(input_text)
        assert result == expected


class TestHelperFixMultiplicationSpacing:
    """Unit tests for _fix_multiplication_spacing helper function."""

    @pytest.mark.parametrize(("input_text", "expected"), SPACING_TESTS.items())
    def test_helper_spacing(self, input_text, expected):
        """Test _fix_multiplication_spacing directly."""
        result = _fix_multiplication_spacing(input_text)
        assert result == expected
