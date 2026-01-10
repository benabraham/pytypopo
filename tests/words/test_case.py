"""
Tests for accidental uppercase correction.

Port of tests/words/case.test.js from typopo.
"""

import pytest

from pytypopo.modules.words.case import fix_case

# Test cases for fixing accidental uppercase
# Format: {input: expected_output}
# Two patterns are fixed:
# [1] Two first uppercase letters (UPpercase -> Uppercase)
# [2] Swapped cases (uPPERCASE -> UPPERCASE)
CASE_TESTS = {
    # Pattern [2]: Swapped cases (uPPERCASE -> UPPERCASE)
    "cAPSLOCK and what else.": "Capslock and what else.",
    "Previous sentence. cAPSLOCK and what else.": "Previous sentence. Capslock and what else.",
    "Press cAPSLOCK.": "Press Capslock.",
    # Non-Latin characters (Central European and Cyrillic)
    "aĎIÉUБUГ and what else.": "Aďiéuбuг and what else.",
    "Central Europe and Cyrillic tests: aĎIÉUБUГ": "Central Europe and Cyrillic tests: Aďiéuбuг",
    # In brackets
    "There is (cAPSLOCK) in the brackets.": "There is (Capslock) in the brackets.",
    "There is [cAPSLOCK] in the brackets.": "There is [Capslock] in the brackets.",
    "There is {cAPSLOCK} in the brackets.": "There is {Capslock} in the brackets.",
    # Pattern [1]: Two first uppercase (JEnnifer -> Jennifer)
    "Hey, JEnnifer!": "Hey, Jennifer!",
    # False positives - should NOT be changed
    "CMSko": "CMSko",  # Brand-like pattern
    "FPs": "FPs",  # Abbreviation with suffix
    "ČSNka": "ČSNka",  # Non-Latin abbreviation with suffix
    "BigONE": "BigONE",  # Brand name
    "two Panzer IVs": "two Panzer IVs",  # Roman numeral suffix
    "How about ABC?": "How about ABC?",  # All caps abbreviation
    # Special brand names that should be preserved
    "iPhone": "iPhone",
    "iOS": "iOS",
    "macOS": "macOS",
    # Units - should NOT be changed
    "kW": "kW",  # kilowatt
    "mA": "mA",  # milliampere
}


class TestFixCase:
    """Tests for fixing accidental CAPSLOCK errors."""

    @pytest.mark.parametrize(("input_text", "expected"), CASE_TESTS.items())
    def test_fix_case(self, input_text, expected):
        """Accidental caps should be corrected while preserving valid patterns."""
        result = fix_case(input_text)
        assert result == expected


class TestFixCaseEdgeCases:
    """Additional edge case tests for case fixing."""

    def test_empty_string(self):
        """Empty string should remain empty."""
        assert fix_case("") == ""

    def test_all_lowercase(self):
        """All lowercase text should remain unchanged."""
        text = "this is all lowercase text."
        assert fix_case(text) == text

    def test_all_uppercase(self):
        """All uppercase text should remain unchanged (not accidental)."""
        text = "THIS IS ALL UPPERCASE."
        assert fix_case(text) == text

    def test_normal_capitalization(self):
        """Normal capitalization should remain unchanged."""
        text = "This Is Normal Capitalization."
        assert fix_case(text) == text

    def test_mixed_valid_patterns(self):
        """Mix of valid abbreviations and normal text should be preserved."""
        text = "Use iOS or macOS with your iPhone."
        assert fix_case(text) == text

    def test_sentence_start_preserved(self):
        """First letter capitalization at sentence start should be preserved."""
        text = "Hello World. How are you?"
        assert fix_case(text) == text

    def test_multiple_errors_in_text(self):
        """Multiple accidental caps in same text should all be fixed."""
        input_text = "Hey jOHN, this is mARY speaking."
        expected = "Hey John, this is Mary speaking."
        assert fix_case(input_text) == expected
