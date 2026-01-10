"""
Tests for number sign (#) fixing.

Port of tests/symbols/number-sign.test.js from typopo.
"""

import pytest

from pytypopo.const import HAIR_SPACE, NARROW_NBSP, NBSP
from pytypopo.modules.symbols.number_sign import fix_number_sign, remove_extra_spaces_after_number_sign

# Test cases: input -> expected output
# Remove extra spaces after number sign
NUMBER_SIGN_TESTS = {
    # Basic spacing fixes
    "word # 9": "word #9",
    "word #    9": "word #9",
    # Non-breaking space after #
    f"word #{NBSP}9": "word #9",
    # Hair space after #
    f"word #{HAIR_SPACE}9": "word #9",
    # Narrow non-breaking space after #
    f"word #{NARROW_NBSP}9": "word #9",
}

# False positive protection - markdown headings at start of paragraph
NUMBER_SIGN_FALSE_POSITIVES = {
    # Do not fix position at the beginning of the paragraph as it may be markdown title
    "# 1 markdown title": "# 1 markdown title",
    "## 1. Markdown title": "## 1. Markdown title",
}


@pytest.mark.parametrize(("input_text", "expected"), NUMBER_SIGN_TESTS.items())
def test_fix_number_sign_removes_extra_spaces(input_text, expected, locale):
    """Test that extra spaces after # are removed."""
    assert fix_number_sign(input_text, locale) == expected


@pytest.mark.parametrize(("input_text", "expected"), NUMBER_SIGN_FALSE_POSITIVES.items())
def test_fix_number_sign_preserves_markdown_headings(input_text, expected, locale):
    """Test that markdown headings at paragraph start are preserved."""
    assert fix_number_sign(input_text, locale) == expected


# ============================================================================
# Helper function tests (unit tests for internal functions)
# ============================================================================


class TestHelperRemoveExtraSpacesAfterNumberSign:
    """Unit tests for remove_extra_spaces_after_number_sign helper function."""

    @pytest.mark.parametrize(("input_text", "expected"), NUMBER_SIGN_TESTS.items())
    def test_helper_removes_extra_spaces(self, input_text, expected, locale):
        """Test remove_extra_spaces_after_number_sign directly."""
        result = remove_extra_spaces_after_number_sign(input_text, locale)
        assert result == expected

    @pytest.mark.parametrize(("input_text", "expected"), NUMBER_SIGN_FALSE_POSITIVES.items())
    def test_helper_preserves_markdown_headings(self, input_text, expected, locale):
        """Test that helper preserves markdown headings at paragraph start."""
        result = remove_extra_spaces_after_number_sign(input_text, locale)
        assert result == expected
