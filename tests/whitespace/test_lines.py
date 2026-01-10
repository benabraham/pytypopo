"""
Tests for line handling: remove excessive empty lines.

Port of tests/whitespace/lines.test.js from typopo.
"""

import pytest

from pytypopo.modules.whitespace.lines import fix_lines

# Test cases for removing excessive empty lines between paragraphs
# Format: {input: expected_output}
LINES_TESTS = {
    # Remove excessive empty lines between paragraphs
    "line\nline\n\nline\n\n\nline": "line\nline\nline\nline",
    "\n": "\n",
    "\n\n": "\n",
    "\n\n\n": "\n",
    # Mixed line endings (CR+LF)
    "line\nline\r\nline\r\n\nline": "line\nline\nline\nline",
    "\n\r\n": "\n",
    # False positives - preserve intended content
    " - she said": " - she said",  # do not remove space at beginning of paragraph
}


class TestFixLines:
    """Tests for fixing excessive empty lines."""

    @pytest.mark.parametrize(("input_text", "expected"), LINES_TESTS.items())
    def test_fix_lines(self, input_text, expected, locale):
        """Excessive empty lines should be collapsed to single newlines."""
        result = fix_lines(input_text, locale)
        assert result == expected
