"""
Tests for trademark/service mark symbol fixes: (r) → ®, (tm) → ™, (sm) → ℠

Port of tests/symbols/marks.test.js from typopo.
"""

import pytest

from pytypopo.const import REGISTERED_TRADEMARK, SERVICE_MARK, TRADEMARK
from pytypopo.modules.symbols.marks import _replace_mark, fix_marks

# Test cases for registered trademark symbol (®)
# Format: {input: expected_output}
REGISTERED_TRADEMARK_TESTS = {
    # Basic replacements
    "(r)": "®",
    "(R)": "®",
    # With company name - single space removed
    "Company (r)": "Company®",
    "Company ®": "Company®",
    # With company name - double space removed
    "Company  (r)": "Company®",
    "Company  ®": "Company®",
    # With company name - triple space removed
    "Company   (r)": "Company®",
    "Company   ®": "Company®",
    # False positives - should NOT be replaced
    "Item (R-1000)": "Item (R-1000)",
    "Section 7(r)": "Section 7(r)",
}


# Test cases for service mark symbol (℠)
# Format: {input: expected_output}
SERVICE_MARK_TESTS = {
    # Basic replacements
    "(sm)": "℠",
    "(SM)": "℠",
    # With company name - single space removed
    "Company (sm)": "Company℠",
    "Company ℠": "Company℠",
    # With company name - double space removed
    "Company  (sm)": "Company℠",
    "Company  ℠": "Company℠",
    # With company name - triple space removed
    "Company   (sm)": "Company℠",
    "Company   ℠": "Company℠",
    # False positives - should NOT be replaced
    "Item (SM-1000)": "Item (SM-1000)",
    "Section 7(s)": "Section 7(s)",
}


# Test cases for trademark symbol (™)
# Format: {input: expected_output}
TRADEMARK_TESTS = {
    # Basic replacements
    "(tm)": "™",
    "(TM)": "™",
    # With company name - single space removed
    "Company (tm)": "Company™",
    "Company ™": "Company™",
    # With company name - double space removed
    "Company  (tm)": "Company™",
    "Company  ™": "Company™",
    # With company name - triple space removed
    "Company   (tm)": "Company™",
    "Company   ™": "Company™",
    # False positives - should NOT be replaced
    "Item (TM-1000)": "Item (TM-1000)",
    "Section 7(t)": "Section 7(t)",
}


class TestFixRegisteredTrademark:
    """Tests for fixing registered trademark symbol (r) → ®."""

    @pytest.mark.parametrize(("input_text", "expected"), REGISTERED_TRADEMARK_TESTS.items())
    def test_fix_registered_trademark(self, input_text, expected, locale):
        """Registered trademark (r) and (R) should be replaced with ®."""
        result = fix_marks(input_text, locale)
        assert result == expected


class TestFixServiceMark:
    """Tests for fixing service mark symbol (sm) → ℠."""

    @pytest.mark.parametrize(("input_text", "expected"), SERVICE_MARK_TESTS.items())
    def test_fix_service_mark(self, input_text, expected, locale):
        """Service mark (sm) and (SM) should be replaced with ℠."""
        result = fix_marks(input_text, locale)
        assert result == expected


class TestFixTrademark:
    """Tests for fixing trademark symbol (tm) → ™."""

    @pytest.mark.parametrize(("input_text", "expected"), TRADEMARK_TESTS.items())
    def test_fix_trademark(self, input_text, expected, locale):
        """Trademark (tm) and (TM) should be replaced with ™."""
        result = fix_marks(input_text, locale)
        assert result == expected


# ============================================================================
# Helper function tests (unit tests for internal functions)
# ============================================================================


class TestHelperReplaceMark:
    """Unit tests for _replace_mark helper function."""

    @pytest.mark.parametrize(("input_text", "expected"), REGISTERED_TRADEMARK_TESTS.items())
    def test_helper_replace_mark_r(self, input_text, expected):
        """Test _replace_mark with 'r' for registered trademark symbol."""
        result = _replace_mark(input_text, "r", REGISTERED_TRADEMARK)
        assert result == expected

    @pytest.mark.parametrize(("input_text", "expected"), SERVICE_MARK_TESTS.items())
    def test_helper_replace_mark_sm(self, input_text, expected):
        """Test _replace_mark with 'sm' for service mark symbol."""
        result = _replace_mark(input_text, "sm", SERVICE_MARK)
        assert result == expected

    @pytest.mark.parametrize(("input_text", "expected"), TRADEMARK_TESTS.items())
    def test_helper_replace_mark_tm(self, input_text, expected):
        """Test _replace_mark with 'tm' for trademark symbol."""
        result = _replace_mark(input_text, "tm", TRADEMARK)
        assert result == expected
