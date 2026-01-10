"""
Tests for plus-minus symbol (plus/minus) fixing.

Port of tests/symbols/plus-minus.test.js from typopo.
"""

import pytest

from pytypopo.const import PLUS_MINUS
from pytypopo.modules.symbols.plus_minus import fix_plus_minus

# Test cases: input -> expected output
PLUS_MINUS_TESTS = {
    # Plus followed by minus becomes plus-minus
    "+-": PLUS_MINUS,
    # Minus followed by plus also becomes plus-minus
    "-+": PLUS_MINUS,
}


@pytest.mark.parametrize(("input_text", "expected"), PLUS_MINUS_TESTS.items())
def test_fix_plus_minus(input_text, expected, locale):
    """Test that +- and -+ are converted to the plus-minus symbol."""
    assert fix_plus_minus(input_text, locale) == expected
