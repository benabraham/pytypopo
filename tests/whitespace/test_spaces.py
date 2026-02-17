"""
Tests for space handling: multiple spaces, tabs, leading/trailing whitespace.

Port of tests/whitespace/spaces.test.js from typopo.
"""

import pytest

from pytypopo.locale import Locale
from pytypopo.modules.whitespace.spaces import (
    add_space_after_closing_brackets,
    add_space_after_sentence_pause,
    add_space_after_terminal_punctuation,
    add_space_before_opening_brackets,
    add_space_before_symbol,
    fix_spaces,
    remove_multiple_spaces,
    remove_space_after_opening_brackets,
    remove_space_before_ordinal_indicator,
    remove_space_before_sentence_pause_punctuation,
    remove_space_before_terminal_punctuation,
    remove_spaces_at_paragraph_beginning,
    remove_spaces_at_paragraph_end,
)

# -------------------------------------------------------------------
# Multiple spaces
# -------------------------------------------------------------------
MULTIPLE_SPACES_TESTS = {
    "How  many spaces": "How many spaces",
    "How   many": "How many",
    "How    many": "How many",
    "How     many": "How many",
    "How       many": "How many",
    "How      many": "How many",
    "How\u00a0     \u00a0many": "How many",  # nbsp mixed in
    "How\u200a     \u200amany": "How many",  # hairSpace mixed in
    "How\u202f     \u202fmany": "How many",  # narrowNbsp mixed in
    "How\u010d     \u010dmany": "How\u010d \u010dmany",  # non-latin character (č)
}


class TestRemoveMultipleSpaces:
    """Tests for collapsing multiple spaces to single space."""

    @pytest.mark.parametrize(("input_text", "expected"), MULTIPLE_SPACES_TESTS.items())
    def test_remove_multiple_spaces(self, input_text, expected, locale):
        """Multiple consecutive spaces should be collapsed to one."""
        result = remove_multiple_spaces(input_text, locale)
        assert result == expected


# -------------------------------------------------------------------
# Spaces at paragraph beginning
# -------------------------------------------------------------------
REMOVE_SPACES_BEFORE_TEXT_TESTS = {
    " What if paragraph starts with extra space at the beginning?": "What if paragraph starts with extra space at the beginning?",
    "  What if paragraph starts with extra space at the beginning?": "What if paragraph starts with extra space at the beginning?",
    "   What if paragraph starts with extra space at the beginning?": "What if paragraph starts with extra space at the beginning?",
    "    What if paragraph starts with extra space at the beginning?": "What if paragraph starts with extra space at the beginning?",
    "\t\t\tWhat if paragraph starts with extra space at the beginning?": "What if paragraph starts with extra space at the beginning?",
    "\t\tWhat if paragraph starts with extra space at the beginning?": "What if paragraph starts with extra space at the beginning?",
    "One sentence ends. And next one continues as it should": "One sentence ends. And next one continues as it should",
    "\t\t\tWhat if sentence starts with tabs?": "What if sentence starts with tabs?",
    "\t\tWhat if sentence starts with tabs?": "What if sentence starts with tabs?",
    "\tWhat if sentence starts with tabs?": "What if sentence starts with tabs?",
    "If there is one line\nand another": "If there is one line\nand another",
}

REMOVE_SPACES_BEFORE_MARKDOWN_LIST_TESTS = {
    " - list": "- list",
    "  - list": "- list",
    "\t- list": "- list",
    "\t\t- list": "- list",
    " * list": "* list",
    "  * list": "* list",
    "\t\t* list": "* list",
    "\t* list": "* list",
    "* list": "* list",
    " + list": "+ list",
    "  + list": "+ list",
    "\t+ list": "+ list",
    "\t\t+ list": "+ list",
    " > list": "> list",
    "  > list": "> list",
    "\t> list": "> list",
    "\t\t> list": "> list",
}


class TestRemoveSpacesAtParagraphBeginning:
    """Tests for removing leading whitespace from paragraphs."""

    @pytest.mark.parametrize(
        ("input_text", "expected"),
        {**REMOVE_SPACES_BEFORE_TEXT_TESTS, **REMOVE_SPACES_BEFORE_MARKDOWN_LIST_TESTS}.items(),
    )
    def test_remove_spaces(self, input_text, expected, locale):
        """Leading spaces should always be removed."""
        result = remove_spaces_at_paragraph_beginning(input_text, locale)
        assert result == expected


# -------------------------------------------------------------------
# Spaces before sentence pause punctuation
# -------------------------------------------------------------------
SPACES_BEFORE_SENTENCE_PAUSE_TESTS = {
    "Hey , man.": "Hey, man.",
    "Hey\u00a0, man.": "Hey, man.",  # nbsp
    "Hey\u200a, man.": "Hey, man.",  # hairSpace
    "Hey\u202f, man.": "Hey, man.",  # narrowNbsp
    "Sentence and\u2026 :": "Sentence and\u2026:",
    "Sentence and\u2026 , else": "Sentence and\u2026, else",
    "Sentence and\u2026 ; else": "Sentence and\u2026; else",
    # False positives - keep space before emoticons
    "Keep space before emoticon :)": "Keep space before emoticon :)",
    "Keep space before emoticon :-)": "Keep space before emoticon :-)",
}


class TestRemoveSpaceBeforeSentencePause:
    """Tests for removing space before commas, colons, semicolons."""

    @pytest.mark.parametrize(("input_text", "expected"), SPACES_BEFORE_SENTENCE_PAUSE_TESTS.items())
    def test_remove_space_before_sentence_pause(self, input_text, expected, locale):
        """Space before , : ; should be removed."""
        result = remove_space_before_sentence_pause_punctuation(input_text, locale)
        assert result == expected


# -------------------------------------------------------------------
# Spaces before terminal punctuation
# -------------------------------------------------------------------
SPACES_BEFORE_TERMINAL_PUNCTUATION_TESTS = {
    "Hey.": "Hey.",
    "Hey .": "Hey.",
    "Hey\u00a0.": "Hey.",  # nbsp
    "Hey\u200a.": "Hey.",  # hairSpace
    "Hey\u202f.": "Hey.",  # narrowNbsp
    "Sentence and\u2026!": "Sentence and\u2026!",
    "Sentence and\u2026 !": "Sentence and\u2026!",
    "Sentence and\u2026?": "Sentence and\u2026?",
    "Sentence and\u2026 ?": "Sentence and\u2026?",
    "Something (\u2026) something else": "Something (\u2026) something else",
    "Something (\u2026 ) something else": "Something (\u2026) something else",
    "Something [\u2026 ] something else": "Something [\u2026] something else",
    "(? )": "(?)",
    "(! )": "(!)",
    "It was good (It was bad !).": "It was good (It was bad!).",
    "5\u00b0": "5\u00b0",
    "5 \u00b0": "5\u00b0",
    "Sentence ended. \u2026and we were there.": "Sentence ended. \u2026and we were there.",
    # False positives - empty brackets should stay
    "[ ]": "[ ]",
    "[\u00a0]": "[\u00a0]",  # nbsp in empty bracket
    "( )": "( )",
    "{ }": "{ }",
}


class TestRemoveSpaceBeforeTerminalPunctuation:
    """Tests for removing space before . ! ? and closing brackets."""

    @pytest.mark.parametrize(("input_text", "expected"), SPACES_BEFORE_TERMINAL_PUNCTUATION_TESTS.items())
    def test_remove_space_before_terminal_punctuation(self, input_text, expected, locale):
        """Space before terminal punctuation should be removed."""
        result = remove_space_before_terminal_punctuation(input_text, locale)
        assert result == expected


# -------------------------------------------------------------------
# Spaces before ordinal indicator
# -------------------------------------------------------------------
ORDINAL_INDICATOR_EN_US_TESTS = {
    "1 st": "1st",
    "2 nd": "2nd",
    "3 rd": "3rd",
    "4 th attempt": "4th attempt",
    "104 th": "104th",
    # False positives
    "Number 4 there you go": "Number 4 there you go",
}

ORDINAL_INDICATOR_OTHER_TESTS = {
    "1 . spoj": "1. spoj",
    "154 . spoj": "154. spoj",
}


class TestRemoveSpaceBeforeOrdinalIndicator:
    """Tests for removing space before ordinal indicator (1st, 2nd, 1.)."""

    @pytest.mark.parametrize(("input_text", "expected"), ORDINAL_INDICATOR_EN_US_TESTS.items())
    def test_ordinal_indicator_en_us(self, input_text, expected):
        """English ordinal indicators: 1st, 2nd, 3rd, 4th."""
        result = remove_space_before_ordinal_indicator(input_text, Locale("en-us"))
        assert result == expected

    @pytest.mark.parametrize(("input_text", "expected"), ORDINAL_INDICATOR_OTHER_TESTS.items())
    @pytest.mark.parametrize("locale_id", ["sk", "cs", "rue", "de-de"])
    def test_ordinal_indicator_other_locales(self, input_text, expected, locale_id):
        """Non-English ordinal indicators: 1. 2. etc."""
        result = remove_space_before_ordinal_indicator(input_text, Locale(locale_id))
        assert result == expected


# -------------------------------------------------------------------
# Spaces after opening brackets
# -------------------------------------------------------------------
SPACES_AFTER_OPENING_BRACKETS_TESTS = {
    "Something ( \u2026) something else": "Something (\u2026) something else",
    "Something [ \u2026] something else": "Something [\u2026] something else",
    "word ( word) word": "word (word) word",
    "( ?)": "(?)",
    "( !)": "(!)",
    "{ !}": "{!}",
    # False positives - empty brackets should stay
    "[ ]": "[ ]",
    "( )": "( )",
    "{ }": "{ }",
}


class TestRemoveSpaceAfterOpeningBrackets:
    """Tests for removing space after opening brackets."""

    @pytest.mark.parametrize(("input_text", "expected"), SPACES_AFTER_OPENING_BRACKETS_TESTS.items())
    def test_remove_space_after_opening_brackets(self, input_text, expected, locale):
        """Space after ( [ { should be removed."""
        result = remove_space_after_opening_brackets(input_text, locale)
        assert result == expected


# -------------------------------------------------------------------
# Spaces before opening brackets
# -------------------------------------------------------------------
SPACES_BEFORE_OPENING_BRACKETS_TESTS = {
    "Enclosed(in) the brackets.": "Enclosed (in) the brackets.",
    "Enclosed[in] the brackets.": "Enclosed [in] the brackets.",
    "quote[\u2026] with parts left out": "quote [\u2026] with parts left out",
    "Enclosed{in} the brackets.": "Enclosed {in} the brackets.",
    # False positives - plurals should NOT get space
    "name(s)": "name(s)",
    "NAME(S)": "NAME(S)",
    "mass(es)": "mass(es)",
    "MASS(ES)": "MASS(ES)",
}


class TestAddSpaceBeforeOpeningBrackets:
    """Tests for adding space before opening brackets."""

    @pytest.mark.parametrize(("input_text", "expected"), SPACES_BEFORE_OPENING_BRACKETS_TESTS.items())
    def test_add_space_before_opening_brackets(self, input_text, expected, locale):
        """Space should be added before opening brackets between words."""
        result = add_space_before_opening_brackets(input_text, locale)
        assert result == expected


# -------------------------------------------------------------------
# Spaces after terminal punctuation
# -------------------------------------------------------------------
SPACES_AFTER_TERMINAL_PUNCTUATION_TESTS = {
    "One sentence ended. Another started.": "One sentence ended. Another started.",
    "One sentence ended.Another started.": "One sentence ended. Another started.",
    "One sentence ended!Another started.": "One sentence ended! Another started.",
    "One sentence ended\u2026!Another started.": "One sentence ended\u2026! Another started.",
    "One sentence ended?Another started.": "One sentence ended? Another started.",
    # False positives - abbreviations, filenames
    "R-N.D.": "R-N.D.",
    "the U.S.": "the U.S.",
    "John Thune (S.D.)": "John Thune (S.D.)",
    "filename.js": "filename.js",
}


class TestAddSpaceAfterTerminalPunctuation:
    """Tests for adding space after . ! ?"""

    @pytest.mark.parametrize(("input_text", "expected"), SPACES_AFTER_TERMINAL_PUNCTUATION_TESTS.items())
    def test_add_space_after_terminal_punctuation(self, input_text, expected, locale):
        """Space should be added after terminal punctuation."""
        result = add_space_after_terminal_punctuation(input_text, locale)
        assert result == expected


# -------------------------------------------------------------------
# Spaces after sentence pause punctuation
# -------------------------------------------------------------------
SPACES_AFTER_SENTENCE_PAUSE_TESTS = {
    "One sentence ended, another started.": "One sentence ended, another started.",
    "One sentence ended,another started.": "One sentence ended, another started.",
    "One sentence ended,John started.": "One sentence ended, John started.",
    "One sentence ended\u2026,John started.": "One sentence ended\u2026, John started.",
    "One sentence ended:another started.": "One sentence ended: another started.",
    "One sentence ended;another started.": "One sentence ended; another started.",
    # False positives - abbreviations, filenames
    "R-N.D.": "R-N.D.",
    "the U.S.": "the U.S.",
    "John Thune (S.D.)": "John Thune (S.D.)",
    "filename.js": "filename.js",
}


class TestAddSpaceAfterSentencePause:
    """Tests for adding space after , : ;"""

    @pytest.mark.parametrize(("input_text", "expected"), SPACES_AFTER_SENTENCE_PAUSE_TESTS.items())
    def test_add_space_after_sentence_pause(self, input_text, expected, locale):
        """Space should be added after sentence pause punctuation."""
        result = add_space_after_sentence_pause(input_text, locale)
        assert result == expected


# -------------------------------------------------------------------
# Spaces after closing brackets
# -------------------------------------------------------------------
SPACES_AFTER_CLOSING_BRACKETS_TESTS = {
    "Enclosed (in) the brackets.": "Enclosed (in) the brackets.",
    "Enclosed (in)the brackets.": "Enclosed (in) the brackets.",
    "Enclosed [in] the brackets.": "Enclosed [in] the brackets.",
    "Enclosed [in]the brackets.": "Enclosed [in] the brackets.",
    "Enclosed {in} the brackets.": "Enclosed {in} the brackets.",
    "Enclosed {in}the brackets.": "Enclosed {in} the brackets.",
    "quote [\u2026]with parts left out": "quote [\u2026] with parts left out",
}


class TestAddSpaceAfterClosingBrackets:
    """Tests for adding space after closing brackets."""

    @pytest.mark.parametrize(("input_text", "expected"), SPACES_AFTER_CLOSING_BRACKETS_TESTS.items())
    def test_add_space_after_closing_brackets(self, input_text, expected, locale):
        """Space should be added after closing brackets before words."""
        result = add_space_after_closing_brackets(input_text, locale)
        assert result == expected


# -------------------------------------------------------------------
# Trailing spaces
# -------------------------------------------------------------------
TRAILING_SPACES_TESTS = {
    "trailing spaces    ": "trailing spaces",
    "trailing spaces\u00a0   ": "trailing spaces",  # includes nbsp
    "trailing spaces\u200a": "trailing spaces",  # hairSpace
    "trailing spaces \u202f": "trailing spaces",  # narrowNbsp
    "trailing spaces\t\t": "trailing spaces",
    "trailing spaces.    ": "trailing spaces.",
    "trailing spaces;    ": "trailing spaces;",
    "first line    \nsecond line  ": "first line\nsecond line",
    "first line    \nsecond line  \nthird line   ": "first line\nsecond line\nthird line",
    "Радостна комната \u2014  ": "Радостна комната \u2014",
}


class TestRemoveTrailingSpaces:
    """Tests for removing trailing whitespace from paragraphs."""

    @pytest.mark.parametrize(("input_text", "expected"), TRAILING_SPACES_TESTS.items())
    def test_remove_trailing_spaces(self, input_text, expected, locale):
        """Trailing spaces should be removed from each line."""
        result = remove_spaces_at_paragraph_end(input_text, locale)
        assert result == expected


# -------------------------------------------------------------------
# Space before symbol
# -------------------------------------------------------------------
SPACES_BEFORE_SYMBOL_TESTS = {
    "\u00a9 2017": "\u00a9 2017",
    "(\u00a9 2017)": "(\u00a9 2017)",
    "Company\u00a9 2017": "Company \u00a9 2017",
    "text.\u00a91": "text. \u00a91",
    "text,\u00a91": "text, \u00a91",
    "text;\u00a91": "text; \u00a91",
    "text:\u00a91": "text: \u00a91",
    "text!\u00a91": "text! \u00a91",
    "text?\u00a91": "text? \u00a91",
    "#\u00a91": "# \u00a91",
    "@\u00a9section": "@ \u00a9section",
    "*\u00a9note": "* \u00a9note",
    "&\u00a9clause": "& \u00a9clause",
    "%\u00a9rate": "% \u00a9rate",
    "$\u00a9cost": "$ \u00a9cost",
    '"text"\u00a91': '"text" \u00a91',
    "'text'\u00a91": "'text' \u00a91",
    "`code`\u00a91": "`code` \u00a91",
    # False positives - brackets
    "(\u00a91)": "(\u00a91)",
    "[\u00a91]": "[\u00a91]",
    "{\u00a91}": "{\u00a91}",
    # Already has space or at start
    "\u00a91 text": "\u00a91 text",
    "text \u00a91111": "text \u00a91111",
}


class TestAddSpaceBeforeSymbol:
    """Tests for adding space before symbols like copyright."""

    @pytest.mark.parametrize(("input_text", "expected"), SPACES_BEFORE_SYMBOL_TESTS.items())
    def test_add_space_before_symbol(self, input_text, expected, locale):
        """Space should be added before symbols when needed."""
        result = add_space_before_symbol(input_text, "\u00a9", locale)
        assert result == expected


# -------------------------------------------------------------------
# Full fix_spaces function
# -------------------------------------------------------------------
FIX_SPACES_TESTS = {
    # Multiple spaces
    "How  many spaces": "How many spaces",
    # Leading whitespace
    " What if paragraph starts with extra space?": "What if paragraph starts with extra space?",
    # Trailing whitespace
    "trailing spaces    ": "trailing spaces",
    # Sentence pause punctuation
    "Hey , man.": "Hey, man.",
    # Terminal punctuation
    "Hey .": "Hey.",
    # Opening brackets
    "word ( word) word": "word (word) word",
    # Terminal punctuation spacing
    "One sentence ended.Another started.": "One sentence ended. Another started.",
    # Closing brackets
    "Enclosed (in)the brackets.": "Enclosed (in) the brackets.",
}


class TestFixSpaces:
    """Integration tests for fix_spaces function."""

    @pytest.mark.parametrize(("input_text", "expected"), FIX_SPACES_TESTS.items())
    def test_fix_spaces(self, input_text, expected, locale):
        """Full fix_spaces should handle all space issues."""
        result = fix_spaces(input_text, locale)
        assert result == expected
