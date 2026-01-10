"""
Tests for pytypopo locale system.

Validates that all supported locales load correctly and have proper
quote character mappings matching the original typopo library.
"""

import pytest

from pytypopo.locale import Locale, get_locale  # noqa: I001

# All supported locales
ALL_LOCALES = ["en-us", "de-de", "cs", "sk", "rue"]

# Quote character constants using Unicode escapes to avoid syntax issues
# These are the typographically correct quote characters
LEFT_DOUBLE_QUOTE = "\u201c"  # " LEFT DOUBLE QUOTATION MARK
RIGHT_DOUBLE_QUOTE = "\u201d"  # " RIGHT DOUBLE QUOTATION MARK
LEFT_SINGLE_QUOTE = "\u2018"  # ' LEFT SINGLE QUOTATION MARK
RIGHT_SINGLE_QUOTE = "\u2019"  # ' RIGHT SINGLE QUOTATION MARK
DOUBLE_LOW_9_QUOTE = "\u201e"  # „ DOUBLE LOW-9 QUOTATION MARK
SINGLE_LOW_9_QUOTE = "\u201a"  # ‚ SINGLE LOW-9 QUOTATION MARK
LEFT_GUILLEMET = "\u00ab"  # « LEFT-POINTING DOUBLE ANGLE QUOTATION MARK
RIGHT_GUILLEMET = "\u00bb"  # » RIGHT-POINTING DOUBLE ANGLE QUOTATION MARK
LEFT_SINGLE_GUILLEMET = "\u2039"  # ‹ SINGLE LEFT-POINTING ANGLE QUOTATION MARK
RIGHT_SINGLE_GUILLEMET = "\u203a"  # › SINGLE RIGHT-POINTING ANGLE QUOTATION MARK

# Expected quote characters for each locale
# Matches original typopo: https://github.com/surfinzap/typopo/
EXPECTED_QUOTES = {
    "en-us": {
        "double_quote_open": LEFT_DOUBLE_QUOTE,
        "double_quote_close": RIGHT_DOUBLE_QUOTE,
        "single_quote_open": LEFT_SINGLE_QUOTE,
        "single_quote_close": RIGHT_SINGLE_QUOTE,
    },
    "de-de": {
        "double_quote_open": DOUBLE_LOW_9_QUOTE,
        "double_quote_close": RIGHT_DOUBLE_QUOTE,
        "single_quote_open": SINGLE_LOW_9_QUOTE,
        "single_quote_close": RIGHT_SINGLE_QUOTE,
    },
    "cs": {
        "double_quote_open": DOUBLE_LOW_9_QUOTE,
        "double_quote_close": RIGHT_DOUBLE_QUOTE,
        "single_quote_open": SINGLE_LOW_9_QUOTE,
        "single_quote_close": RIGHT_SINGLE_QUOTE,
    },
    "sk": {
        "double_quote_open": DOUBLE_LOW_9_QUOTE,
        "double_quote_close": RIGHT_DOUBLE_QUOTE,
        "single_quote_open": SINGLE_LOW_9_QUOTE,
        "single_quote_close": RIGHT_SINGLE_QUOTE,
    },
    "rue": {
        "double_quote_open": LEFT_GUILLEMET,
        "double_quote_close": RIGHT_GUILLEMET,
        "single_quote_open": LEFT_SINGLE_GUILLEMET,
        "single_quote_close": RIGHT_SINGLE_GUILLEMET,
    },
}


class TestLocaleClass:
    """Tests for the Locale class."""

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_locale_instantiation(self, locale_id):
        """Locale class can be instantiated with all supported locale IDs."""
        locale = Locale(locale_id)
        assert locale is not None
        assert locale.locale_id == locale_id

    def test_locale_default_to_en_us(self):
        """Unsupported locale ID defaults to en-us."""
        locale = Locale("unsupported-locale")
        assert locale.locale_id == "en-us"

    def test_locale_none_defaults_to_en_us(self):
        """None locale ID defaults to en-us."""
        locale = Locale(None)
        assert locale.locale_id == "en-us"

    def test_locale_empty_string_defaults_to_en_us(self):
        """Empty string locale ID defaults to en-us."""
        locale = Locale("")
        assert locale.locale_id == "en-us"


class TestGetLocaleFunction:
    """Tests for the get_locale() function."""

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_get_locale_returns_locale_instance(self, locale_id):
        """get_locale() returns a Locale instance for all supported locales."""
        locale = get_locale(locale_id)
        assert isinstance(locale, Locale)
        assert locale.locale_id == locale_id

    def test_get_locale_default_is_en_us(self):
        """get_locale() without arguments returns en-us locale."""
        locale = get_locale()
        assert locale.locale_id == "en-us"

    def test_get_locale_invalid_returns_en_us(self):
        """get_locale() with invalid locale ID returns en-us."""
        locale = get_locale("invalid")
        assert locale.locale_id == "en-us"

    def test_get_locale_case_insensitive(self):
        """get_locale() handles case variations."""
        # These should all resolve to the same locale
        locale_lower = get_locale("en-us")
        locale_upper = get_locale("EN-US")
        locale_mixed = get_locale("En-Us")

        assert locale_lower.locale_id == "en-us"
        assert locale_upper.locale_id == "en-us"
        assert locale_mixed.locale_id == "en-us"


class TestQuoteCharacters:
    """Tests for locale-specific quote character mappings."""

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_locale_has_double_quote_open(self, locale_id):
        """Each locale has a double_quote_open property."""
        locale = get_locale(locale_id)
        expected = EXPECTED_QUOTES[locale_id]["double_quote_open"]
        assert locale.double_quote_open == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_locale_has_double_quote_close(self, locale_id):
        """Each locale has a double_quote_close property."""
        locale = get_locale(locale_id)
        expected = EXPECTED_QUOTES[locale_id]["double_quote_close"]
        assert locale.double_quote_close == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_locale_has_single_quote_open(self, locale_id):
        """Each locale has a single_quote_open property."""
        locale = get_locale(locale_id)
        expected = EXPECTED_QUOTES[locale_id]["single_quote_open"]
        assert locale.single_quote_open == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_locale_has_single_quote_close(self, locale_id):
        """Each locale has a single_quote_close property."""
        locale = get_locale(locale_id)
        expected = EXPECTED_QUOTES[locale_id]["single_quote_close"]
        assert locale.single_quote_close == expected

    @pytest.mark.parametrize(
        ("locale_id", "quote_type", "expected"),
        [
            ("en-us", "double_quote_open", LEFT_DOUBLE_QUOTE),
            ("en-us", "double_quote_close", RIGHT_DOUBLE_QUOTE),
            ("en-us", "single_quote_open", LEFT_SINGLE_QUOTE),
            ("en-us", "single_quote_close", RIGHT_SINGLE_QUOTE),
            ("de-de", "double_quote_open", DOUBLE_LOW_9_QUOTE),
            ("de-de", "double_quote_close", RIGHT_DOUBLE_QUOTE),
            ("de-de", "single_quote_open", SINGLE_LOW_9_QUOTE),
            ("de-de", "single_quote_close", RIGHT_SINGLE_QUOTE),
            ("cs", "double_quote_open", DOUBLE_LOW_9_QUOTE),
            ("cs", "double_quote_close", RIGHT_DOUBLE_QUOTE),
            ("cs", "single_quote_open", SINGLE_LOW_9_QUOTE),
            ("cs", "single_quote_close", RIGHT_SINGLE_QUOTE),
            ("sk", "double_quote_open", DOUBLE_LOW_9_QUOTE),
            ("sk", "double_quote_close", RIGHT_DOUBLE_QUOTE),
            ("sk", "single_quote_open", SINGLE_LOW_9_QUOTE),
            ("sk", "single_quote_close", RIGHT_SINGLE_QUOTE),
            ("rue", "double_quote_open", LEFT_GUILLEMET),
            ("rue", "double_quote_close", RIGHT_GUILLEMET),
            ("rue", "single_quote_open", LEFT_SINGLE_GUILLEMET),
            ("rue", "single_quote_close", RIGHT_SINGLE_GUILLEMET),
        ],
    )
    def test_all_quote_mappings_explicit(self, locale_id, quote_type, expected):
        """Explicit test for each quote character mapping."""
        locale = get_locale(locale_id)
        actual = getattr(locale, quote_type)
        assert actual == expected, f"{locale_id}.{quote_type}: expected {expected!r}, got {actual!r}"


class TestEnglishUSLocale:
    """Specific tests for en-us locale (curly quotes)."""

    def test_en_us_uses_curly_double_quotes(self):
        """English uses curly double quotes not straight quotes."""
        locale = get_locale("en-us")
        # Should NOT be straight quotes
        assert locale.double_quote_open != '"'
        assert locale.double_quote_close != '"'
        # Should be curly quotes
        assert locale.double_quote_open == LEFT_DOUBLE_QUOTE
        assert locale.double_quote_close == RIGHT_DOUBLE_QUOTE

    def test_en_us_uses_curly_single_quotes(self):
        """English uses curly single quotes not straight quotes."""
        locale = get_locale("en-us")
        # Should NOT be straight quotes
        assert locale.single_quote_open != "'"
        assert locale.single_quote_close != "'"
        # Should be curly quotes
        assert locale.single_quote_open == LEFT_SINGLE_QUOTE
        assert locale.single_quote_close == RIGHT_SINGLE_QUOTE


class TestGermanLocale:
    """Specific tests for de-de locale (low-high quotes)."""

    def test_de_de_uses_low_opening_quotes(self):
        """German uses low-9 opening quotes (bottom quotes)."""
        locale = get_locale("de-de")
        # Opening quotes should be low (bottom) quotes
        assert locale.double_quote_open == DOUBLE_LOW_9_QUOTE
        assert locale.single_quote_open == SINGLE_LOW_9_QUOTE

    def test_de_de_uses_high_closing_quotes(self):
        """German uses high (top) closing quotes."""
        locale = get_locale("de-de")
        # Closing quotes should be high (same as English closing)
        assert locale.double_quote_close == RIGHT_DOUBLE_QUOTE
        assert locale.single_quote_close == RIGHT_SINGLE_QUOTE


class TestCzechSlovakLocales:
    """Tests for Czech and Slovak locales (same as German)."""

    @pytest.mark.parametrize("locale_id", ["cs", "sk"])
    def test_cs_sk_match_german_quotes(self, locale_id):
        """Czech and Slovak use the same quote style as German."""
        locale = get_locale(locale_id)
        de_locale = get_locale("de-de")

        assert locale.double_quote_open == de_locale.double_quote_open
        assert locale.double_quote_close == de_locale.double_quote_close
        assert locale.single_quote_open == de_locale.single_quote_open
        assert locale.single_quote_close == de_locale.single_quote_close


class TestRusynLocale:
    """Specific tests for rue locale (guillemets/angle quotes)."""

    def test_rue_uses_guillemets_for_double_quotes(self):
        """Rusyn uses guillemets (angle brackets) for double quotes."""
        locale = get_locale("rue")
        assert locale.double_quote_open == LEFT_GUILLEMET
        assert locale.double_quote_close == RIGHT_GUILLEMET

    def test_rue_uses_single_guillemets(self):
        """Rusyn uses single guillemets for single quotes."""
        locale = get_locale("rue")
        assert locale.single_quote_open == LEFT_SINGLE_GUILLEMET
        assert locale.single_quote_close == RIGHT_SINGLE_GUILLEMET


class TestLocaleProperties:
    """Tests for additional locale properties."""

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_locale_has_terminal_quotes(self, locale_id):
        """Each locale has terminal_quotes property combining closing quotes."""
        locale = get_locale(locale_id)
        # terminal_quotes should contain the closing quote characters
        assert hasattr(locale, "terminal_quotes")
        assert locale.single_quote_close in locale.terminal_quotes
        assert locale.double_quote_close in locale.terminal_quotes

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_locale_has_ordinal_indicator(self, locale_id):
        """Each locale has an ordinal_indicator property."""
        locale = get_locale(locale_id)
        assert hasattr(locale, "ordinal_indicator")
        # en-us should have st|nd|rd|th pattern
        if locale_id == "en-us":
            assert "st" in locale.ordinal_indicator
            assert "nd" in locale.ordinal_indicator
            assert "rd" in locale.ordinal_indicator
            assert "th" in locale.ordinal_indicator
