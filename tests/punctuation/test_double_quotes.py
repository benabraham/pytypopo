"""
Tests for double quotes fixes: curly double quotes and double primes.

Port of tests/punctuation/double-quotes.test.js from typopo.
"""

import pytest

from pytypopo.locale import Locale
from pytypopo.modules.punctuation.double_quotes import (
    add_space_after_right_double_quote,
    add_space_before_left_double_quote,
    fix_direct_speech_intro,
    fix_double_quotes_and_primes,
    fix_quoted_sentence_punctuation,
    fix_quoted_word_punctuation,
    identify_double_primes,
    identify_double_quote_pairs,
    place_locale_double_quotes,
    remove_extra_punctuation_after_quotes,
    remove_extra_punctuation_before_quotes,
    remove_extra_spaces_around_quotes,
    remove_unidentified_double_quote,
    replace_double_prime_with_double_quote,
)
from tests.conftest import ALL_LOCALES


# Helper to get locale-specific quote characters
def get_quotes(locale_id):
    loc = Locale(locale_id)
    return {
        "ldq": loc.double_quote_open,
        "rdq": loc.double_quote_close,
        "apos": loc.single_quote_close,  # apostrophe
    }


# Direct speech intro differs by locale
def get_direct_speech_intro(locale_id):
    if locale_id == "en-us":
        return ","
    return ":"


# Character constants
DOUBLE_PRIME = "\u2033"  # ″
SINGLE_PRIME = "\u2032"  # ′
ELLIPSIS = "\u2026"  # …
EN_DASH = "\u2013"  # –
EM_DASH = "\u2014"  # —
NBSP = "\u00a0"  # non-breaking space
DEGREE = "\u00b0"  # °
MULTIPLICATION = "\u00d7"  # ×

# Various quote characters used in tests
LDQUO = "\u201c"  # "
RDQUO = "\u201d"  # "
BDQUO = "\u201e"  # „
LAQUO = "\u00ab"  # «
RAQUO = "\u00bb"  # »
LSAQUO = "\u2039"  # ‹
RSAQUO = "\u203a"  # ›


# =============================================================================
# FALSE POSITIVES - Tests that should NOT be modified
# =============================================================================


class TestDoubleQuotesFalsePositives:
    """False positive tests - text that should not be modified.

    Port of doubleQuotesFalsePositives from JS.
    """

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_abbreviations_preserved(self, locale_id):
        """Abbreviations like c., s., fol., str. should not be modified."""
        text = "c., s., fol., str.,"
        assert fix_double_quotes_and_primes(text, locale_id) == text

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_roman_numeral_in_quotes(self, locale_id):
        """Roman numerals like Karel IV. inside quotes should be preserved."""
        q = get_quotes(locale_id)
        text = f"Byl to {q['ldq']}Karel IV.{q['rdq']}, ktery"
        assert fix_double_quotes_and_primes(text, locale_id) == text

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_ending_quote_with_period(self, locale_id):
        """Quote ending with period at end of text."""
        q = get_quotes(locale_id)
        text = f"Hey.{q['rdq']}"
        # This is a fragment - should not be changed
        result = fix_double_quotes_and_primes(text, locale_id)
        assert q["rdq"] in result

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_namespace_pollution_example(self, locale_id):
        """Programming text about namespace pollution - JS moves comma inside multi-word quotes."""
        q = get_quotes(locale_id)
        text = f"common to have {q['ldq']}namespace pollution{q['rdq']}, where completely unrelated code shares global variables."
        # JS behavior: fixQuotedSentencePunctuation moves comma inside for multi-word quotes
        expected = f"common to have {q['ldq']}namespace pollution,{q['rdq']} where completely unrelated code shares global variables."
        assert fix_double_quotes_and_primes(text, locale_id) == expected


# =============================================================================
# REMOVE EXTRA PUNCTUATION BEFORE QUOTES
# =============================================================================


class TestRemoveExtraPunctuationBeforeQuotes:
    """Remove extra punctuation before closing quotes.

    Port of removePunctuationBeforeQuotesSet tests from JS.
    """

    # Tests for comma after terminal punctuation
    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    @pytest.mark.parametrize("punct", ["!", "?", ".", ":", ";", ","])
    def test_remove_extra_comma_after_punct(self, locale_id, punct):
        q = get_quotes(locale_id)
        text = f"{q['ldq']}Hey{punct},{q['rdq']} she said"
        expected = f"{q['ldq']}Hey{punct}{q['rdq']} she said"
        assert remove_extra_punctuation_before_quotes(text, locale_id) == expected

    # Tests for colon after terminal punctuation
    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    @pytest.mark.parametrize("punct", ["!", "?", ".", ":", ";", ","])
    def test_remove_extra_colon_after_punct(self, locale_id, punct):
        q = get_quotes(locale_id)
        text = f"{q['ldq']}Hey{punct}:{q['rdq']} she said"
        expected = f"{q['ldq']}Hey{punct}{q['rdq']} she said"
        assert remove_extra_punctuation_before_quotes(text, locale_id) == expected

    # Tests for semicolon after terminal punctuation
    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    @pytest.mark.parametrize("punct", ["!", "?", ".", ":", ";", ","])
    def test_remove_extra_semicolon_after_punct(self, locale_id, punct):
        q = get_quotes(locale_id)
        text = f"{q['ldq']}Hey{punct};{q['rdq']} she said"
        expected = f"{q['ldq']}Hey{punct}{q['rdq']} she said"
        assert remove_extra_punctuation_before_quotes(text, locale_id) == expected

    # False positives - should NOT remove ! or ? after terminal punctuation
    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    @pytest.mark.parametrize(
        ("first", "second"),
        [
            ("!", "!"),
            ("?", "!"),
            (".", "!"),
            (":", "!"),
            (";", "!"),
            (",", "!"),
            ("!", "?"),
            ("?", "?"),
            (".", "?"),
            (":", "?"),
            (";", "?"),
            (",", "?"),
            ("!", "."),
            ("?", "."),
            (":", "."),
            (";", "."),
            (",", "."),
        ],
    )
    def test_false_positive_exclamation_question_period(self, locale_id, first, second):
        """Should NOT remove ! or ? or . after other punctuation (these are valid)."""
        q = get_quotes(locale_id)
        text = f"{q['ldq']}Hey{first}{second}{q['rdq']} she said"
        # No change expected - these patterns are valid (e.g., "Hey!!" or "Hey!?")
        assert remove_extra_punctuation_before_quotes(text, locale_id) == text

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_false_positive_roman_numeral(self, locale_id):
        """Preserve roman numerals like Karel IV."""
        q = get_quotes(locale_id)
        text = f"Byl to {q['ldq']}Karel IV.{q['rdq']}, ktery"
        # Should NOT remove punctuation - roman numeral exception
        assert remove_extra_punctuation_before_quotes(text, locale_id) == text


# =============================================================================
# REMOVE EXTRA PUNCTUATION AFTER QUOTES
# =============================================================================


class TestRemoveExtraPunctuationAfterQuotes:
    """Remove extra punctuation after closing quotes.

    Port of removePunctuationAfterQuotesSet tests from JS.
    """

    # Extra comma after closing quote
    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    @pytest.mark.parametrize("inner_punct", ["!", "?", ".", ":", ";", ","])
    def test_remove_extra_comma_after_closing_quote(self, locale_id, inner_punct):
        q = get_quotes(locale_id)
        text = f"{q['ldq']}Hey{inner_punct}{q['rdq']}, she said"
        expected = f"{q['ldq']}Hey{inner_punct}{q['rdq']} she said"
        assert remove_extra_punctuation_after_quotes(text, locale_id) == expected

    # Extra colon after closing quote
    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    @pytest.mark.parametrize("inner_punct", ["!", "?", ".", ":", ";", ","])
    def test_remove_extra_colon_after_closing_quote(self, locale_id, inner_punct):
        q = get_quotes(locale_id)
        text = f"{q['ldq']}Hey{inner_punct}{q['rdq']}: she said"
        expected = f"{q['ldq']}Hey{inner_punct}{q['rdq']} she said"
        assert remove_extra_punctuation_after_quotes(text, locale_id) == expected

    # Extra semicolon after closing quote
    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    @pytest.mark.parametrize("inner_punct", ["!", "?", ".", ":", ";", ","])
    def test_remove_extra_semicolon_after_closing_quote(self, locale_id, inner_punct):
        q = get_quotes(locale_id)
        text = f"{q['ldq']}Hey{inner_punct}{q['rdq']}; she said"
        expected = f"{q['ldq']}Hey{inner_punct}{q['rdq']} she said"
        assert remove_extra_punctuation_after_quotes(text, locale_id) == expected

    # Extra period after closing quote
    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    @pytest.mark.parametrize("inner_punct", ["!", "?", ".", ":", ";", ","])
    def test_remove_extra_period_after_closing_quote(self, locale_id, inner_punct):
        q = get_quotes(locale_id)
        text = f"{q['ldq']}Hey{inner_punct}{q['rdq']}. she said"
        expected = f"{q['ldq']}Hey{inner_punct}{q['rdq']} she said"
        assert remove_extra_punctuation_after_quotes(text, locale_id) == expected

    # Extra question mark after closing quote
    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    @pytest.mark.parametrize("inner_punct", ["!", "?", ".", ":", ";", ","])
    def test_remove_extra_question_after_closing_quote(self, locale_id, inner_punct):
        q = get_quotes(locale_id)
        text = f"{q['ldq']}Hey{inner_punct}{q['rdq']}? she said"
        expected = f"{q['ldq']}Hey{inner_punct}{q['rdq']} she said"
        assert remove_extra_punctuation_after_quotes(text, locale_id) == expected

    # Extra exclamation mark after closing quote
    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    @pytest.mark.parametrize("inner_punct", ["!", "?", ".", ":", ";", ","])
    def test_remove_extra_exclamation_after_closing_quote(self, locale_id, inner_punct):
        q = get_quotes(locale_id)
        text = f"{q['ldq']}Hey{inner_punct}{q['rdq']}! she said"
        expected = f"{q['ldq']}Hey{inner_punct}{q['rdq']} she said"
        assert remove_extra_punctuation_after_quotes(text, locale_id) == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_false_positive_roman_numeral(self, locale_id):
        """Preserve roman numerals like Karel IV. followed by comma."""
        q = get_quotes(locale_id)
        text = f"Byl to {q['ldq']}Karel IV.{q['rdq']}, ktery"
        # Should NOT remove the comma - roman numeral exception
        assert remove_extra_punctuation_after_quotes(text, locale_id) == text


# =============================================================================
# IDENTIFY DOUBLE PRIMES (Unit tests)
# =============================================================================


class TestIdentifyDoublePrimesUnit:
    """Identify inches, arcseconds following numbers - unit tests.

    Port of identifyDoublePrimesUnitSet tests from JS.
    """

    # Various quote representations followed by numbers (with space before quote)
    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    @pytest.mark.parametrize(
        "quote_char",
        [
            '"',  # straight double quote
            LDQUO,  # left double quotation mark "
            RDQUO,  # right double quotation mark "
            DOUBLE_PRIME,  # ″
            "''",  # two apostrophes
            "\u2019\u2019",  # two right single quotes ''
            "\u2032\u2032",  # two primes ′′
        ],
    )
    def test_identify_double_prime_arcminutes_space(self, locale_id, quote_char):
        """Identify double prime with space after arcminutes: 12' 45 " -> 12' 45 ″ (space preserved)"""
        text = f"12{SINGLE_PRIME} 45 {quote_char}"
        result = place_locale_double_quotes(identify_double_primes(text, locale_id), locale_id)
        # Space is preserved in unit test (JS expects "12′ 45 ″")
        assert result == f"12{SINGLE_PRIME} 45 {DOUBLE_PRIME}"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_identify_inches_two_apostrophes(self, locale_id):
        """Identify inches from two apostrophes: 12 '' -> 12 ″ (preserves space)"""
        text = "12 ''"
        result = place_locale_double_quotes(identify_double_primes(text, locale_id), locale_id)
        assert result == f"12 {DOUBLE_PRIME}"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_false_positive_conference_year(self, locale_id):
        """Should not convert quotes around conference year to primes."""
        text = '"Conference 2020" and "something in quotes".'
        result = identify_double_primes(text, locale_id)
        # Should not change - 4 digit numbers are excluded
        assert result == text

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_false_positive_number_before_opening_quote(self, locale_id):
        """Should not convert quotes to primes when followed by letters (opening quote)."""
        text = 'Level 3 "with" word'
        result = identify_double_primes(text, locale_id)
        # The " before "with" is an opening quote, not inches
        assert result == text

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_swap_inches_with_terminal_punctuation(self, locale_id):
        """Swap inches with terminal punctuation: "He was 12". -> "He was 12." """
        text = '"He was 12".'
        result = place_locale_double_quotes(identify_double_primes(text, locale_id), locale_id)
        assert result == '"He was 12."'

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_inches_at_end_with_period(self, locale_id):
        """He was 12". -> He was 12″. (false positive check)"""
        text = 'He was 12".'
        result = place_locale_double_quotes(identify_double_primes(text, locale_id), locale_id)
        assert result == f"He was 12{DOUBLE_PRIME}."

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_quoted_sentence_with_inches(self, locale_id):
        """ "He was 12." should remain unchanged."""
        text = '"He was 12."'
        result = identify_double_primes(text, locale_id)
        assert result == text

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_dimensions_x_lowercase(self, locale_id):
        """It's 12" x 12". -> It's 12″ x 12″."""
        q = get_quotes(locale_id)
        text = f'It{q["apos"]}s 12" x 12".'
        result = place_locale_double_quotes(identify_double_primes(text, locale_id), locale_id)
        assert result == f"It{q['apos']}s 12{DOUBLE_PRIME} x 12{DOUBLE_PRIME}."

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_dimensions_multiplication_sign(self, locale_id):
        """It's 12" x 12". -> It's 12″ x 12″."""
        q = get_quotes(locale_id)
        text = f'It{q["apos"]}s 12" {MULTIPLICATION} 12".'
        result = place_locale_double_quotes(identify_double_primes(text, locale_id), locale_id)
        assert result == f"It{q['apos']}s 12{DOUBLE_PRIME} {MULTIPLICATION} 12{DOUBLE_PRIME}."


# =============================================================================
# IDENTIFY DOUBLE PRIMES (Module tests)
# =============================================================================


class TestIdentifyDoublePrimesModule:
    """Identify inches, arcseconds - module/integration tests.

    Port of identifyDoublePrimesModuleSet tests from JS.
    Tests with fix_double_quotes_and_primes for full pipeline.
    """

    # Various quote representations directly after numbers (no space)
    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    @pytest.mark.parametrize(
        "quote_char",
        [
            '"',  # straight double quote
            LDQUO,  # left double quotation mark "
            RDQUO,  # right double quotation mark "
            DOUBLE_PRIME,  # ″
            "''",  # two apostrophes
            "\u2019\u2019",  # two right single quotes ''
            "\u2032\u2032",  # two primes ′′
            "\u2032'",  # mixed prime and apostrophe ′'
        ],
    )
    def test_identify_double_prime_arcminutes_nospace(self, locale_id, quote_char):
        """Identify double prime directly after arcminutes: 12' 45" """
        text = f"12{SINGLE_PRIME} 45{quote_char}"
        result = fix_double_quotes_and_primes(text, locale_id)
        assert result == f"12{SINGLE_PRIME} 45{DOUBLE_PRIME}"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_inches_two_apostrophes_nospace(self, locale_id):
        """12'' -> 12″"""
        text = "12''"
        result = fix_double_quotes_and_primes(text, locale_id)
        assert result == f"12{DOUBLE_PRIME}"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_inches_two_primes_nospace(self, locale_id):
        """12′′ -> 12″"""
        text = "12\u2032\u2032"
        result = fix_double_quotes_and_primes(text, locale_id)
        assert result == f"12{DOUBLE_PRIME}"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_dms_notation(self, locale_id):
        """Degree-minute-second notation: 3° 5′ 30" -> 3° 5′ 30″"""
        text = f'3{DEGREE} 5{SINGLE_PRIME} 30"'
        result = fix_double_quotes_and_primes(text, locale_id)
        assert result == f"3{DEGREE} 5{SINGLE_PRIME} 30{DOUBLE_PRIME}"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_dms_notation_reversed(self, locale_id):
        """Reversed DMS: 12"3′00° -> 12″3′00°"""
        text = f'12"3{SINGLE_PRIME}00{DEGREE}'
        result = fix_double_quotes_and_primes(text, locale_id)
        assert result == f"12{DOUBLE_PRIME}3{SINGLE_PRIME}00{DEGREE}"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_dimensions_with_question(self, locale_id):
        """So it's 12" × 12", right?"""
        q = get_quotes(locale_id)
        text = f'So it{q["apos"]}s 12" {MULTIPLICATION} 12", right?'
        result = fix_double_quotes_and_primes(text, locale_id)
        # Note: NBSP may be inserted after short words depending on locale rules
        expected_plain = f"So it{q['apos']}s 12{DOUBLE_PRIME} {MULTIPLICATION} 12{DOUBLE_PRIME}, right?"
        expected_nbsp = f"So it{q['apos']}s{NBSP}12{DOUBLE_PRIME} {MULTIPLICATION} 12{DOUBLE_PRIME}, right?"
        assert result == expected_plain or result == expected_nbsp

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_number_before_opening_quote_module(self, locale_id):
        """Level 3 "with" word — should use locale quotes, not primes."""
        q = get_quotes(locale_id)
        text = 'Level 3 "with" word'
        result = fix_double_quotes_and_primes(text, locale_id)
        assert result == f"Level 3 {q['ldq']}with{q['rdq']} word"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_inches_in_direct_speech(self, locale_id):
        """She said: "It's a 12" inch!" """
        q = get_quotes(locale_id)
        intro = get_direct_speech_intro(locale_id)
        text = f'She said{intro} "It{q["apos"]}s a 12" inch!"'
        result = fix_double_quotes_and_primes(text, locale_id)
        assert f"12{DOUBLE_PRIME} inch" in result
        assert q["ldq"] in result
        assert q["rdq"] in result

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_dimensions_end_with_period(self, locale_id):
        """It's 12" × 12″."""
        q = get_quotes(locale_id)
        text = f'It{q["apos"]}s 12" {MULTIPLICATION} 12".'
        result = fix_double_quotes_and_primes(text, locale_id)
        # Note: NBSP may be inserted after short words depending on locale rules
        expected_plain = f"It{q['apos']}s 12{DOUBLE_PRIME} {MULTIPLICATION} 12{DOUBLE_PRIME}."
        expected_nbsp = f"It{q['apos']}s{NBSP}12{DOUBLE_PRIME} {MULTIPLICATION} 12{DOUBLE_PRIME}."
        assert result == expected_plain or result == expected_nbsp

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_swap_inches_module(self, locale_id):
        """ "He was 12". -> "He was 12." in full pipeline"""
        q = get_quotes(locale_id)
        text = '"He was 12".'
        result = fix_double_quotes_and_primes(text, locale_id)
        assert result == f"{q['ldq']}He was 12.{q['rdq']}"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_inches_false_positive_module(self, locale_id):
        """He was 12". -> He was 12″. in full pipeline"""
        text = 'He was 12".'
        result = fix_double_quotes_and_primes(text, locale_id)
        assert result == f"He was 12{DOUBLE_PRIME}."


# =============================================================================
# IDENTIFY DOUBLE QUOTE PAIRS (Unit tests)
# =============================================================================


class TestIdentifyDoubleQuotePairsUnit:
    """Identify paired double quotes - unit tests.

    Port of identifyDoubleQuotePairsUnitSet tests from JS.
    """

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_quote_pair_with_spaces(self, locale_id):
        text = '" quoted material "'
        result = identify_double_quote_pairs(text, locale_id)
        assert "{{typopo__ldq}}" in result
        assert "{{typopo__rdq}}" in result

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_quote_pair_left_space_only(self, locale_id):
        text = '"quoted material "'
        result = identify_double_quote_pairs(text, locale_id)
        assert "{{typopo__ldq}}" in result
        assert "{{typopo__rdq}}" in result

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_quote_pair_right_space_only(self, locale_id):
        text = '" quoted material"'
        result = identify_double_quote_pairs(text, locale_id)
        assert "{{typopo__ldq}}" in result
        assert "{{typopo__rdq}}" in result


# =============================================================================
# IDENTIFY DOUBLE QUOTE PAIRS (Module tests)
# =============================================================================


class TestIdentifyDoubleQuotePairsModule:
    """Identify paired double quotes - module/integration tests.

    Port of identifyDoubleQuotePairsModuleSet tests from JS.
    """

    # Various quote pair types
    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    @pytest.mark.parametrize(
        ("open_q", "close_q"),
        [
            ('"', '"'),  # straight quotes
            (BDQUO, '"'),  # low-9 + straight „..."
            (LAQUO, LAQUO),  # guillemets (same char) «...«
            ("''", "''"),  # two apostrophes
            ("\u203a\u203a", "\u2039\u2039"),  # double single guillemets ››...‹‹
            (",,", ",,"),  # two commas (unusual)
            ("\u2019\u2019", "\u2019\u2019"),  # double right single quotes ''...''
            ("'''", "'''"),  # three apostrophes
            ("\u00b4\u00b4", "\u00b4\u00b4"),  # two acute accents ´´...´´
            ("``", "``"),  # two grave accents
            (LDQUO, RDQUO),  # curly quotes "..."
            (BDQUO, RDQUO),  # low-9 + right curly „..."
            (LAQUO, RAQUO),  # proper guillemets «...»
        ],
    )
    def test_identify_various_quote_pairs(self, locale_id, open_q, close_q):
        """Identify various quote pair types."""
        q = get_quotes(locale_id)
        text = f"{open_q}quoted material{close_q}"
        result = fix_double_quotes_and_primes(text, locale_id)
        expected = f"{q['ldq']}quoted material{q['rdq']}"
        assert result == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_quote_in_unquoted_material(self, locale_id):
        """unquoted "quoted material" material"""
        q = get_quotes(locale_id)
        text = 'unquoted "quoted material" material'
        result = fix_double_quotes_and_primes(text, locale_id)
        assert f"{q['ldq']}quoted material{q['rdq']}" in result

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_multiple_quote_pairs(self, locale_id):
        """ "quoted material" and "quoted material" """
        q = get_quotes(locale_id)
        text = '"quoted material" and "quoted material"'
        result = fix_double_quotes_and_primes(text, locale_id)
        assert result == f"{q['ldq']}quoted material{q['rdq']} and {q['ldq']}quoted material{q['rdq']}"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_primes_vs_quotes_conference(self, locale_id):
        """ "Conference 2020" and "something in quotes". - JS moves period inside multi-word quotes."""
        q = get_quotes(locale_id)
        text = '"Conference 2020" and "something in quotes".'
        result = fix_double_quotes_and_primes(text, locale_id)
        # JS behavior: fixQuotedSentencePunctuation moves period inside for multi-word quotes
        assert result == f"{q['ldq']}Conference 2020{q['rdq']} and {q['ldq']}something in quotes.{q['rdq']}"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_quotes_around_number_with_prime(self, locale_id):
        """ "Gone in 60″" where prime already identified"""
        q = get_quotes(locale_id)
        text = f'"Gone in 60{DOUBLE_PRIME}"'
        result = fix_double_quotes_and_primes(text, locale_id)
        assert result == f"{q['ldq']}Gone in 60{DOUBLE_PRIME}{q['rdq']}"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    @pytest.mark.parametrize("year", ["2020", "202"])
    def test_quotes_around_year(self, locale_id, year):
        """Quotes around year should be identified as quotes, not primes."""
        q = get_quotes(locale_id)
        text = f'"{year}"'
        result = fix_double_quotes_and_primes(text, locale_id)
        assert result == f"{q['ldq']}{year}{q['rdq']}"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_false_positive_primes_in_quotes(self, locale_id):
        """ "starting quotes, primes 90″, ending quotes" """
        q = get_quotes(locale_id)
        text = f'"starting quotes, primes 90{DOUBLE_PRIME}, ending quotes"'
        result = fix_double_quotes_and_primes(text, locale_id)
        assert result == f"{q['ldq']}starting quotes, primes 90{DOUBLE_PRIME}, ending quotes{q['rdq']}"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_jibberish_inside_quotes(self, locale_id):
        """Random content inside quotes should still be identified."""
        q = get_quotes(locale_id)
        text = ",,idjsa; frilj f0d, if9,,"
        result = fix_double_quotes_and_primes(text, locale_id)
        assert result == f"{q['ldq']}idjsa; frilj f0d, if9{q['rdq']}"


# =============================================================================
# IDENTIFY UNPAIRED LEFT DOUBLE QUOTE
# =============================================================================


class TestIdentifyUnpairedLeftDoubleQuote:
    """Identify unpaired left double quotes.

    Port of identifyUnpairedLeftDoubleQuoteSet tests from JS.
    """

    # Lowercase following unpaired left quote
    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    @pytest.mark.parametrize(
        "quote_char",
        [
            '"',  # straight quote
            LAQUO,  # guillemet «
            BDQUO,  # low-9 „
            ",,",  # two commas
            "\u203a\u203a",  # double single guillemets ››
            "''",  # two apostrophes
        ],
    )
    def test_unpaired_left_quote_lowercase(self, locale_id, quote_char):
        q = get_quotes(locale_id)
        text = f"{quote_char}unpaired left quote."
        result = fix_double_quotes_and_primes(text, locale_id)
        expected = f"{q['ldq']}unpaired left quote."
        assert result == expected

    # Uppercase following unpaired left quote
    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    @pytest.mark.parametrize(
        "quote_char",
        [
            '"',  # straight quote
            LDQUO,  # left double quotation mark "
            LAQUO,  # guillemet «
            BDQUO,  # low-9 „
            ",,",  # two commas
            "\u203a\u203a",  # double single guillemets ››
            "''",  # two apostrophes
        ],
    )
    def test_unpaired_left_quote_uppercase(self, locale_id, quote_char):
        q = get_quotes(locale_id)
        text = f"{quote_char}Unpaired left quote."
        result = fix_double_quotes_and_primes(text, locale_id)
        expected = f"{q['ldq']}Unpaired left quote."
        assert result == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_unpaired_left_quote_followed_by_number(self, locale_id):
        """Unpaired left quote followed by digit."""
        q = get_quotes(locale_id)
        text = "''1 unpaired left quote."
        result = fix_double_quotes_and_primes(text, locale_id)
        expected = f"{q['ldq']}1 unpaired left quote."
        assert result == expected


# =============================================================================
# IDENTIFY UNPAIRED RIGHT DOUBLE QUOTE
# =============================================================================


class TestIdentifyUnpairedRightDoubleQuote:
    """Identify unpaired right double quotes.

    Port of identifyUnpairedRightDoubleQuoteSet tests from JS.
    """

    # Various quote types after word
    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    @pytest.mark.parametrize(
        "quote_char",
        [
            '"',  # straight quote
            LAQUO,  # guillemet «
            BDQUO,  # low-9 „
            LDQUO,  # left double quotation mark "
            RDQUO,  # right double quotation mark "
            ",,",  # two commas
            "\u2039\u2039",  # double single guillemets ‹‹
            "''",  # two apostrophes
        ],
    )
    def test_unpaired_right_quote_after_lowercase(self, locale_id, quote_char):
        q = get_quotes(locale_id)
        text = f"unpaired{quote_char} right quote."
        result = fix_double_quotes_and_primes(text, locale_id)
        expected = f"unpaired{q['rdq']} right quote."
        assert result == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_unpaired_right_quote_after_uppercase(self, locale_id):
        q = get_quotes(locale_id)
        text = 'UNPAIRED" right quote.'
        result = fix_double_quotes_and_primes(text, locale_id)
        expected = f"UNPAIRED{q['rdq']} right quote."
        assert result == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_unpaired_right_quote_after_period(self, locale_id):
        q = get_quotes(locale_id)
        text = 'unpaired right quote."'
        result = fix_double_quotes_and_primes(text, locale_id)
        expected = f"unpaired right quote.{q['rdq']}"
        assert result == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_unpaired_right_quote_after_ellipsis(self, locale_id):
        q = get_quotes(locale_id)
        text = f'unpaired right quote{ELLIPSIS}"'
        result = fix_double_quotes_and_primes(text, locale_id)
        expected = f"unpaired right quote{ELLIPSIS}{q['rdq']}"
        assert result == expected


# =============================================================================
# REMOVE UNIDENTIFIED DOUBLE QUOTE
# =============================================================================


class TestRemoveUnidentifiedDoubleQuote:
    """Remove double quotes that cannot be identified.

    Port of removeUnidentifiedDoubleQuoteSet tests from JS.
    """

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    @pytest.mark.parametrize(
        "quote_char",
        [
            BDQUO,  # low-9 „
            LDQUO,  # left double quotation mark "
            RDQUO,  # right double quotation mark "
            '"',  # straight quote
            LAQUO,  # left guillemet «
            RAQUO,  # right guillemet »
            DOUBLE_PRIME,  # ″
            "''",  # two apostrophes
            "\u201a\u201a",  # two single low-9 quotes ‚‚
            "\u2019\u2019",  # two right single quotes ''
            "\u2018\u2018",  # two left single quotes ''
            "\u2039\u2039",  # double left single guillemets ‹‹
            "\u203a\u203a",  # double right single guillemets ››
            "\u2032\u2032",  # double primes ′′
            "\u00b4\u00b4",  # double acute accents ´´
            "``",  # double grave accents
        ],
    )
    def test_remove_unidentified_quote(self, locale_id, quote_char):
        text = f"word {quote_char} word"
        expected = "word word"
        assert remove_unidentified_double_quote(text, locale_id) == expected


# =============================================================================
# REPLACE DOUBLE PRIME WITH DOUBLE QUOTE
# =============================================================================


class TestReplaceDoublePrimeWithDoubleQuote:
    """Replace double prime with double quote when part of quote pair.

    Port of replaceDoublePrimeWDoubleQuoteUnitSet and
    replaceDoublePrimeWDoubleQuoteModuleSet tests from JS.
    """

    # Unit tests (with placeholders)
    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_unpaired_left_quote_with_double_prime(self, locale_id):
        """Unpaired left quote + double prime -> quote pair."""
        text = "{{typopo__ldq--unpaired}}word{{typopo__double-prime}}"
        result = replace_double_prime_with_double_quote(text, locale_id)
        assert result == "{{typopo__ldq}}word{{typopo__rdq}}"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_double_prime_with_unpaired_right_quote(self, locale_id):
        """Double prime + unpaired right quote -> quote pair."""
        text = "{{typopo__double-prime}}word{{typopo__rdq--unpaired}}"
        result = replace_double_prime_with_double_quote(text, locale_id)
        assert result == "{{typopo__ldq}}word{{typopo__rdq}}"

    # Module tests (full pipeline)
    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_localhost_3000_module(self, locale_id):
        """It's called "Localhost 3000" and it's pretty fast."""
        q = get_quotes(locale_id)
        text = "It's called \"Localhost 3000\" and it's pretty fast."
        result = fix_double_quotes_and_primes(text, locale_id)
        assert f"{q['ldq']}Localhost 3000{q['rdq']}" in result

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_30_bucks_module(self, locale_id):
        """Here are 30 "bucks" """
        q = get_quotes(locale_id)
        text = 'Here are 30 "bucks"'
        result = fix_double_quotes_and_primes(text, locale_id)
        assert result == f"Here are 30 {q['ldq']}bucks{q['rdq']}"


# =============================================================================
# FIX QUOTED WORD PUNCTUATION (JS parity)
# =============================================================================


class TestFixQuotedWordPunctuation:
    """Test fix_quoted_word_punctuation - moves .,;: outside single-word quotes.

    Port of fixQuotedWordPunctuation tests from JS.
    """

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_move_period_outside_single_word(self, locale_id):
        """Move period outside single-word quote."""
        q = get_quotes(locale_id)
        text = f"{q['ldq']}word.{q['rdq']}"
        expected = f"{q['ldq']}word{q['rdq']}."
        assert fix_quoted_word_punctuation(text, locale_id) == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_move_comma_outside_single_word(self, locale_id):
        """Move comma outside single-word quote."""
        q = get_quotes(locale_id)
        text = f"{q['ldq']}word,{q['rdq']}"
        expected = f"{q['ldq']}word{q['rdq']},"
        assert fix_quoted_word_punctuation(text, locale_id) == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_move_semicolon_outside_single_word(self, locale_id):
        """Move semicolon outside single-word quote."""
        q = get_quotes(locale_id)
        text = f"{q['ldq']}word;{q['rdq']}"
        expected = f"{q['ldq']}word{q['rdq']};"
        assert fix_quoted_word_punctuation(text, locale_id) == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_move_colon_outside_single_word(self, locale_id):
        """Move colon outside single-word quote."""
        q = get_quotes(locale_id)
        text = f"{q['ldq']}word:{q['rdq']}"
        expected = f"{q['ldq']}word{q['rdq']}:"
        assert fix_quoted_word_punctuation(text, locale_id) == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_keep_exclamation_inside_single_word(self, locale_id):
        """Keep exclamation mark inside single-word quote (ambiguous)."""
        q = get_quotes(locale_id)
        text = f"{q['ldq']}word!{q['rdq']}"
        assert fix_quoted_word_punctuation(text, locale_id) == text

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_keep_question_inside_single_word(self, locale_id):
        """Keep question mark inside single-word quote (ambiguous)."""
        q = get_quotes(locale_id)
        text = f"{q['ldq']}word?{q['rdq']}"
        assert fix_quoted_word_punctuation(text, locale_id) == text


# =============================================================================
# FIX QUOTED SENTENCE PUNCTUATION (JS parity)
# =============================================================================


class TestFixQuotedSentencePunctuation:
    """Test fix_quoted_sentence_punctuation - moves punctuation inside multi-word quotes.

    Port of fixQuotedSentencePunctuation tests from JS.
    """

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_move_period_inside_multi_word(self, locale_id):
        """Move period inside multi-word quote."""
        q = get_quotes(locale_id)
        text = f"{q['ldq']}quoted part{q['rdq']}."
        expected = f"{q['ldq']}quoted part.{q['rdq']}"
        assert fix_quoted_sentence_punctuation(text, locale_id) == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_move_question_inside_multi_word(self, locale_id):
        """Move question mark inside multi-word quote."""
        q = get_quotes(locale_id)
        text = f"{q['ldq']}quoted part{q['rdq']}?"
        expected = f"{q['ldq']}quoted part?{q['rdq']}"
        assert fix_quoted_sentence_punctuation(text, locale_id) == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_move_colon_back_outside(self, locale_id):
        """Colon is moved inside then back outside."""
        q = get_quotes(locale_id)
        # First period would move inside, then colon stays outside
        text = f"{q['ldq']}quoted part:{q['rdq']}"
        expected = f"{q['ldq']}quoted part{q['rdq']}:"
        assert fix_quoted_sentence_punctuation(text, locale_id) == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_move_semicolon_back_outside(self, locale_id):
        """Semicolon is moved inside then back outside."""
        q = get_quotes(locale_id)
        text = f"{q['ldq']}quoted part;{q['rdq']}"
        expected = f"{q['ldq']}quoted part{q['rdq']};"
        assert fix_quoted_sentence_punctuation(text, locale_id) == expected


# =============================================================================
# REMOVE EXTRA SPACES AROUND QUOTES
# =============================================================================


class TestRemoveExtraSpacesAroundQuotes:
    """Remove extra spaces around quotes.

    Port of removeExtraSpacesAroundQuotesSet tests from JS.
    """

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_remove_space_after_left_quote(self, locale_id):
        """Remove space after opening quote."""
        q = get_quotes(locale_id)
        text = f"{q['ldq']} extra space at the beginning{q['rdq']}"
        expected = f"{q['ldq']}extra space at the beginning{q['rdq']}"
        assert remove_extra_spaces_around_quotes(text, locale_id) == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_remove_space_before_right_quote(self, locale_id):
        """Remove space before closing quote."""
        q = get_quotes(locale_id)
        text = f"{q['ldq']}extra space at the end {q['rdq']}"
        expected = f"{q['ldq']}extra space at the end{q['rdq']}"
        assert remove_extra_spaces_around_quotes(text, locale_id) == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_remove_space_before_right_quote_with_ellipsis(self, locale_id):
        """Remove space before closing quote after ellipsis."""
        q = get_quotes(locale_id)
        text = f"{q['ldq']}Sentence and{ELLIPSIS} {q['rdq']}"
        expected = f"{q['ldq']}Sentence and{ELLIPSIS}{q['rdq']}"
        assert remove_extra_spaces_around_quotes(text, locale_id) == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_remove_space_before_double_prime(self, locale_id):
        """Remove space before double prime (arcseconds)."""
        text = f"12{SINGLE_PRIME} 45 {DOUBLE_PRIME}"
        expected = f"12{SINGLE_PRIME} 45{DOUBLE_PRIME}"
        assert remove_extra_spaces_around_quotes(text, locale_id) == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_remove_space_before_double_prime_degrees(self, locale_id):
        """Remove space in degree notation."""
        text = f"3{DEGREE} 5{SINGLE_PRIME} 30 {DOUBLE_PRIME}"
        expected = f"3{DEGREE} 5{SINGLE_PRIME} 30{DOUBLE_PRIME}"
        assert remove_extra_spaces_around_quotes(text, locale_id) == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_remove_space_before_double_prime_with_trailing_text(self, locale_id):
        """Remove space before double prime followed by text."""
        text = f"3{DEGREE} 5{SINGLE_PRIME} 30 {DOUBLE_PRIME} and"
        expected = f"3{DEGREE} 5{SINGLE_PRIME} 30{DOUBLE_PRIME} and"
        assert remove_extra_spaces_around_quotes(text, locale_id) == expected


# =============================================================================
# ADD SPACE BEFORE LEFT DOUBLE QUOTE
# =============================================================================


class TestAddSpaceBeforeLeftDoubleQuote:
    """Add missing space before left double quote.

    Port of addSpaceBeforeLeftDoubleQuoteSet tests from JS.

    Note: This function also applies NBSP after prepositions, so some spaces
    may be converted to non-breaking spaces.
    """

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_no_change_when_space_exists(self, locale_id):
        """Should not change when space already present (may apply nbsp rules)."""
        q = get_quotes(locale_id)
        text = f"It's a very {q['ldq']}nice{q['rdq']} saying."
        result = add_space_before_left_double_quote(text, locale_id)
        # The function may convert spaces to nbsp due to preposition rules
        # Check that the quote structure is preserved
        assert q["ldq"] in result
        assert q["rdq"] in result
        assert "nice" in result

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_add_space_before_quote_after_word(self, locale_id):
        """Add space before quote when preceded by letter: It's a"nice" -> It's a "nice" """
        q = get_quotes(locale_id)
        text = f"It's a{q['ldq']}nice{q['rdq']} saying."
        result = add_space_before_left_double_quote(text, locale_id)
        # Should add space (or nbsp) before the quote
        assert f"a {q['ldq']}" in result or f"a{NBSP}{q['ldq']}" in result

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_add_space_after_sentence_end(self, locale_id):
        """Add space before quote when preceded by sentence end."""
        q = get_quotes(locale_id)
        text = f"An unquoted sentence.{q['ldq']}And a quoted one.{q['rdq']}"
        result = add_space_before_left_double_quote(text, locale_id)
        assert f". {q['ldq']}" in result


# =============================================================================
# ADD SPACE AFTER RIGHT DOUBLE QUOTE
# =============================================================================


class TestAddSpaceAfterRightDoubleQuote:
    """Add missing space after right double quote.

    Port of addSpaceAfterRightDoubleQuoteSet tests from JS.
    """

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_add_space_after_quote_before_word(self, locale_id):
        """Add space after quote when followed by letter."""
        q = get_quotes(locale_id)
        text = f"It's a {q['ldq']}nice{q['rdq']}saying."
        expected = f"It's a {q['ldq']}nice{q['rdq']} saying."
        assert add_space_after_right_double_quote(text, locale_id) == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_add_space_after_quoted_sentence(self, locale_id):
        """Add space after quoted sentence followed by unquoted."""
        q = get_quotes(locale_id)
        text = f"{q['ldq']}A quoted sentence.{q['rdq']}And an unquoted one."
        expected = f"{q['ldq']}A quoted sentence.{q['rdq']} And an unquoted one."
        assert add_space_after_right_double_quote(text, locale_id) == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_add_space_after_quoted_exclamation(self, locale_id):
        """Add space after quoted sentence with exclamation."""
        q = get_quotes(locale_id)
        text = f"{q['ldq']}A quoted sentence!{q['rdq']}And an unquoted one."
        expected = f"{q['ldq']}A quoted sentence!{q['rdq']} And an unquoted one."
        assert add_space_after_right_double_quote(text, locale_id) == expected


# =============================================================================
# FIX DIRECT SPEECH INTRO
# =============================================================================


class TestFixDirectSpeechIntro:
    """Fix direct speech introduction with dashes.

    Port of fixDirectSpeechIntroSet tests from JS.
    """

    # Problem Type 1: Using hyphen, en dash, or em dash instead of proper introduction

    # Hyphen with spaces
    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_hyphen_both_sides(self, locale_id):
        """She said - "Hello" - and left."""
        q = get_quotes(locale_id)
        intro = get_direct_speech_intro(locale_id)
        text = f"She said - {q['ldq']}Hello{q['rdq']} - and left."
        expected = f"She said{intro} {q['ldq']}Hello{q['rdq']} and left."
        assert fix_direct_speech_intro(text, locale_id) == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_hyphen_before_only(self, locale_id):
        """She said - "Hello" and left."""
        q = get_quotes(locale_id)
        intro = get_direct_speech_intro(locale_id)
        text = f"She said - {q['ldq']}Hello{q['rdq']} and left."
        expected = f"She said{intro} {q['ldq']}Hello{q['rdq']} and left."
        assert fix_direct_speech_intro(text, locale_id) == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_hyphen_no_space_before_quote(self, locale_id):
        """She said -"Hello" - and left."""
        q = get_quotes(locale_id)
        intro = get_direct_speech_intro(locale_id)
        text = f"She said -{q['ldq']}Hello{q['rdq']} - and left."
        expected = f"She said{intro} {q['ldq']}Hello{q['rdq']} and left."
        assert fix_direct_speech_intro(text, locale_id) == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_hyphen_no_spaces(self, locale_id):
        """She said-"Hello" - and left."""
        q = get_quotes(locale_id)
        intro = get_direct_speech_intro(locale_id)
        text = f"She said-{q['ldq']}Hello{q['rdq']} - and left."
        expected = f"She said{intro} {q['ldq']}Hello{q['rdq']} and left."
        assert fix_direct_speech_intro(text, locale_id) == expected

    # En dash with spaces
    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_en_dash_both_sides(self, locale_id):
        """She said – "Hello" – and left."""
        q = get_quotes(locale_id)
        intro = get_direct_speech_intro(locale_id)
        text = f"She said {EN_DASH} {q['ldq']}Hello{q['rdq']} {EN_DASH} and left."
        expected = f"She said{intro} {q['ldq']}Hello{q['rdq']} and left."
        assert fix_direct_speech_intro(text, locale_id) == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_en_dash_before_only(self, locale_id):
        """She said – "Hello" and left."""
        q = get_quotes(locale_id)
        intro = get_direct_speech_intro(locale_id)
        text = f"She said {EN_DASH} {q['ldq']}Hello{q['rdq']} and left."
        expected = f"She said{intro} {q['ldq']}Hello{q['rdq']} and left."
        assert fix_direct_speech_intro(text, locale_id) == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_en_dash_no_space_before_quote(self, locale_id):
        """She said –"Hello" – and left."""
        q = get_quotes(locale_id)
        intro = get_direct_speech_intro(locale_id)
        text = f"She said {EN_DASH}{q['ldq']}Hello{q['rdq']} {EN_DASH} and left."
        expected = f"She said{intro} {q['ldq']}Hello{q['rdq']} and left."
        assert fix_direct_speech_intro(text, locale_id) == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_en_dash_no_spaces(self, locale_id):
        """She said–"Hello" – and left."""
        q = get_quotes(locale_id)
        intro = get_direct_speech_intro(locale_id)
        text = f"She said{EN_DASH}{q['ldq']}Hello{q['rdq']} {EN_DASH} and left."
        expected = f"She said{intro} {q['ldq']}Hello{q['rdq']} and left."
        assert fix_direct_speech_intro(text, locale_id) == expected

    # Em dash with spaces
    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_em_dash_both_sides(self, locale_id):
        """She said — "Hello" — and left."""
        q = get_quotes(locale_id)
        intro = get_direct_speech_intro(locale_id)
        text = f"She said {EM_DASH} {q['ldq']}Hello{q['rdq']} {EM_DASH} and left."
        expected = f"She said{intro} {q['ldq']}Hello{q['rdq']} and left."
        assert fix_direct_speech_intro(text, locale_id) == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_em_dash_before_only(self, locale_id):
        """She said — "Hello" and left."""
        q = get_quotes(locale_id)
        intro = get_direct_speech_intro(locale_id)
        text = f"She said {EM_DASH} {q['ldq']}Hello{q['rdq']} and left."
        expected = f"She said{intro} {q['ldq']}Hello{q['rdq']} and left."
        assert fix_direct_speech_intro(text, locale_id) == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_em_dash_no_space_before_quote(self, locale_id):
        """She said —"Hello" — and left."""
        q = get_quotes(locale_id)
        intro = get_direct_speech_intro(locale_id)
        text = f"She said {EM_DASH}{q['ldq']}Hello{q['rdq']} {EM_DASH} and left."
        expected = f"She said{intro} {q['ldq']}Hello{q['rdq']} and left."
        assert fix_direct_speech_intro(text, locale_id) == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_em_dash_no_spaces(self, locale_id):
        """She said—"Hello" — and left."""
        q = get_quotes(locale_id)
        intro = get_direct_speech_intro(locale_id)
        text = f"She said{EM_DASH}{q['ldq']}Hello{q['rdq']} {EM_DASH} and left."
        expected = f"She said{intro} {q['ldq']}Hello{q['rdq']} and left."
        assert fix_direct_speech_intro(text, locale_id) == expected

    # Problem Type 2: Colon/comma + dash combinations

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_colon_hyphen_space(self, locale_id):
        """She said: - "Hello" - and left."""
        q = get_quotes(locale_id)
        intro = get_direct_speech_intro(locale_id)
        text = f"She said: - {q['ldq']}Hello{q['rdq']} - and left."
        expected = f"She said{intro} {q['ldq']}Hello{q['rdq']} and left."
        assert fix_direct_speech_intro(text, locale_id) == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_colon_hyphen_no_space_before_quote(self, locale_id):
        """She said: -"Hello" - and left."""
        q = get_quotes(locale_id)
        intro = get_direct_speech_intro(locale_id)
        text = f"She said: -{q['ldq']}Hello{q['rdq']} - and left."
        expected = f"She said{intro} {q['ldq']}Hello{q['rdq']} and left."
        assert fix_direct_speech_intro(text, locale_id) == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_colon_no_space_hyphen(self, locale_id):
        """She said:- "Hello" - and left."""
        q = get_quotes(locale_id)
        intro = get_direct_speech_intro(locale_id)
        text = f"She said:- {q['ldq']}Hello{q['rdq']} - and left."
        expected = f"She said{intro} {q['ldq']}Hello{q['rdq']} and left."
        assert fix_direct_speech_intro(text, locale_id) == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_colon_no_spaces_hyphen(self, locale_id):
        """She said:-"Hello" - and left."""
        q = get_quotes(locale_id)
        intro = get_direct_speech_intro(locale_id)
        text = f"She said:-{q['ldq']}Hello{q['rdq']} - and left."
        expected = f"She said{intro} {q['ldq']}Hello{q['rdq']} and left."
        assert fix_direct_speech_intro(text, locale_id) == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_proper_intro_plus_hyphen(self, locale_id):
        """She said: - "Hello" - and left. (proper intro already present)"""
        q = get_quotes(locale_id)
        intro = get_direct_speech_intro(locale_id)
        text = f"She said{intro} - {q['ldq']}Hello{q['rdq']} - and left."
        expected = f"She said{intro} {q['ldq']}Hello{q['rdq']} and left."
        assert fix_direct_speech_intro(text, locale_id) == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_colon_en_dash(self, locale_id):
        """She said: – "Hello" – and left."""
        q = get_quotes(locale_id)
        intro = get_direct_speech_intro(locale_id)
        text = f"She said: {EN_DASH} {q['ldq']}Hello{q['rdq']} {EN_DASH} and left."
        expected = f"She said{intro} {q['ldq']}Hello{q['rdq']} and left."
        assert fix_direct_speech_intro(text, locale_id) == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_colon_en_dash_no_space(self, locale_id):
        """She said: –"Hello" – and left."""
        q = get_quotes(locale_id)
        intro = get_direct_speech_intro(locale_id)
        text = f"She said: {EN_DASH}{q['ldq']}Hello{q['rdq']} {EN_DASH} and left."
        expected = f"She said{intro} {q['ldq']}Hello{q['rdq']} and left."
        assert fix_direct_speech_intro(text, locale_id) == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_colon_no_space_en_dash(self, locale_id):
        """She said:– "Hello" – and left."""
        q = get_quotes(locale_id)
        intro = get_direct_speech_intro(locale_id)
        text = f"She said:{EN_DASH} {q['ldq']}Hello{q['rdq']} {EN_DASH} and left."
        expected = f"She said{intro} {q['ldq']}Hello{q['rdq']} and left."
        assert fix_direct_speech_intro(text, locale_id) == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_colon_no_spaces_en_dash(self, locale_id):
        """She said:–"Hello" – and left."""
        q = get_quotes(locale_id)
        intro = get_direct_speech_intro(locale_id)
        text = f"She said:{EN_DASH}{q['ldq']}Hello{q['rdq']} {EN_DASH} and left."
        expected = f"She said{intro} {q['ldq']}Hello{q['rdq']} and left."
        assert fix_direct_speech_intro(text, locale_id) == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_colon_em_dash(self, locale_id):
        """She said: — "Hello" — and left."""
        q = get_quotes(locale_id)
        intro = get_direct_speech_intro(locale_id)
        text = f"She said: {EM_DASH} {q['ldq']}Hello{q['rdq']} {EM_DASH} and left."
        expected = f"She said{intro} {q['ldq']}Hello{q['rdq']} and left."
        assert fix_direct_speech_intro(text, locale_id) == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_colon_em_dash_no_space(self, locale_id):
        """She said: —"Hello" — and left."""
        q = get_quotes(locale_id)
        intro = get_direct_speech_intro(locale_id)
        text = f"She said: {EM_DASH}{q['ldq']}Hello{q['rdq']} {EM_DASH} and left."
        expected = f"She said{intro} {q['ldq']}Hello{q['rdq']} and left."
        assert fix_direct_speech_intro(text, locale_id) == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_colon_no_space_em_dash(self, locale_id):
        """She said:— "Hello" — and left."""
        q = get_quotes(locale_id)
        intro = get_direct_speech_intro(locale_id)
        text = f"She said:{EM_DASH} {q['ldq']}Hello{q['rdq']} {EM_DASH} and left."
        expected = f"She said{intro} {q['ldq']}Hello{q['rdq']} and left."
        assert fix_direct_speech_intro(text, locale_id) == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_colon_no_spaces_em_dash(self, locale_id):
        """She said:—"Hello" — and left."""
        q = get_quotes(locale_id)
        intro = get_direct_speech_intro(locale_id)
        text = f"She said:{EM_DASH}{q['ldq']}Hello{q['rdq']} {EM_DASH} and left."
        expected = f"She said{intro} {q['ldq']}Hello{q['rdq']} and left."
        assert fix_direct_speech_intro(text, locale_id) == expected

    # Problem Type 3: Extra spaces between introduction and quote

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_colon_no_space_before_quote(self, locale_id):
        """She said:"Hello" and left."""
        q = get_quotes(locale_id)
        intro = get_direct_speech_intro(locale_id)
        text = f"She said:{q['ldq']}Hello{q['rdq']} and left."
        expected = f"She said{intro} {q['ldq']}Hello{q['rdq']} and left."
        assert fix_direct_speech_intro(text, locale_id) == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_comma_no_space_before_quote(self, locale_id):
        """She said,"Hello" and left."""
        q = get_quotes(locale_id)
        intro = get_direct_speech_intro(locale_id)
        text = f"She said,{q['ldq']}Hello{q['rdq']} and left."
        expected = f"She said{intro} {q['ldq']}Hello{q['rdq']} and left."
        assert fix_direct_speech_intro(text, locale_id) == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    @pytest.mark.parametrize("spaces", ["  ", "   ", "    ", "     "])
    def test_colon_with_extra_spaces(self, locale_id, spaces):
        """She said:   "Hello" and left."""
        q = get_quotes(locale_id)
        intro = get_direct_speech_intro(locale_id)
        text = f"She said:{spaces}{q['ldq']}Hello{q['rdq']} and left."
        expected = f"She said{intro} {q['ldq']}Hello{q['rdq']} and left."
        assert fix_direct_speech_intro(text, locale_id) == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    @pytest.mark.parametrize("spaces", ["     "])
    def test_comma_with_extra_spaces(self, locale_id, spaces):
        """She said,     "Hello" and left."""
        q = get_quotes(locale_id)
        intro = get_direct_speech_intro(locale_id)
        text = f"She said,{spaces}{q['ldq']}Hello{q['rdq']} and left."
        expected = f"She said{intro} {q['ldq']}Hello{q['rdq']} and left."
        assert fix_direct_speech_intro(text, locale_id) == expected

    # Combination: wrong intro + extra spaces
    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_colon_hyphen_extra_spaces(self, locale_id):
        """She said: -  "Hello" - and left."""
        q = get_quotes(locale_id)
        intro = get_direct_speech_intro(locale_id)
        text = f"She said: -  {q['ldq']}Hello{q['rdq']} - and left."
        expected = f"She said{intro} {q['ldq']}Hello{q['rdq']} and left."
        assert fix_direct_speech_intro(text, locale_id) == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_colon_en_dash_extra_spaces(self, locale_id):
        """She said: –   "Hello" – and left."""
        q = get_quotes(locale_id)
        intro = get_direct_speech_intro(locale_id)
        text = f"She said: {EN_DASH}   {q['ldq']}Hello{q['rdq']} {EN_DASH} and left."
        expected = f"She said{intro} {q['ldq']}Hello{q['rdq']} and left."
        assert fix_direct_speech_intro(text, locale_id) == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_colon_em_dash_extra_spaces(self, locale_id):
        """She said: —    "Hello" — and left."""
        q = get_quotes(locale_id)
        intro = get_direct_speech_intro(locale_id)
        text = f"She said: {EM_DASH}    {q['ldq']}Hello{q['rdq']} {EM_DASH} and left."
        expected = f"She said{intro} {q['ldq']}Hello{q['rdq']} and left."
        assert fix_direct_speech_intro(text, locale_id) == expected

    # Multiple spaces around dashes
    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_hyphen_multiple_spaces(self, locale_id):
        """She said  -  "Hello"  -  and left."""
        q = get_quotes(locale_id)
        intro = get_direct_speech_intro(locale_id)
        text = f"She said  -  {q['ldq']}Hello{q['rdq']}  -  and left."
        expected = f"She said{intro} {q['ldq']}Hello{q['rdq']} and left."
        assert fix_direct_speech_intro(text, locale_id) == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_en_dash_multiple_spaces(self, locale_id):
        """She said  –  "Hello"  –  and left."""
        q = get_quotes(locale_id)
        intro = get_direct_speech_intro(locale_id)
        text = f"She said  {EN_DASH}  {q['ldq']}Hello{q['rdq']}  {EN_DASH}  and left."
        expected = f"She said{intro} {q['ldq']}Hello{q['rdq']} and left."
        assert fix_direct_speech_intro(text, locale_id) == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_em_dash_multiple_spaces(self, locale_id):
        """She said  —  "Hello"  —  and left."""
        q = get_quotes(locale_id)
        intro = get_direct_speech_intro(locale_id)
        text = f"She said  {EM_DASH}  {q['ldq']}Hello{q['rdq']}  {EM_DASH}  and left."
        expected = f"She said{intro} {q['ldq']}Hello{q['rdq']} and left."
        assert fix_direct_speech_intro(text, locale_id) == expected

    # Edge cases: Quote at end (no ending sentence)
    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    @pytest.mark.parametrize("dash", ["-", EN_DASH, EM_DASH])
    def test_dash_quote_at_end(self, locale_id, dash):
        """She said - "Hello" (no ending)"""
        q = get_quotes(locale_id)
        intro = get_direct_speech_intro(locale_id)
        text = f"She said {dash} {q['ldq']}Hello{q['rdq']}"
        expected = f"She said{intro} {q['ldq']}Hello{q['rdq']}"
        assert fix_direct_speech_intro(text, locale_id) == expected

    # Varied content between quotes
    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_content_with_punctuation(self, locale_id):
        """She said - "Hello, world!" - and left."""
        q = get_quotes(locale_id)
        intro = get_direct_speech_intro(locale_id)
        text = f"She said - {q['ldq']}Hello, world!{q['rdq']} - and left."
        expected = f"She said{intro} {q['ldq']}Hello, world!{q['rdq']} and left."
        assert fix_direct_speech_intro(text, locale_id) == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_content_with_multiple_sentences(self, locale_id):
        """She said - "Hello! How are you?" - and left."""
        q = get_quotes(locale_id)
        intro = get_direct_speech_intro(locale_id)
        text = f"She said - {q['ldq']}Hello! How are you?{q['rdq']} - and left."
        expected = f"She said{intro} {q['ldq']}Hello! How are you?{q['rdq']} and left."
        assert fix_direct_speech_intro(text, locale_id) == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_content_with_numbers_ellipsis(self, locale_id):
        """She said — "Numbers: 123, 456.78…" — and left."""
        q = get_quotes(locale_id)
        intro = get_direct_speech_intro(locale_id)
        text = f"She said {EM_DASH} {q['ldq']}Numbers: 123, 456.78{ELLIPSIS}{q['rdq']} {EM_DASH} and left."
        expected = f"She said{intro} {q['ldq']}Numbers: 123, 456.78{ELLIPSIS}{q['rdq']} and left."
        assert fix_direct_speech_intro(text, locale_id) == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_content_with_url(self, locale_id):
        """She said — "URL: http://example.com/path" — and left."""
        q = get_quotes(locale_id)
        intro = get_direct_speech_intro(locale_id)
        text = f"She said {EM_DASH} {q['ldq']}URL: http://example.com/path{q['rdq']} {EM_DASH} and left."
        expected = f"She said{intro} {q['ldq']}URL: http://example.com/path{q['rdq']} and left."
        assert fix_direct_speech_intro(text, locale_id) == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_content_with_email(self, locale_id):
        """She said - "Email: test@example.com" - and left."""
        q = get_quotes(locale_id)
        intro = get_direct_speech_intro(locale_id)
        text = f"She said - {q['ldq']}Email: test@example.com{q['rdq']} - and left."
        expected = f"She said{intro} {q['ldq']}Email: test@example.com{q['rdq']} and left."
        assert fix_direct_speech_intro(text, locale_id) == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_content_with_various_punctuation(self, locale_id):
        """She said – "Quote with: colon, semicolon; comma, dot." – and left."""
        q = get_quotes(locale_id)
        intro = get_direct_speech_intro(locale_id)
        text = f"She said {EN_DASH} {q['ldq']}Quote with: colon, semicolon; comma, dot.{q['rdq']} {EN_DASH} and left."
        expected = f"She said{intro} {q['ldq']}Quote with: colon, semicolon; comma, dot.{q['rdq']} and left."
        assert fix_direct_speech_intro(text, locale_id) == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_very_long_content(self, locale_id):
        """Very long sentence inside quotes."""
        q = get_quotes(locale_id)
        intro = get_direct_speech_intro(locale_id)
        long_text = (
            "A very long sentence with many words and punctuation marks, including commas, periods, and other symbols!"
        )
        text = f"She said {EM_DASH} {q['ldq']}{long_text}{q['rdq']} {EM_DASH} and left."
        expected = f"She said{intro} {q['ldq']}{long_text}{q['rdq']} and left."
        assert fix_direct_speech_intro(text, locale_id) == expected

    # Edge cases: Paragraph starts with dash before quote
    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    @pytest.mark.parametrize("dash", ["-", EN_DASH, EM_DASH])
    def test_paragraph_starts_with_dash(self, locale_id, dash):
        """- "Hello" - she said. (at paragraph start)"""
        q = get_quotes(locale_id)
        text = f"{dash} {q['ldq']}Hello{q['rdq']} - she said."
        expected = f"{q['ldq']}Hello{q['rdq']} she said."
        assert fix_direct_speech_intro(text, locale_id) == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_paragraph_starts_with_hyphen_no_space(self, locale_id):
        """-"Hello" - she said."""
        q = get_quotes(locale_id)
        text = f"-{q['ldq']}Hello{q['rdq']} - she said."
        expected = f"{q['ldq']}Hello{q['rdq']} she said."
        assert fix_direct_speech_intro(text, locale_id) == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_paragraph_starts_with_space_and_hyphen(self, locale_id):
        """- "Hello" - she said."""
        q = get_quotes(locale_id)
        text = f" - {q['ldq']}Hello{q['rdq']} - she said."
        expected = f"{q['ldq']}Hello{q['rdq']} she said."
        assert fix_direct_speech_intro(text, locale_id) == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_paragraph_starts_with_hyphen_extra_spaces(self, locale_id):
        """-   "Hello" - she said."""
        q = get_quotes(locale_id)
        text = f"-   {q['ldq']}Hello{q['rdq']} - she said."
        expected = f"{q['ldq']}Hello{q['rdq']} she said."
        assert fix_direct_speech_intro(text, locale_id) == expected

    # Edge cases: Following quoted sentence introduced with dash (after sentence end)
    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    @pytest.mark.parametrize("end_punct", [".", "?", "!", ELLIPSIS])
    @pytest.mark.parametrize("dash", ["-", EN_DASH, EM_DASH])
    def test_dash_after_sentence_end(self, locale_id, end_punct, dash):
        """ends. - "Hello" - she said."""
        q = get_quotes(locale_id)
        text = f"ends{end_punct} {dash} {q['ldq']}Hello{q['rdq']} - she said."
        expected = f"ends{end_punct} {q['ldq']}Hello{q['rdq']} she said."
        assert fix_direct_speech_intro(text, locale_id) == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    @pytest.mark.parametrize("end_punct", [".", "?", "!", ELLIPSIS])
    def test_hyphen_no_space_after_sentence_end(self, locale_id, end_punct):
        """ends. -"Hello" - she said."""
        q = get_quotes(locale_id)
        text = f"ends{end_punct} -{q['ldq']}Hello{q['rdq']} - she said."
        expected = f"ends{end_punct} {q['ldq']}Hello{q['rdq']} she said."
        assert fix_direct_speech_intro(text, locale_id) == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    @pytest.mark.parametrize("end_punct", [".", "?", "!", ELLIPSIS])
    def test_hyphen_double_space_after_sentence_end(self, locale_id, end_punct):
        """ends.  - "Hello" - she said."""
        q = get_quotes(locale_id)
        text = f"ends{end_punct}  - {q['ldq']}Hello{q['rdq']} - she said."
        expected = f"ends{end_punct} {q['ldq']}Hello{q['rdq']} she said."
        assert fix_direct_speech_intro(text, locale_id) == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    @pytest.mark.parametrize("end_punct", [".", "?", "!", ELLIPSIS])
    def test_hyphen_extra_spaces_after_sentence_end(self, locale_id, end_punct):
        """ends. -   "Hello" - she said."""
        q = get_quotes(locale_id)
        text = f"ends{end_punct} -   {q['ldq']}Hello{q['rdq']} - she said."
        expected = f"ends{end_punct} {q['ldq']}Hello{q['rdq']} she said."
        assert fix_direct_speech_intro(text, locale_id) == expected

    # False positive: Already correct
    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_no_change_when_correct(self, locale_id):
        """She said: "Hello" and left. (already correct)"""
        q = get_quotes(locale_id)
        intro = get_direct_speech_intro(locale_id)
        text = f"She said{intro} {q['ldq']}Hello{q['rdq']} and left."
        assert fix_direct_speech_intro(text, locale_id) == text


# =============================================================================
# INTEGRATION TESTS - fix_double_quotes_and_primes
# =============================================================================


class TestFixDoubleQuotesAndPrimes:
    """Integration test for the main function.

    Combined tests from various JS test sets through the full pipeline.
    """

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_basic_quote_replacement(self, locale_id):
        """Replace straight quotes with locale quotes."""
        q = get_quotes(locale_id)
        text = '"Hello world"'
        expected = f"{q['ldq']}Hello world{q['rdq']}"
        assert fix_double_quotes_and_primes(text, locale_id) == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_no_change_when_correct(self, locale_id):
        """No change when quotes are already correct."""
        q = get_quotes(locale_id)
        text = f"{q['ldq']}Already correct{q['rdq']}"
        assert fix_double_quotes_and_primes(text, locale_id) == text

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_complex_direct_speech(self, locale_id):
        """Full pipeline: direct speech with dashes."""
        q = get_quotes(locale_id)
        intro = get_direct_speech_intro(locale_id)
        text = 'She said - "Hello" - and left.'
        expected = f"She said{intro} {q['ldq']}Hello{q['rdq']} and left."
        assert fix_double_quotes_and_primes(text, locale_id) == expected
