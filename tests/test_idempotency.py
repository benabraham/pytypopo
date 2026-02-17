"""
Idempotency tests for pytypopo.

Port of tests/idempotency.test.js from typopo.
Tests that running fix_typos() twice produces the same result.
"""

import pytest

from pytypopo import fix_typos

# All supported locales
ALL_LOCALES = ["en-us", "de-de", "cs", "sk", "rue"]

# Comprehensive test cases gathered from various modules
# These are inputs that should produce stable outputs when processed multiple times
IDEMPOTENCY_TEST_CASES = [
    # Ellipsis
    "...",
    "....",
    ".....",
    "Wait... what?",
    "And then...",
    # Dashes
    "word - word",
    "word -- word",
    "word --- word",
    "2020-2021",
    "pages 10-20",
    # Quotes
    '"Hello"',
    "'Hello'",
    '"Hello," she said.',
    "It's working",
    # Multiplication sign
    "5 x 4",
    "5 X 4",
    "12x3",
    "5 x 4 x 3",
    # Symbols
    "(c) 2020",
    "(C) 2020",
    "(r)",
    "(tm)",
    "(p) 2020",
    "§ 1",
    "§1",
    "№ 5",
    "№5",
    # Exponents
    "m2",
    "m3",
    "km2",
    "100m2",
    # Plus/minus
    "+-5",
    "+- 5",
    "+/- 5",
    # Number sign
    "#5",
    "# 5",
    # Spaces
    "Hello  world",
    "Hello   world",
    " Leading space",
    "Trailing space ",
    # Lines
    "First.\n\n\nSecond.",
    # Abbreviations
    "e.g.",
    "i.e.",
    "etc.",
    "F. X. Šalda",
    # Case
    "HELLO world",
    "HEllo",
    # Periods
    "test...",
    "test,,,",
    # Brackets
    "( word )",
    "[ word ]",
    "word(test)word",
    # Mixed content
    "Visit http://example.com for more info.",
    "Email: test@example.com",
    "File: document.pdf",
    # Markdown
    "```code```",
    "`inline code`",
    "- list item",
    "* list item",
    "> blockquote",
    # Edge cases
    "",
    "   ",
    "Single",
    ".",
    # Unicode
    "Příliš žluťoučký kůň",
    "Größe",
    "naïve café",
]


class TestIdempotency:
    """Test that fix_typos is idempotent - running it twice gives the same result."""

    @pytest.mark.parametrize("locale", ALL_LOCALES)
    @pytest.mark.parametrize("text", IDEMPOTENCY_TEST_CASES)
    def test_idempotency(self, text, locale):
        """Running fix_typos twice should produce the same result as running it once."""
        first_pass = fix_typos(text, locale)
        second_pass = fix_typos(first_pass, locale)
        assert second_pass == first_pass, f'Not idempotent for {locale}: "{text}" -> "{first_pass}" -> "{second_pass}"'

    @pytest.mark.parametrize("locale", ALL_LOCALES)
    @pytest.mark.parametrize("text", IDEMPOTENCY_TEST_CASES)
    def test_idempotency_keep_lines(self, text, locale):
        """Idempotency with remove_lines=False."""
        first_pass = fix_typos(text, locale, remove_lines=False)
        second_pass = fix_typos(first_pass, locale, remove_lines=False)
        assert second_pass == first_pass
