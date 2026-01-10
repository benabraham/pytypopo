"""
Tests for ellipsis fixes: ... -> ellipsis character, spacing around ellipsis.

Port of tests/punctuation/ellipsis.test.js from typopo.
"""

import pytest

from pytypopo.modules.punctuation.ellipsis import (
    fix_aposiopesis_between_sentences,
    fix_aposiopesis_between_words,
    fix_aposiopesis_ending_paragraph,
    fix_aposiopesis_starting_paragraph,
    fix_aposiopesis_starting_sentence,
    fix_ellipsis,
    fix_ellipsis_as_last_item,
    fix_ellipsis_between_sentences,
    fix_ellipsis_spacing_around_commas,
    replace_three_chars_with_ellipsis,
    replace_two_chars_with_ellipsis,
    replace_two_periods_with_ellipsis,
)

# Character constants for test clarity
ELLIPSIS = "\u2026"
NBSP = "\u00a0"
HAIR_SPACE = "\u200a"
NARROW_NBSP = "\u202f"


class TestReplaceThreeCharsWithEllipsis:
    """Tests for replacing three or more periods/ellipses with single ellipsis."""

    # Tests from JS: singleEllipsisSet
    TESTS = {
        # [1] replace 3 and more dots/ellipses with an ellipsis
        "Sentence ... another sentence": f"Sentence {ELLIPSIS} another sentence",
        "Sentence .... another sentence": f"Sentence {ELLIPSIS} another sentence",
        "Sentence ..... another sentence": f"Sentence {ELLIPSIS} another sentence",
        "Sentence ending...": f"Sentence ending{ELLIPSIS}",
        "Sentence ending....": f"Sentence ending{ELLIPSIS}",
        "Sentence ending.....": f"Sentence ending{ELLIPSIS}",
        f"Sentence ending{ELLIPSIS}.....": f"Sentence ending{ELLIPSIS}",
        f"Sentence ending{ELLIPSIS}.{ELLIPSIS}": f"Sentence ending{ELLIPSIS}",
        f"Sentence ending.{ELLIPSIS}.....": f"Sentence ending{ELLIPSIS}",
    }

    # Tests from JS: singleEllipsisUnitSet (false positives - should NOT change)
    FALSE_POSITIVE_TESTS = {
        "Sentence ending.": "Sentence ending.",
        "Sentence ending..": "Sentence ending..",
    }

    @pytest.mark.parametrize(("input_text", "expected"), TESTS.items())
    def test_replace_three_chars(self, input_text, expected, locale):
        """Three or more periods/ellipses should become single ellipsis."""
        result = replace_three_chars_with_ellipsis(input_text, locale)
        assert result == expected

    @pytest.mark.parametrize(("input_text", "expected"), FALSE_POSITIVE_TESTS.items())
    def test_replace_three_chars_false_positives(self, input_text, expected, locale):
        """One or two periods should NOT be changed."""
        result = replace_three_chars_with_ellipsis(input_text, locale)
        assert result == expected


class TestReplaceTwoCharsWithEllipsis:
    """Tests for replacing two-char ellipsis combinations."""

    # Tests from JS: periodEllipsisComboSet
    TESTS = {
        f"Sentence ending{ELLIPSIS}": f"Sentence ending{ELLIPSIS}",
        f"Sentence ending{ELLIPSIS}{ELLIPSIS}": f"Sentence ending{ELLIPSIS}",
        f"Sentence ending{ELLIPSIS}.": f"Sentence ending{ELLIPSIS}",
        f"Sentence ending.{ELLIPSIS}": f"Sentence ending{ELLIPSIS}",
    }

    @pytest.mark.parametrize(("input_text", "expected"), TESTS.items())
    def test_replace_two_chars(self, input_text, expected, locale):
        """Period+ellipsis or multiple ellipses should become single ellipsis."""
        result = replace_two_chars_with_ellipsis(input_text, locale)
        assert result == expected


class TestReplaceTwoPeriodsWithEllipsis:
    """Tests for two periods between spaces -> ellipsis."""

    # Tests from JS: twoPeriodsBetweenWordsSet
    TESTS = {
        "Sentence .. another sentence": f"Sentence {ELLIPSIS} another sentence",
    }

    @pytest.mark.parametrize(("input_text", "expected"), TESTS.items())
    def test_replace_two_periods(self, input_text, expected, locale):
        """Two periods surrounded by spaces should become ellipsis with spaces."""
        result = replace_two_periods_with_ellipsis(input_text, locale)
        assert result == expected


class TestFixEllipsisSpacingAroundCommas:
    """Tests for ellipsis spacing in comma-ellipsis-comma sequences."""

    # Tests from JS: ellipsisAroundCommasSet
    TESTS = {
        # neutral (already correct)
        f"We sell apples, oranges, {ELLIPSIS}, pens.": f"We sell apples, oranges, {ELLIPSIS}, pens.",
        # Fix spacing
        f"We sell apples, oranges,{ELLIPSIS}, pens.": f"We sell apples, oranges, {ELLIPSIS}, pens.",
        f"We sell apples, oranges,{ELLIPSIS} , pens.": f"We sell apples, oranges, {ELLIPSIS}, pens.",
        f"We sell apples, oranges, {ELLIPSIS} , pens.": f"We sell apples, oranges, {ELLIPSIS}, pens.",
        # nbsp
        f"We sell apples, oranges,{NBSP}{ELLIPSIS}{NBSP}, pens.": f"We sell apples, oranges, {ELLIPSIS}, pens.",
        # hair_space
        f"We sell apples, oranges,{HAIR_SPACE}{ELLIPSIS}{HAIR_SPACE}, pens.": f"We sell apples, oranges, {ELLIPSIS}, pens.",
        # narrow_nbsp
        f"We sell apples, oranges,{NARROW_NBSP}{ELLIPSIS}{NARROW_NBSP}, pens.": f"We sell apples, oranges, {ELLIPSIS}, pens.",
    }

    @pytest.mark.parametrize(("input_text", "expected"), TESTS.items())
    def test_fix_comma_ellipsis_spacing(self, input_text, expected, locale):
        """Ellipsis between commas should have proper spacing."""
        result = fix_ellipsis_spacing_around_commas(input_text, locale)
        assert result == expected


class TestFixEllipsisAsLastItem:
    """Tests for ellipsis as last item in a list (remove space before)."""

    # Tests from JS: ellipsisListItemSet
    TESTS = {
        f"We sell apples, oranges,{ELLIPSIS}": f"We sell apples, oranges,{ELLIPSIS}",
        f"We sell apples, oranges, {ELLIPSIS}": f"We sell apples, oranges,{ELLIPSIS}",
        f"We sell apples, oranges,{ELLIPSIS} ": f"We sell apples, oranges,{ELLIPSIS}",
        f"We sell apples, oranges, {ELLIPSIS} ": f"We sell apples, oranges,{ELLIPSIS}",
        # nbsp (special space before ellipsis, regular space after)
        f"We sell apples, oranges,{NBSP}{ELLIPSIS} ": f"We sell apples, oranges,{ELLIPSIS}",
        # hairSpace (special space before ellipsis, regular space after)
        f"We sell apples, oranges,{HAIR_SPACE}{ELLIPSIS} ": f"We sell apples, oranges,{ELLIPSIS}",
        # narrowNbsp (special space before ellipsis, regular space after)
        f"We sell apples, oranges,{NARROW_NBSP}{ELLIPSIS} ": f"We sell apples, oranges,{ELLIPSIS}",
        # In parentheses
        f"(apples, oranges,{ELLIPSIS})": f"(apples, oranges,{ELLIPSIS})",
        f"(apples, oranges, {ELLIPSIS})": f"(apples, oranges,{ELLIPSIS})",
        f"(apples, oranges, {ELLIPSIS} )": f"(apples, oranges,{ELLIPSIS})",
        f"(apples, oranges,{ELLIPSIS} )": f"(apples, oranges,{ELLIPSIS})",
    }

    # Tests from JS: ellipsisListItemUnitSet (false positives)
    FALSE_POSITIVE_TESTS = {
        # Not at end of list - no change
        f"We sell apples, oranges, {ELLIPSIS}, pens.": f"We sell apples, oranges, {ELLIPSIS}, pens.",
    }

    @pytest.mark.parametrize(("input_text", "expected"), TESTS.items())
    def test_fix_ellipsis_last_item(self, input_text, expected, locale):
        """Ellipsis as last item in list should not have space before it."""
        result = fix_ellipsis_as_last_item(input_text, locale)
        assert result == expected

    @pytest.mark.parametrize(("input_text", "expected"), FALSE_POSITIVE_TESTS.items())
    def test_fix_ellipsis_last_item_false_positives(self, input_text, expected, locale):
        """Ellipsis followed by comma should not be changed."""
        result = fix_ellipsis_as_last_item(input_text, locale)
        assert result == expected


class TestFixAposiopesisStartingParagraph:
    """Tests for aposiopesis (trailing off) at paragraph start."""

    # Tests from JS: aposiopesisParagraphStartSet
    TESTS = {
        # Already correct
        f"{ELLIPSIS}да святить ся": f"{ELLIPSIS}да святить ся",
        # Fix space after ellipsis
        f"{ELLIPSIS} да святить ся": f"{ELLIPSIS}да святить ся",
        # Multiline
        f"{ELLIPSIS} да святить ся\n{ELLIPSIS} multiline test": f"{ELLIPSIS}да святить ся\n{ELLIPSIS}multiline test",
    }

    @pytest.mark.parametrize(("input_text", "expected"), TESTS.items())
    def test_fix_aposiopesis_paragraph_start(self, input_text, expected, locale):
        """Ellipsis at paragraph start should not have trailing space."""
        result = fix_aposiopesis_starting_paragraph(input_text, locale)
        assert result == expected


class TestFixAposiopesisStartingSentence:
    """Tests for aposiopesis at sentence start (after punctuation)."""

    # Tests from JS: aposiopesisSentenceStartSet
    TESTS = {
        # neutral (already correct)
        f"Sentence ended. {ELLIPSIS}and we were there.": f"Sentence ended. {ELLIPSIS}and we were there.",
        # Fix: space after punctuation, none after ellipsis
        f"Sentence ended. {ELLIPSIS} and we were there.": f"Sentence ended. {ELLIPSIS}and we were there.",
        f"Sentence ended.{ELLIPSIS} and we were there.": f"Sentence ended. {ELLIPSIS}and we were there.",
        f"Sentence ended! {ELLIPSIS}and we were there.": f"Sentence ended! {ELLIPSIS}and we were there.",
        f"Sentence ended! {ELLIPSIS} and we were there.": f"Sentence ended! {ELLIPSIS}and we were there.",
        f"Sentence ended!{ELLIPSIS} and we were there.": f"Sentence ended! {ELLIPSIS}and we were there.",
        f"Sentence ended? {ELLIPSIS} and we were there.": f"Sentence ended? {ELLIPSIS}and we were there.",
        # false positive: ellipsis as list item
        f"We sell apples, oranges, {ELLIPSIS}, pens.": f"We sell apples, oranges, {ELLIPSIS}, pens.",
    }

    # Tests from JS: aposiopesisSentenceStartUnitSet (false positives - not fixing space before quotes)
    FALSE_POSITIVE_TESTS = {
        f"'quote' {ELLIPSIS} and we were there.": f"'quote' {ELLIPSIS} and we were there.",
        f"'quote'{ELLIPSIS} and we were there.": f"'quote'{ELLIPSIS} and we were there.",
        f"\u201cquote\u201d{ELLIPSIS} and we were there.": f"\u201cquote\u201d{ELLIPSIS} and we were there.",
    }

    @pytest.mark.parametrize(("input_text", "expected"), TESTS.items())
    def test_fix_aposiopesis_sentence_start(self, input_text, expected, locale):
        """Aposiopesis after sentence end should have no space before lowercase."""
        result = fix_aposiopesis_starting_sentence(input_text, locale)
        assert result == expected

    @pytest.mark.parametrize(("input_text", "expected"), FALSE_POSITIVE_TESTS.items())
    def test_fix_aposiopesis_sentence_start_false_positives(self, input_text, expected, locale):
        """Quotes before ellipsis should not be changed."""
        result = fix_aposiopesis_starting_sentence(input_text, locale)
        assert result == expected


class TestFixAposiopesisBetweenSentences:
    """Tests for aposiopesis between sentences (lowercase ... Uppercase)."""

    # Tests from JS: aposiopesisBetweenSentencesSet
    TESTS = {
        f"Sentence ending{ELLIPSIS} And another starting": f"Sentence ending{ELLIPSIS} And another starting",
        f"Sentence ending {ELLIPSIS} And another starting": f"Sentence ending{ELLIPSIS} And another starting",
        f"Sentence ending {ELLIPSIS}And another starting": f"Sentence ending{ELLIPSIS} And another starting",
    }

    @pytest.mark.parametrize(("input_text", "expected"), TESTS.items())
    def test_fix_aposiopesis_between_sentences(self, input_text, expected, locale):
        """Aposiopesis between sentences should have space after ellipsis."""
        result = fix_aposiopesis_between_sentences(input_text, locale)
        assert result == expected


class TestFixAposiopesisBetweenWords:
    """Tests for aposiopesis between words (word...word -> word... word)."""

    # Tests from JS: aposiopesisBetweenWordsSet
    TESTS = {
        f"word{ELLIPSIS} word": f"word{ELLIPSIS} word",
        f"word{ELLIPSIS}word": f"word{ELLIPSIS} word",
        f"word{ELLIPSIS}Word": f"word{ELLIPSIS} Word",
        f"WORD{ELLIPSIS}WORD": f"WORD{ELLIPSIS} WORD",
    }

    @pytest.mark.parametrize(("input_text", "expected"), TESTS.items())
    def test_fix_aposiopesis_between_words(self, input_text, expected, locale):
        """Ellipsis between words should have space after."""
        result = fix_aposiopesis_between_words(input_text, locale)
        assert result == expected


class TestFixEllipsisBetweenSentences:
    """Tests for ellipsis between sentences (punctuation/quote ... Uppercase)."""

    # Tests from JS: ellipsisBetweenSentencesSet
    TESTS = {
        # Period before ellipsis
        f"What are you saying. {ELLIPSIS} She did not answer.": f"What are you saying. {ELLIPSIS} She did not answer.",
        f"What are you saying. {ELLIPSIS}She did not answer.": f"What are you saying. {ELLIPSIS} She did not answer.",
        f"What are you saying.{ELLIPSIS}She did not answer.": f"What are you saying. {ELLIPSIS} She did not answer.",
        # Exclamation mark before ellipsis
        f"What are you saying! {ELLIPSIS} She did not answer.": f"What are you saying! {ELLIPSIS} She did not answer.",
        f"What are you saying! {ELLIPSIS}She did not answer.": f"What are you saying! {ELLIPSIS} She did not answer.",
        f"What are you saying!{ELLIPSIS}She did not answer.": f"What are you saying! {ELLIPSIS} She did not answer.",
        # Question mark before ellipsis
        f"What are you saying? {ELLIPSIS} She did not answer.": f"What are you saying? {ELLIPSIS} She did not answer.",
        f"What are you saying? {ELLIPSIS}She did not answer.": f"What are you saying? {ELLIPSIS} She did not answer.",
        f"What are you saying?{ELLIPSIS}She did not answer.": f"What are you saying? {ELLIPSIS} She did not answer.",
        # false positive: keep spaces around aposiopesis in the middle of a sentence
        f"Sentence using {ELLIPSIS} aposiopesis in the middle of a sentence.": (
            f"Sentence using {ELLIPSIS} aposiopesis in the middle of a sentence."
        ),
    }

    @pytest.mark.parametrize(("input_text", "expected"), TESTS.items())
    def test_fix_ellipsis_between_sentences(self, input_text, expected, locale):
        """Ellipsis between sentences should have spaces around it."""
        result = fix_ellipsis_between_sentences(input_text, locale)
        assert result == expected


class TestFixEllipsisBetweenSentencesWithQuotes:
    """Tests for ellipsis between sentences with quotes (locale-specific)."""

    # Tests from JS: ellipsisBetweenSentencesUnitSet (quote tests)
    # These use typographic quotes that match en-us/de-de/cs/sk locale's terminal_quotes
    # Note: Uses RIGHT_DOUBLE_QUOTE (") and RIGHT_SINGLE_QUOTE (')
    QUOTE_TESTS = {
        # Already correct
        f"\u2018What are you saying?\u2019 {ELLIPSIS} She did not answer.": (
            f"\u2018What are you saying?\u2019 {ELLIPSIS} She did not answer."
        ),
        # Need space after ellipsis
        f"\u2018What are you saying?\u2019 {ELLIPSIS}She did not answer.": (
            f"\u2018What are you saying?\u2019 {ELLIPSIS} She did not answer."
        ),
        # Need space before and after ellipsis
        f"\u2018What are you saying?\u2019{ELLIPSIS}She did not answer.": (
            f"\u2018What are you saying?\u2019 {ELLIPSIS} She did not answer."
        ),
        f"\u201cWhat are you saying?\u201d{ELLIPSIS}She did not answer.": (
            f"\u201cWhat are you saying?\u201d {ELLIPSIS} She did not answer."
        ),
    }

    # Locales that use RIGHT_DOUBLE_QUOTE and RIGHT_SINGLE_QUOTE as terminal quotes
    SUPPORTED_LOCALES = ["en-us", "de-de", "cs", "sk"]

    @pytest.mark.parametrize(("input_text", "expected"), QUOTE_TESTS.items())
    @pytest.mark.parametrize("locale", SUPPORTED_LOCALES)
    def test_fix_ellipsis_between_sentences_with_quotes(self, input_text, expected, locale):
        """Ellipsis after closing quote should have spaces around it."""
        result = fix_ellipsis_between_sentences(input_text, locale)
        assert result == expected


class TestFixAposiopesisEndingParagraph:
    """Tests for aposiopesis at paragraph end (remove space before ellipsis)."""

    # Tests from JS: aposiopesisEndingParagraphSet
    TESTS = {
        f"Sentence ending{ELLIPSIS}": f"Sentence ending{ELLIPSIS}",
        f"Sentence ending {ELLIPSIS}": f"Sentence ending{ELLIPSIS}",
        f"Sentence ending     {ELLIPSIS}": f"Sentence ending{ELLIPSIS}",
        f"Sentence ending {ELLIPSIS}\nSentence ending {ELLIPSIS}": f"Sentence ending{ELLIPSIS}\nSentence ending{ELLIPSIS}",
    }

    @pytest.mark.parametrize(("input_text", "expected"), TESTS.items())
    def test_fix_aposiopesis_paragraph_end(self, input_text, expected, locale):
        """Aposiopesis at paragraph end should not have space before ellipsis."""
        result = fix_aposiopesis_ending_paragraph(input_text, locale)
        assert result == expected


class TestFixAposiopesisEndingParagraphWithQuotes:
    """Tests for aposiopesis at paragraph end with quotes (locale-specific)."""

    # Tests from JS: aposiopesisEndingParagraphUnitSet (with quotes)
    # These tests use RIGHT_DOUBLE_QUOTE (") and RIGHT_SINGLE_QUOTE (')
    # which are the terminal quotes for en-us, de-de, cs, sk but NOT rue
    QUOTE_TESTS = {
        f"\u201cSentence ending {ELLIPSIS}\u201d": f"\u201cSentence ending{ELLIPSIS}\u201d",
        f"\u2018Sentence ending {ELLIPSIS}\u2019": f"\u2018Sentence ending{ELLIPSIS}\u2019",
    }

    # Locales that use RIGHT_DOUBLE_QUOTE and RIGHT_SINGLE_QUOTE as terminal quotes
    SUPPORTED_LOCALES = ["en-us", "de-de", "cs", "sk"]

    @pytest.mark.parametrize(("input_text", "expected"), QUOTE_TESTS.items())
    @pytest.mark.parametrize("locale", SUPPORTED_LOCALES)
    def test_fix_aposiopesis_paragraph_end_with_quotes(self, input_text, expected, locale):
        """Aposiopesis before closing quote at end should not have space before ellipsis."""
        result = fix_aposiopesis_ending_paragraph(input_text, locale)
        assert result == expected


class TestFixEllipsis:
    """Integration tests for the main fix_ellipsis function."""

    # Combined tests from JS: ellipsisSet (all individual sets merged)
    # This is the exported ellipsisSet from ellipsis.test.js which combines all test sets
    TESTS = {
        # singleEllipsisSet (9 entries)
        "Sentence ... another sentence": f"Sentence {ELLIPSIS} another sentence",
        "Sentence .... another sentence": f"Sentence {ELLIPSIS} another sentence",
        "Sentence ..... another sentence": f"Sentence {ELLIPSIS} another sentence",
        "Sentence ending...": f"Sentence ending{ELLIPSIS}",
        "Sentence ending....": f"Sentence ending{ELLIPSIS}",
        "Sentence ending.....": f"Sentence ending{ELLIPSIS}",
        f"Sentence ending{ELLIPSIS}.....": f"Sentence ending{ELLIPSIS}",
        f"Sentence ending{ELLIPSIS}.{ELLIPSIS}": f"Sentence ending{ELLIPSIS}",
        f"Sentence ending.{ELLIPSIS}.....": f"Sentence ending{ELLIPSIS}",
        # periodEllipsisComboSet (4 entries)
        f"Sentence ending{ELLIPSIS}": f"Sentence ending{ELLIPSIS}",
        f"Sentence ending{ELLIPSIS}{ELLIPSIS}": f"Sentence ending{ELLIPSIS}",
        f"Sentence ending{ELLIPSIS}.": f"Sentence ending{ELLIPSIS}",
        f"Sentence ending.{ELLIPSIS}": f"Sentence ending{ELLIPSIS}",
        # twoPeriodsBetweenWordsSet (1 entry)
        "Sentence .. another sentence": f"Sentence {ELLIPSIS} another sentence",
        # ellipsisAroundCommasSet (7 entries)
        f"We sell apples, oranges, {ELLIPSIS}, pens.": f"We sell apples, oranges, {ELLIPSIS}, pens.",
        f"We sell apples, oranges,{ELLIPSIS}, pens.": f"We sell apples, oranges, {ELLIPSIS}, pens.",
        f"We sell apples, oranges,{ELLIPSIS} , pens.": f"We sell apples, oranges, {ELLIPSIS}, pens.",
        f"We sell apples, oranges, {ELLIPSIS} , pens.": f"We sell apples, oranges, {ELLIPSIS}, pens.",
        f"We sell apples, oranges,{NBSP}{ELLIPSIS}{NBSP}, pens.": f"We sell apples, oranges, {ELLIPSIS}, pens.",
        f"We sell apples, oranges,{HAIR_SPACE}{ELLIPSIS}{HAIR_SPACE}, pens.": f"We sell apples, oranges, {ELLIPSIS}, pens.",
        f"We sell apples, oranges,{NARROW_NBSP}{ELLIPSIS}{NARROW_NBSP}, pens.": f"We sell apples, oranges, {ELLIPSIS}, pens.",
        # ellipsisListItemSet (11 entries)
        f"We sell apples, oranges,{ELLIPSIS}": f"We sell apples, oranges,{ELLIPSIS}",
        f"We sell apples, oranges, {ELLIPSIS}": f"We sell apples, oranges,{ELLIPSIS}",
        f"We sell apples, oranges,{ELLIPSIS} ": f"We sell apples, oranges,{ELLIPSIS}",
        f"We sell apples, oranges, {ELLIPSIS} ": f"We sell apples, oranges,{ELLIPSIS}",
        f"We sell apples, oranges,{NBSP}{ELLIPSIS} ": f"We sell apples, oranges,{ELLIPSIS}",
        f"We sell apples, oranges,{HAIR_SPACE}{ELLIPSIS} ": f"We sell apples, oranges,{ELLIPSIS}",
        f"We sell apples, oranges,{NARROW_NBSP}{ELLIPSIS} ": f"We sell apples, oranges,{ELLIPSIS}",
        f"(apples, oranges,{ELLIPSIS})": f"(apples, oranges,{ELLIPSIS})",
        f"(apples, oranges, {ELLIPSIS})": f"(apples, oranges,{ELLIPSIS})",
        f"(apples, oranges, {ELLIPSIS} )": f"(apples, oranges,{ELLIPSIS})",
        f"(apples, oranges,{ELLIPSIS} )": f"(apples, oranges,{ELLIPSIS})",
        # aposiopesisParagraphStartSet (3 entries)
        f"{ELLIPSIS}да святить ся": f"{ELLIPSIS}да святить ся",
        f"{ELLIPSIS} да святить ся": f"{ELLIPSIS}да святить ся",
        f"{ELLIPSIS} да святить ся\n{ELLIPSIS} multiline test": f"{ELLIPSIS}да святить ся\n{ELLIPSIS}multiline test",
        # aposiopesisSentenceStartSet (8 entries)
        f"Sentence ended. {ELLIPSIS}and we were there.": f"Sentence ended. {ELLIPSIS}and we were there.",
        f"Sentence ended. {ELLIPSIS} and we were there.": f"Sentence ended. {ELLIPSIS}and we were there.",
        f"Sentence ended.{ELLIPSIS} and we were there.": f"Sentence ended. {ELLIPSIS}and we were there.",
        f"Sentence ended! {ELLIPSIS}and we were there.": f"Sentence ended! {ELLIPSIS}and we were there.",
        f"Sentence ended! {ELLIPSIS} and we were there.": f"Sentence ended! {ELLIPSIS}and we were there.",
        f"Sentence ended!{ELLIPSIS} and we were there.": f"Sentence ended! {ELLIPSIS}and we were there.",
        f"Sentence ended? {ELLIPSIS} and we were there.": f"Sentence ended? {ELLIPSIS}and we were there.",
        # aposiopesisBetweenSentencesSet (3 entries)
        f"Sentence ending{ELLIPSIS} And another starting": f"Sentence ending{ELLIPSIS} And another starting",
        f"Sentence ending {ELLIPSIS} And another starting": f"Sentence ending{ELLIPSIS} And another starting",
        f"Sentence ending {ELLIPSIS}And another starting": f"Sentence ending{ELLIPSIS} And another starting",
        # aposiopesisBetweenWordsSet (4 entries)
        f"word{ELLIPSIS} word": f"word{ELLIPSIS} word",
        f"word{ELLIPSIS}word": f"word{ELLIPSIS} word",
        f"word{ELLIPSIS}Word": f"word{ELLIPSIS} Word",
        f"WORD{ELLIPSIS}WORD": f"WORD{ELLIPSIS} WORD",
        # ellipsisBetweenSentencesSet (10 entries)
        f"What are you saying. {ELLIPSIS} She did not answer.": f"What are you saying. {ELLIPSIS} She did not answer.",
        f"What are you saying. {ELLIPSIS}She did not answer.": f"What are you saying. {ELLIPSIS} She did not answer.",
        f"What are you saying.{ELLIPSIS}She did not answer.": f"What are you saying. {ELLIPSIS} She did not answer.",
        f"What are you saying! {ELLIPSIS} She did not answer.": f"What are you saying! {ELLIPSIS} She did not answer.",
        f"What are you saying! {ELLIPSIS}She did not answer.": f"What are you saying! {ELLIPSIS} She did not answer.",
        f"What are you saying!{ELLIPSIS}She did not answer.": f"What are you saying! {ELLIPSIS} She did not answer.",
        f"What are you saying? {ELLIPSIS} She did not answer.": f"What are you saying? {ELLIPSIS} She did not answer.",
        f"What are you saying? {ELLIPSIS}She did not answer.": f"What are you saying? {ELLIPSIS} She did not answer.",
        f"What are you saying?{ELLIPSIS}She did not answer.": f"What are you saying? {ELLIPSIS} She did not answer.",
        f"Sentence using {ELLIPSIS} aposiopesis in the middle of a sentence.": (
            f"Sentence using {ELLIPSIS} aposiopesis in the middle of a sentence."
        ),
        # aposiopesisEndingParagraphSet (3 entries - 1 duplicate removed)
        f"Sentence ending {ELLIPSIS}": f"Sentence ending{ELLIPSIS}",
        f"Sentence ending     {ELLIPSIS}": f"Sentence ending{ELLIPSIS}",
        f"Sentence ending {ELLIPSIS}\nSentence ending {ELLIPSIS}": f"Sentence ending{ELLIPSIS}\nSentence ending{ELLIPSIS}",
    }

    @pytest.mark.parametrize(("input_text", "expected"), TESTS.items())
    def test_fix_ellipsis_integration(self, input_text, expected, locale):
        """Main fix_ellipsis should handle all ellipsis cases."""
        result = fix_ellipsis(input_text, locale)
        assert result == expected


class TestFixEllipsisWithQuotes:
    """Integration tests for fix_ellipsis with locale-specific quotes.

    These tests combine aposiopesisEndingParagraphUnitSet and ellipsisBetweenSentencesUnitSet
    that use RIGHT_DOUBLE_QUOTE (") and RIGHT_SINGLE_QUOTE (') which are terminal quotes
    for en-us, de-de, cs, sk but NOT rue.
    """

    # Tests from JS: aposiopesisEndingParagraphUnitSet (2 entries)
    ENDING_PARAGRAPH_QUOTE_TESTS = {
        f"\u201cSentence ending {ELLIPSIS}\u201d": f"\u201cSentence ending{ELLIPSIS}\u201d",
        f"\u2018Sentence ending {ELLIPSIS}\u2019": f"\u2018Sentence ending{ELLIPSIS}\u2019",
    }

    # Tests from JS: ellipsisBetweenSentencesUnitSet (4 entries)
    BETWEEN_SENTENCES_QUOTE_TESTS = {
        f"\u2018What are you saying?\u2019 {ELLIPSIS} She did not answer.": (
            f"\u2018What are you saying?\u2019 {ELLIPSIS} She did not answer."
        ),
        f"\u2018What are you saying?\u2019 {ELLIPSIS}She did not answer.": (
            f"\u2018What are you saying?\u2019 {ELLIPSIS} She did not answer."
        ),
        f"\u2018What are you saying?\u2019{ELLIPSIS}She did not answer.": (
            f"\u2018What are you saying?\u2019 {ELLIPSIS} She did not answer."
        ),
        f"\u201cWhat are you saying?\u201d{ELLIPSIS}She did not answer.": (
            f"\u201cWhat are you saying?\u201d {ELLIPSIS} She did not answer."
        ),
    }

    # Locales that use RIGHT_DOUBLE_QUOTE and RIGHT_SINGLE_QUOTE as terminal quotes
    SUPPORTED_LOCALES = ["en-us", "de-de", "cs", "sk"]

    @pytest.mark.parametrize(("input_text", "expected"), ENDING_PARAGRAPH_QUOTE_TESTS.items())
    @pytest.mark.parametrize("locale", SUPPORTED_LOCALES)
    def test_fix_ellipsis_ending_paragraph_with_quotes(self, input_text, expected, locale):
        """fix_ellipsis should handle aposiopesis ending paragraph inside quotes."""
        result = fix_ellipsis(input_text, locale)
        assert result == expected

    @pytest.mark.parametrize(("input_text", "expected"), BETWEEN_SENTENCES_QUOTE_TESTS.items())
    @pytest.mark.parametrize("locale", SUPPORTED_LOCALES)
    def test_fix_ellipsis_between_sentences_with_quotes(self, input_text, expected, locale):
        """fix_ellipsis should handle ellipsis between sentences after closing quotes."""
        result = fix_ellipsis(input_text, locale)
        assert result == expected
