"""
Tests for period fixes: double periods → single period.

Port of tests/punctuation/period.test.js from typopo.
"""

import pytest

from pytypopo.modules.punctuation.period import fix_period

# Test cases for period fixes
# Format: {input: expected_output}
PERIOD_TESTS = {
    # Basic double period fix
    "Sentence ending..": "Sentence ending.",
    # After abbreviations
    "He is a vice president at Apple Inc..": "He is a vice president at Apple Inc.",
    # False positives - file paths should NOT be modified
    "../../src/filename.ext": "../../src/filename.ext",
    "..\\..\\filename.ext": "..\\..\\filename.ext",
    "../": "../",
    "..\\": "..\\",
    # Additional edge cases
    "Multiple... periods": "Multiple. periods",  # Three periods become one (not ellipsis - that's handled elsewhere)
    "Already correct.": "Already correct.",
    "No period here": "No period here",
}


class TestFixPeriod:
    """Tests for fixing double/multiple periods."""

    @pytest.mark.parametrize(("input_text", "expected"), PERIOD_TESTS.items())
    def test_fix_period(self, input_text, expected, locale):
        """Double periods should be replaced with single period."""
        result = fix_period(input_text, locale)
        assert result == expected
