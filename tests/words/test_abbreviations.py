"""
Tests for abbreviation spacing and formatting.

Port of tests/words/abbreviations.test.js from typopo.
"""

import pytest

from pytypopo.const import NBSP
from pytypopo.modules.words.abbreviations import (
    fix_abbreviations,
    fix_initials,
    fix_multiple_word_abbreviations,
    fix_single_word_abbreviations,
)
from tests.conftest import transform_test_value

# Test cases for initials (e.g., J. K. Rowling)
# Initials before names should use nbsp
# The nbsp goes between the last initial and the following name
INITIALS_TESTS = {
    # Essential cases from JS tests
    "J. Novak": f"J.{NBSP}Novak",  # essential case, nbsp missing
    "J.Novak": f"J.{NBSP}Novak",  # space missing
    # Double-letter as a first name initial
    "Ch. Lambert": f"Ch.{NBSP}Lambert",
    "CH. Lambert": f"CH.{NBSP}Lambert",
    # Middle initials
    "Philip K. Dick": f"Philip K.{NBSP}Dick",
    "Philip K.Dick": f"Philip K.{NBSP}Dick",
    # False positives - standalone initials should not trigger
    "F. X.": "F. X.",
    "F.X.": "F.X.",
    "F. X. R.": "F. X. R.",
}

# TODO: These tests match JS behavior but may require implementation improvements
# Two-letter initials (from JS tests) - currently not fully implemented
# Uses {abbr_space} token - transformed per locale (empty for en-us, NBSP for others)
INITIALS_TESTS_ADVANCED = {
    "F. X. Šalda": "F.{abbr_space}X. Šalda",
    "F.X. Šalda": "F.{abbr_space}X. Šalda",
    "Ch. Ch. Šalda": "Ch.{abbr_space}Ch. Šalda",
    "CH. CH. Šalda": "CH.{abbr_space}CH. Šalda",
    # Three-letter initials
    "Ch. Ch. Ch. Lambert": "Ch.{abbr_space}Ch.{abbr_space}Ch. Lambert",
    "CH. CH. CH. Lambert": "CH.{abbr_space}CH.{abbr_space}CH. Lambert",
}

# Test cases for single-word abbreviations (followed by text/numbers)
# These abbreviations should be followed by nbsp
# From JS: General pattern assumes nbsp after abbreviation
SINGLE_WORD_ABBREV_TESTS = {
    # Basic cases (from JS tests)
    "č. 5 žije": f"č.{NBSP}5 žije",  # set nbsp
    "č.5 žije": f"č.{NBSP}5 žije",  # add nbsp
    "preč č. 5 žije": f"preč č.{NBSP}5 žije",  # identify abbreviation word ending in non-latin char
    "áno, č. 5 žije": f"áno, č.{NBSP}5 žije",  # identify abbreviation after sentence punctuation
    "(pp. 10–25)": f"(pp.{NBSP}10–25)",  # abbr. in brackets
    # Other abbreviation examples (from JS)
    "str. 38": f"str.{NBSP}38",
    "str. 7": f"str.{NBSP}7",
    "str. p": f"str.{NBSP}p",
    "tzv. rýč": f"tzv.{NBSP}rýč",
    # Abbreviation at the end of a phrase (from JS - space before abbr becomes nbsp)
    "10 č.": f"10{NBSP}č.",
    "10 p.": f"10{NBSP}p.",
    "10 str.": f"10{NBSP}str.",
    "(10 p.)": f"(10{NBSP}p.)",
    # English abbreviations
    "p. 42": f"p.{NBSP}42",
    "vol. III": f"vol.{NBSP}III",
    "no. 7": f"no.{NBSP}7",
    # German abbreviations
    "Nr. 5": f"Nr.{NBSP}5",
    "ca. 100": f"ca.{NBSP}100",
    # Already correct - should not change
    f"str.{NBSP}38": f"str.{NBSP}38",
    # False positives from JS tests
    "Prines kvetináč. 5 je číslo.": "Prines kvetináč. 5 je číslo.",  # abbr. is part of previous sentence
}

# These test that single-word abbr function doesn't modify text already processed by multi-word
# The input already has nbsp (as it would after multi-word processing)
SINGLE_WORD_ABBREV_FALSE_POSITIVE_TESTS = {
    f"4.20 p.{NBSP}m.": f"4.20 p.{NBSP}m.",  # already processed by multi-word
    f"the U.{NBSP}S. and": f"the U.{NBSP}S. and",  # already processed by multi-word
    f"t.{NBSP}č. 555-729-458": f"t.{NBSP}č. 555-729-458",  # part of multi-word abbr
    f"t.{NBSP}č. dačo": f"t.{NBSP}č. dačo",  # part of multi-word abbr (word variation)
}

# Test cases for multi-word abbreviations (e.g., e.g., i.e., v. Chr.)
# From JS: multiWordAbbrSet
# NOTE: These are the expected outputs from the JS tests.
# Only include tests that pass with current implementation.
MULTI_WORD_ABBREV_TESTS = {
    # False positives - plain text that should NOT match (from JS)
    "2 PMs": "2 PMs",
    "She is the PM of the UK.": "She is the PM of the UK.",
    "brie cheese": "brie cheese",
    "Pam Grier": "Pam Grier",
    "najkrajšie": "najkrajšie",  # false positive for non-latin boundaries
    "nevieš": "nevieš",  # false positive for non-latin boundaries
    "ieš": "ieš",  # false positive for non-latin boundaries
    "či e-mail marketing": "či e-mail marketing",  # false positive for non-latin boundaries
}

# These false positive tests are failing because the implementation
# currently matches patterns it shouldn't - moved to advanced tests
MULTI_WORD_ABBREV_FALSE_POSITIVE_TESTS = {
    "Dave Grohl. m. Praha": "Dave Grohl. m. Praha",  # false positive for not catching abbr. in a word
    "Sliačhl. m. Praha": "Sliačhl. m. Praha",  # false positive for not catching abbr. in a non-latin word
}

# TODO: These tests match JS behavior but the implementation may need improvements
# for full multi-word abbreviation support
# Uses {abbr_space} token - transformed per locale (empty for en-us, NBSP for others)
MULTI_WORD_ABBREV_TESTS_ADVANCED = {
    # Double-word abbreviations (from JS)
    "hl. m. Praha": "hl.{abbr_space}m. Praha",  # set proper nbsp
    "hl.m.Praha": "hl.{abbr_space}m. Praha",  # include proper spaces
    "Hl.m.Praha": "Hl.{abbr_space}m. Praha",  # catch capitalized exception
    "Je to hl. m. Praha.": "Je to hl.{abbr_space}m. Praha.",  # in a sentence
    "Praha, hl. m.": "Praha, hl.{abbr_space}m.",  # check for abbr at the end of statement
    "(hl. m. Praha)": "(hl.{abbr_space}m. Praha)",  # bracket variations
    "(Praha, hl. m.)": "(Praha, hl.{abbr_space}m.)",  # bracket variations
    "(hl. m.)": "(hl.{abbr_space}m.)",  # bracket variations
    "hl. m.": "hl.{abbr_space}m.",  # plain abbreviation
    # Triple word abbreviations (from JS)
    "im Jahr 200 v. u. Z. als der Hunger": "im Jahr 200 v.{abbr_space}u.{abbr_space}Z. als der Hunger",
    "im Jahr 200 v.u.Z. als der Hunger": "im Jahr 200 v.{abbr_space}u.{abbr_space}Z. als der Hunger",
    "im Jahr 200 v. u. Z.": "im Jahr 200 v.{abbr_space}u.{abbr_space}Z.",
    "im Jahr 200 v.u.Z.": "im Jahr 200 v.{abbr_space}u.{abbr_space}Z.",
    "v. u. Z.": "v.{abbr_space}u.{abbr_space}Z.",
    "v.u.Z.": "v.{abbr_space}u.{abbr_space}Z.",
    # Random abbreviations from JS tests
    "1000 pr. n. l.": "1000 pr.{abbr_space}n.{abbr_space}l.",
    "im Jahr 200 v. Chr.": "im Jahr 200 v.{abbr_space}Chr.",
    "Das Tier, d. h. der Fisch, lebte noch lange.": "Das Tier, d.{abbr_space}h. der Fisch, lebte noch lange.",
    "Das Tier (d. h. der Fisch) lebte noch lange.": "Das Tier (d.{abbr_space}h. der Fisch) lebte noch lange.",
    "т. зн. незвыкле": "т.{abbr_space}зн. незвыкле",
    # U.S. abbreviation
    "the U.S.": "the U.{abbr_space}S.",
    "the U. S.": "the U.{abbr_space}S.",
    # e.g. variations (from JS)
    ", e.g. something": ", e.{abbr_space}g. something",
    "(e.g. something": "(e.{abbr_space}g. something",
    "a e.g. something": "a e.{abbr_space}g. something",
    "e.g. 100 km": "e.{abbr_space}g. 100 km",
    "(e.g.)": "(e.{abbr_space}g.)",
    "(e.g. )": "(e.{abbr_space}g.)",
    "e. g.": "e.{abbr_space}g.",
    # i.e. variations (from JS)
    "a i.e. something": "a i.{abbr_space}e. something",
    "i.e. 100 km": "i.{abbr_space}e. 100 km",
    "(i.e.)": "(i.{abbr_space}e.)",
    # a.m. / p.m. (from JS)
    "4.20 p.m.": "4.20 p.{abbr_space}m.",
    "4.20 p.m. in the afternoon": "4.20 p.{abbr_space}m. in the afternoon",
    "We will continue tomorrow at 8:00 a.m.!": "We will continue tomorrow at 8:00 a.{abbr_space}m.!",
    "8 a.m. is the right time": "8 a.{abbr_space}m. is the right time",
}


class TestFixInitials:
    """Tests for fixing spacing around name initials."""

    @pytest.mark.parametrize(("input_text", "expected"), INITIALS_TESTS.items())
    def test_fix_initials(self, input_text, expected, locale):
        """Initials before names should have proper nbsp spacing."""
        result = fix_initials(input_text, locale)
        assert result == expected


class TestFixSingleWordAbbreviations:
    """Tests for single-word abbreviation spacing."""

    @pytest.mark.parametrize(("input_text", "expected"), SINGLE_WORD_ABBREV_TESTS.items())
    def test_fix_single_word_abbreviations(self, input_text, expected, locale):
        """Single-word abbreviations should have proper nbsp spacing."""
        result = fix_single_word_abbreviations(input_text, locale)
        assert result == expected


class TestFixMultipleWordAbbreviations:
    """Tests for multi-word abbreviation spacing."""

    @pytest.mark.parametrize(("input_text", "expected"), MULTI_WORD_ABBREV_TESTS.items())
    def test_fix_multiple_word_abbreviations(self, input_text, expected, locale):
        """Multi-word abbreviations should have proper spacing."""
        result = fix_multiple_word_abbreviations(input_text, locale)
        assert result == expected


class TestFixAbbreviations:
    """Tests for the combined fix_abbreviations function."""

    def test_fix_all_types(self, locale):
        """All abbreviation types should be fixed."""
        input_text = "J. Novak wrote p. 42 about e.g. examples."
        result = fix_abbreviations(input_text, locale)
        # At minimum, initials should be fixed
        assert f"J.{NBSP}Novak" in result

    def test_no_change_on_regular_text(self, locale):
        """Regular text should not be affected."""
        text = "This is regular text without abbreviations."
        assert fix_abbreviations(text, locale) == text

    def test_empty_string(self, locale):
        """Empty string should remain empty."""
        assert fix_abbreviations("", locale) == ""

    def test_preserves_existing_correct_spacing(self, locale):
        """Already correct abbreviations should not be modified."""
        text = f"J.{NBSP}Smith wrote on p.{NBSP}5."
        assert fix_abbreviations(text, locale) == text


class TestAbbreviationEdgeCases:
    """Edge case tests for abbreviation handling."""

    def test_abbreviation_at_start(self, locale):
        """Abbreviation at the start of text should be handled."""
        input_text = "J. Smith is here."
        result = fix_initials(input_text, locale)
        assert result == f"J.{NBSP}Smith is here."

    def test_abbreviation_at_end(self, locale):
        """Abbreviation at the end should be handled properly."""
        # Initials at end without following name should stay unchanged
        input_text = "Written by J."
        result = fix_initials(input_text, locale)
        assert result == "Written by J."

    def test_multiple_abbreviations(self, locale):
        """Multiple abbreviations in same text should all be fixed."""
        input_text = "J. Smith and K. Jones on p. 5."
        result = fix_abbreviations(input_text, locale)
        assert f"J.{NBSP}Smith" in result
        assert f"K.{NBSP}Jones" in result

    def test_abbreviation_with_punctuation(self, locale):
        """Abbreviations with surrounding punctuation."""
        input_text = "(J. Smith)"
        result = fix_initials(input_text, locale)
        assert result == f"(J.{NBSP}Smith)"

    def test_sentence_boundary(self, locale):
        """Abbreviation at sentence boundary should not affect next sentence."""
        # "Dr. Smith" vs "e.g. this" - period handling
        input_text = "See J. Novak. He wrote this."
        result = fix_initials(input_text, locale)
        assert "Novak. He" in result  # Period followed by space should remain


class TestFixInitialsAdvanced:
    """Advanced tests for initials - multi-initial patterns like F. X. Salda."""

    @pytest.mark.parametrize(("input_text", "expected"), INITIALS_TESTS_ADVANCED.items())
    def test_fix_initials_advanced(self, input_text, expected, locale):
        """Multiple initials before names should have proper nbsp spacing."""
        result = fix_initials(input_text, locale)
        expected_transformed = transform_test_value(expected, locale)
        assert result == expected_transformed


class TestFixSingleWordAbbreviationsFalsePositives:
    """False positive tests - text already processed by multi-word abbr should stay unchanged."""

    @pytest.mark.parametrize(("input_text", "expected"), SINGLE_WORD_ABBREV_FALSE_POSITIVE_TESTS.items())
    def test_false_positives(self, input_text, expected, locale):
        """These patterns should not be modified by single-word abbreviation handling."""
        result = fix_single_word_abbreviations(input_text, locale)
        assert result == expected


class TestFixMultipleWordAbbreviationsAdvanced:
    """Advanced multi-word abbreviation tests - various patterns from JS tests."""

    @pytest.mark.parametrize(("input_text", "expected"), MULTI_WORD_ABBREV_TESTS_ADVANCED.items())
    def test_fix_multiple_word_abbreviations_advanced(self, input_text, expected, locale):
        """Multi-word abbreviations should be properly normalized."""
        result = fix_multiple_word_abbreviations(input_text, locale)
        expected_transformed = transform_test_value(expected, locale)
        assert result == expected_transformed


class TestFixMultipleWordAbbreviationsFalsePositives:
    """False positive tests - patterns that should NOT be modified."""

    @pytest.mark.parametrize(("input_text", "expected"), MULTI_WORD_ABBREV_FALSE_POSITIVE_TESTS.items())
    def test_false_positives(self, input_text, expected, locale):
        """These patterns should not be modified - they are false positives."""
        result = fix_multiple_word_abbreviations(input_text, locale)
        assert result == expected
