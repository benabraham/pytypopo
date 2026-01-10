"""
Tests for markdown code block extraction and restoration.

Port of tests/utils/markdown.test.js from typopo.
"""

import pytest

from pytypopo.utils.markdown import (
    identify_markdown_code_ticks,
    place_markdown_code_ticks,
)

# Test cases for identify_markdown_code_ticks
# The function now extracts entire code blocks and returns them in a list
# Format: (input, expected_placeholder_count, expected_blocks)
IDENTIFY_TESTS = [
    # Triple backticks (fenced code blocks)
    ("```\ncode\n```", 1, ["```\ncode\n```"]),
    # Triple backticks with language identifier
    ("```python\nprint(1)\n```", 1, ["```python\nprint(1)\n```"]),
    # Double backticks (inline code with backtick inside)
    ("``code``", 1, ["``code``"]),
    # Double backticks with space in code
    ("``code code``", 1, ["``code code``"]),
    # Multiple double backtick segments
    ("``code`` ``code``", 2, ["``code``", "``code``"]),
    # Single backticks (inline code)
    ("`code`", 1, ["`code`"]),
    # Single backticks with space in code
    ("`code code`", 1, ["`code code`"]),
    # Multiple single backtick segments
    ("`code` `code`", 2, ["`code`", "`code`"]),
    # Mixed with text
    ("before `code` after", 1, ["`code`"]),
    # Code with quotes inside
    ('`code with "quotes"`', 1, ['`code with "quotes"`']),
]


# Test cases for when markdown processing is disabled (passthrough)
# Input should equal output with empty blocks list
IGNORE_TESTS = [
    "```\ncode\n```",
    "\t```\ncode\n```",
    "``code``",
    "`code`",
    "`code code`",
]


class TestIdentifyMarkdownCodeTicks:
    """Tests for identify_markdown_code_ticks function."""

    @pytest.mark.parametrize(("input_text", "expected_count", "expected_blocks"), IDENTIFY_TESTS)
    def test_extracts_code_blocks(self, input_text, expected_count, expected_blocks):
        """Code blocks should be extracted and replaced with placeholders."""
        result_text, blocks = identify_markdown_code_ticks(input_text, keep_markdown_code_blocks=True)

        # Check correct number of blocks extracted
        assert len(blocks) == expected_count

        # Check blocks match expected
        assert blocks == expected_blocks

        # Check result text contains placeholders (not the original code blocks)
        for block in expected_blocks:
            assert block not in result_text

    @pytest.mark.parametrize("input_text", IGNORE_TESTS)
    def test_passthrough_when_disabled(self, input_text):
        """When disabled, input should pass through unchanged with empty blocks."""
        result_text, blocks = identify_markdown_code_ticks(input_text, keep_markdown_code_blocks=False)
        assert result_text == input_text
        assert blocks == []


class TestPlaceMarkdownCodeTicks:
    """Tests for place_markdown_code_ticks function."""

    def test_restores_single_block(self):
        """Single code block should be restored from placeholder."""
        original = "`code`"
        text, blocks = identify_markdown_code_ticks(original, keep_markdown_code_blocks=True)
        restored = place_markdown_code_ticks(text, blocks, keep_markdown_code_blocks=True)
        assert restored == original

    def test_restores_multiple_blocks(self):
        """Multiple code blocks should be restored in order."""
        original = "`first` and `second`"
        text, blocks = identify_markdown_code_ticks(original, keep_markdown_code_blocks=True)
        restored = place_markdown_code_ticks(text, blocks, keep_markdown_code_blocks=True)
        assert restored == original

    def test_restores_fenced_block(self):
        """Fenced code block should be restored."""
        original = '```python\nprint("hello")\n```'
        text, blocks = identify_markdown_code_ticks(original, keep_markdown_code_blocks=True)
        restored = place_markdown_code_ticks(text, blocks, keep_markdown_code_blocks=True)
        assert restored == original

    def test_passthrough_when_disabled(self):
        """When disabled, input should pass through unchanged."""
        text = "some text"
        result = place_markdown_code_ticks(text, [], keep_markdown_code_blocks=False)
        assert result == text


class TestRoundTrip:
    """Tests that identify and place are inverse operations."""

    @pytest.mark.parametrize(
        "original",
        [
            "```\ncode\n```",
            '```python\nprint("hello")\n```',
            "``code with `backtick` inside``",
            "`code`",
            "`code code`",
            "`code` `code`",
            "before `code` after",
            '`code with "quotes"`',
            "Some text with `inline code` and more text.",
            "```\nfenced\n```\ntext\n`inline`",
        ],
    )
    def test_identify_then_place_returns_original(self, original):
        """identify -> place should return the original text."""
        text, blocks = identify_markdown_code_ticks(original, keep_markdown_code_blocks=True)
        restored = place_markdown_code_ticks(text, blocks, keep_markdown_code_blocks=True)
        assert restored == original


class TestContentProtection:
    """Tests that content inside code blocks is protected."""

    def test_quotes_preserved(self):
        """Quotes inside code blocks should not be modified."""
        original = '`code with "quotes"`'
        text, blocks = identify_markdown_code_ticks(original, keep_markdown_code_blocks=True)

        # The placeholder should not contain the original quotes
        assert '"' not in text

        # Restoring should give us the original with quotes intact
        restored = place_markdown_code_ticks(text, blocks, keep_markdown_code_blocks=True)
        assert restored == original
        assert '"quotes"' in restored

    def test_special_chars_preserved(self):
        """Special characters inside code blocks should be preserved."""
        original = "`x = 3 * 2 + 1`"
        text, blocks = identify_markdown_code_ticks(original, keep_markdown_code_blocks=True)
        restored = place_markdown_code_ticks(text, blocks, keep_markdown_code_blocks=True)
        assert restored == original
