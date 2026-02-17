"""
Integration tests for pytypopo.

Port of tests/integration/typopo.test.js from typopo.
Tests the main fix_typos() function with full processing pipeline.
"""

import pytest

from pytypopo import fix_typos
from pytypopo.const import ELLIPSIS, NBSP

# All supported locales
ALL_LOCALES = ["en-us", "de-de", "cs", "sk", "rue"]


# Test data: internal variables should be preserved (not treated as typography errors)
INTERNAL_VARIABLES_TESTS = {
    "{{test-variable}}": "{{test-variable}}",
    "{{test-variable}} at the beginning of the sentence.": "{{test-variable}} at the beginning of the sentence.",
    "And {{test-variable}} in the middle of the sentence.": "And {{test-variable}} in the middle of the sentence.",
    "And at the end {{test-variable}}.": "And at the end {{test-variable}}.",
    "Multiple {{var1}} and {{var2}} variables.": "Multiple {{var1}} and {{var2}} variables.",
}


# Module combinations: tests that ellipsis and bracket spacing work together
MODULE_COMBINATIONS_TESTS = {
    # Ellipsis in brackets
    "quote [...]with parts left out": f"quote [{ELLIPSIS}] with parts left out",
    "quote[...] with parts left out": f"quote [{ELLIPSIS}] with parts left out",
    "quote [ ...] with parts left out": f"quote [{ELLIPSIS}] with parts left out",
    "quote [.... ] with parts left out": f"quote [{ELLIPSIS}] with parts left out",
    "quote [ ..... ] with parts left out": f"quote [{ELLIPSIS}] with parts left out",
    # Ellipsis character variant
    f"quote[{ELLIPSIS}] with parts left out": f"quote [{ELLIPSIS}] with parts left out",
}


# False positives: dash patterns that should remain unchanged
# Note: Single-letter prepositions like "a" get nbsp after them (locale-dependent behavior)
FALSE_POSITIVES_DASH_TESTS = {
    # German compound words
    "Ein- und Ausgang": "Ein- und Ausgang",
    "ein- und ausschalten": "ein- und ausschalten",
    "S- oder U-Bahn": "S- oder U-Bahn",
    # Czech compound words - 'a' gets nbsp after it (single-letter preposition)
    "dvou- a trzipokojove byty": f"dvou- a{NBSP}trzipokojove byty",
    # English compound words
    "R- and X-rated films": "R- and X-rated films",
    # German suspended hyphenation
    "Softwareentwicklung, -verkauf und -wartung": "Softwareentwicklung, -verkauf und -wartung",
}


# Tests for remove_lines configuration
REMOVE_LINES_TESTS = {
    "First paragraph.\n\n\nSecond paragraph.": "First paragraph.\nSecond paragraph.",
    "First paragraph.\n\n\n\nSecond paragraph.": "First paragraph.\nSecond paragraph.",
}


# Tests for keeping lines (remove_lines=False)
KEEP_LINES_TESTS = {
    "First paragraph.\n\n\nSecond paragraph.": "First paragraph.\n\n\nSecond paragraph.",
}


# Tests for basic typography fixes
BASIC_TYPOGRAPHY_TESTS = {
    # Multiple spaces
    "Hello   world": "Hello world",
    # Trailing spaces
    "Hello world   ": "Hello world",
    # Leading spaces
    "   Hello world": "Hello world",
}


# Exception preservation tests (URLs, emails)
EXCEPTION_TESTS = {
    # URLs should not be modified
    "Visit https://example.com for info": "Visit https://example.com for info",
    "Check http://example.com/path?query=1": "Check http://example.com/path?query=1",
    # Emails should not be modified
    "Contact user@example.com for help": "Contact user@example.com for help",
    # Filenames should not be modified
    "Open file.txt to view": "Open file.txt to view",
}


# Apostrophe tests - straight quotes get converted to typographic apostrophes
# The apostrophe ' (U+2019 RIGHT SINGLE QUOTATION MARK) is used in English contractions
APOSTROPHE = "\u2019"  # Typographic apostrophe
APOSTROPHE_TESTS = {
    # Straight apostrophe becomes curly, nbsp after single-letter word
    "Because of this, it's common": f"Because of this, it{APOSTROPHE}s{NBSP}common",
    "don't do that": f"don{APOSTROPHE}t{NBSP}do that",
    "I've been there": f"I{APOSTROPHE}ve been there",
}


class TestInternalVariables:
    """Test that internal variable placeholders are preserved."""

    @pytest.mark.parametrize(("input_text", "expected"), INTERNAL_VARIABLES_TESTS.items())
    @pytest.mark.parametrize("locale", ALL_LOCALES)
    def test_preserves_internal_variables(self, input_text, expected, locale):
        result = fix_typos(input_text, locale)
        assert result == expected


class TestModuleCombinations:
    """Test that multiple modules work together correctly."""

    @pytest.mark.parametrize(("input_text", "expected"), MODULE_COMBINATIONS_TESTS.items())
    @pytest.mark.parametrize("locale", ALL_LOCALES)
    def test_ellipsis_and_brackets(self, input_text, expected, locale):
        result = fix_typos(input_text, locale)
        assert result == expected


class TestFalsePositives:
    """Test that valid patterns are not incorrectly modified."""

    @pytest.mark.parametrize(("input_text", "expected"), FALSE_POSITIVES_DASH_TESTS.items())
    @pytest.mark.parametrize("locale", ALL_LOCALES)
    def test_compound_words_with_dashes(self, input_text, expected, locale):
        result = fix_typos(input_text, locale)
        assert result == expected


class TestConfiguration:
    """Test configuration options."""

    @pytest.mark.parametrize(("input_text", "expected"), REMOVE_LINES_TESTS.items())
    @pytest.mark.parametrize("locale", ALL_LOCALES)
    def test_remove_lines_enabled(self, input_text, expected, locale):
        result = fix_typos(input_text, locale, remove_lines=True)
        assert result == expected

    @pytest.mark.parametrize(("input_text", "expected"), KEEP_LINES_TESTS.items())
    @pytest.mark.parametrize("locale", ALL_LOCALES)
    def test_remove_lines_disabled(self, input_text, expected, locale):
        result = fix_typos(input_text, locale, remove_lines=False)
        assert result == expected


class TestBasicTypography:
    """Test basic typography fixes."""

    @pytest.mark.parametrize(("input_text", "expected"), BASIC_TYPOGRAPHY_TESTS.items())
    @pytest.mark.parametrize("locale", ALL_LOCALES)
    def test_basic_fixes(self, input_text, expected, locale):
        result = fix_typos(input_text, locale)
        assert result == expected


class TestExceptions:
    """Test that URLs, emails, and filenames are protected."""

    @pytest.mark.parametrize(("input_text", "expected"), EXCEPTION_TESTS.items())
    @pytest.mark.parametrize("locale", ALL_LOCALES)
    def test_exceptions_preserved(self, input_text, expected, locale):
        result = fix_typos(input_text, locale)
        assert result == expected


class TestApostrophes:
    """Test that contractions with apostrophes are handled correctly."""

    @pytest.mark.parametrize(("input_text", "expected"), APOSTROPHE_TESTS.items())
    def test_contractions_preserved(self, input_text, expected):
        # Apostrophe handling is locale-specific, test with en-us
        result = fix_typos(input_text, "en-us")
        assert result == expected


class TestApiDefaults:
    """Test API default values."""

    def test_default_locale(self):
        """Default locale should be en-us."""
        result = fix_typos("Hello   world")
        assert result == "Hello world"

    def test_default_remove_lines(self):
        """Default should remove empty lines."""
        result = fix_typos("First.\n\n\nSecond.")
        assert result == "First.\nSecond."

    def test_backticks_treated_as_regular_chars(self):
        """Backticks are treated as regular characters (no markdown protection)."""
        # Backticks are no longer protected - they get processed as regular text
        result = fix_typos('`code with "quotes"`')
        # The quotes inside backticks will be processed now
        assert result == "\u2019code with \u201cquotes\u201d\u2019"


class TestEmptyInput:
    """Test handling of empty and edge case inputs."""

    @pytest.mark.parametrize("locale", ALL_LOCALES)
    def test_empty_string(self, locale):
        assert fix_typos("", locale) == ""

    @pytest.mark.parametrize("locale", ALL_LOCALES)
    def test_whitespace_only(self, locale):
        assert fix_typos("   ", locale) == ""

    @pytest.mark.parametrize("locale", ALL_LOCALES)
    def test_newlines_only(self, locale):
        assert fix_typos("\n\n\n", locale) == ""


class TestLocaleNormalization:
    """Test that locale identifiers are normalized correctly."""

    def test_uppercase_locale(self):
        """Uppercase locale should work."""
        result = fix_typos("Hello   world", "EN-US")
        assert result == "Hello world"

    def test_mixed_case_locale(self):
        """Mixed case locale should work."""
        result = fix_typos("Hello   world", "En-Us")
        assert result == "Hello world"

    def test_invalid_locale_defaults_to_enus(self):
        """Invalid locale should default to en-us."""
        result = fix_typos("Hello   world", "invalid")
        assert result == "Hello world"

    def test_none_locale_defaults_to_enus(self):
        """None locale should default to en-us."""
        result = fix_typos("Hello   world", None)
        assert result == "Hello world"
