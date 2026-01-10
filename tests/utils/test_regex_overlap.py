"""
Tests for regex overlap handling utility.

Port of tests/utils/regex-overlap.test.js from typopo.
"""

import re

import pytest

from pytypopo.utils.regex_overlap import replace_with_overlap_handling


class TestBasicFunctionality:
    """Basic non-overlapping replacement scenarios."""

    BASIC_CASES = {
        "hello world hello": "hi world hi",
    }

    @pytest.mark.parametrize(("input_text", "expected"), BASIC_CASES.items())
    def test_simple_non_overlapping_replacements(self, input_text, expected):
        pattern = re.compile(r"hello")
        result = replace_with_overlap_handling(input_text, pattern, "hi")
        assert result == expected

    def test_single_replacement(self):
        pattern = re.compile(r"test")
        result = replace_with_overlap_handling("test string", pattern, "demo")
        assert result == "demo string"

    def test_no_matches_returns_unchanged(self):
        pattern = re.compile(r"xyz")
        result = replace_with_overlap_handling("no matches here", pattern, "replacement")
        assert result == "no matches here"


class TestOverlappingMatches:
    """Tests for overlapping match scenarios - the core functionality."""

    def test_overlapping_dash_patterns_simple(self):
        """1-2-3 should become 1-2-3 (en-dash)."""
        pattern = re.compile(r"(\d)-(\d)")
        result = replace_with_overlap_handling("1-2-3", pattern, r"\1–\2")
        assert result == "1–2–3"

    def test_overlapping_dash_patterns_complex(self):
        """1-2-3-4-5 should become 1-2-3-4-5 (all en-dashes)."""
        pattern = re.compile(r"(\d)-(\d)")
        result = replace_with_overlap_handling("1-2-3-4-5", pattern, r"\1–\2")
        assert result == "1–2–3–4–5"

    def test_overlapping_word_patterns(self):
        """a x b x c should become a*b*c (multiplication signs)."""
        pattern = re.compile(r"(\w) x (\w)")
        result = replace_with_overlap_handling("a x b x c", pattern, r"\1×\2")
        assert result == "a×b×c"  # multiplication sign

    def test_overlapping_with_mixed_patterns(self):
        """Mixed word-dash and number-dash patterns."""
        pattern = re.compile(r"(\w)-(\w)")
        result = replace_with_overlap_handling("word-to-word and 1-2-3 mixed", pattern, r"\1–\2")
        assert result == "word–to–word and 1–2–3 mixed"


class TestMultipleIterationsRequired:
    """Tests for patterns that need multiple passes."""

    def test_patterns_requiring_multiple_passes(self):
        """AAA with AA->B should become BA."""
        pattern = re.compile(r"AA")
        result = replace_with_overlap_handling("AAA", pattern, "B")
        assert result == "BA"

    def test_cascading_replacements(self):
        """AAAA with AA->B should become BB."""
        pattern = re.compile(r"AA")
        result = replace_with_overlap_handling("AAAA", pattern, "B")
        assert result == "BB"

    def test_complex_cascading_pattern(self):
        """AAAAAA with AA->B should become BBB."""
        pattern = re.compile(r"AA")
        result = replace_with_overlap_handling("AAAAAA", pattern, "B")
        assert result == "BBB"


class TestCallableReplacement:
    """Tests for function-based replacement."""

    def test_callable_replacement(self):
        """Function replacement with captured groups."""
        pattern = re.compile(r"test(\d)")

        def replacer(match):
            return f"demo{match.group(1)}"

        result = replace_with_overlap_handling("test1 test2 test3", pattern, replacer)
        assert result == "demo1 demo2 demo3"

    def test_callable_replacement_with_overlaps(self):
        """Function replacement handling overlapping matches."""
        pattern = re.compile(r"(\d)-(\d)")

        def replacer(match):
            return f"{match.group(1)}–{match.group(2)}"

        result = replace_with_overlap_handling("1-2-3", pattern, replacer)
        assert result == "1–2–3"


class TestEdgeCases:
    """Edge case scenarios."""

    def test_empty_string(self):
        pattern = re.compile(r"test")
        result = replace_with_overlap_handling("", pattern, "replacement")
        assert result == ""

    def test_empty_replacement(self):
        pattern = re.compile(r"remove ")
        result = replace_with_overlap_handling("remove this remove that", pattern, "")
        assert result == "this that"

    def test_single_character_patterns(self):
        pattern = re.compile(r"a")
        result = replace_with_overlap_handling("aaaa", pattern, "b")
        assert result == "bbbb"

    def test_special_regex_characters(self):
        pattern = re.compile(r"\.")
        result = replace_with_overlap_handling("a.b.c", pattern, "-")
        assert result == "a-b-c"

    def test_unicode_characters(self):
        pattern = re.compile(r"cafe")
        result = replace_with_overlap_handling("cafe\u2192cafe", pattern, "coffee")
        assert result == "coffee\u2192coffee"

    def test_unicode_with_accents(self):
        pattern = re.compile(r"caf\u00e9")
        result = replace_with_overlap_handling("caf\u00e9\u2192caf\u00e9", pattern, "coffee")
        assert result == "coffee\u2192coffee"


class TestPerformanceAndSafety:
    """Performance and infinite loop prevention tests."""

    def test_patterns_that_converge_quickly(self):
        """Long dash sequences should complete efficiently."""
        pattern = re.compile(r"(\d+)-(\d+)")
        result = replace_with_overlap_handling("1-2-3-4-5-6-7-8-9-10", pattern, r"\1–\2")
        assert result == "1–2–3–4–5–6–7–8–9–10"

    def test_long_strings_efficiently(self):
        """Repeated patterns in long strings should complete."""
        input_text = "a-b-" * 100 + "c"
        pattern = re.compile(r"(\w)-(\w)")
        result = replace_with_overlap_handling(input_text, pattern, r"\1–\2")
        assert "a–b" in result

    def test_prevent_infinite_loops(self):
        """Simple character replacement should not loop."""
        pattern = re.compile(r"t")
        result = replace_with_overlap_handling("test", pattern, "x")
        assert result == "xesx"


class TestRealWorldScenarios:
    """Real-world typography fixing scenarios."""

    def test_typography_dash_fixes(self):
        """Mixed dash styles should be normalized."""
        pattern = re.compile(r"(\d)\s*[-\u2013]\s*(\d)")
        result = replace_with_overlap_handling("1-2-3 and 4 \u2013 5 \u2013 6", pattern, r"\1–\2")
        assert "1–2" in result
        assert "4–5" in result

    def test_multiplication_sign_replacements(self):
        """Dimension notation should use proper multiplication sign."""
        pattern = re.compile(r"(\d+)\s*x\s*(\d+)")
        result = replace_with_overlap_handling("2 x 3 x 4 cm", pattern, r"\1×\2")
        assert result == "2×4 cm" or result == "2×3×4 cm"

    def test_space_normalization(self):
        """Multiple spaces should be normalized to single space."""
        pattern = re.compile(r"\s{2,}")
        result = replace_with_overlap_handling("word  word  word", pattern, " ")
        assert result == "word word word"

    def test_nested_quote_patterns(self):
        """Quote replacement in multiple occurrences."""
        pattern = re.compile(r'"(\w+)"')
        result = replace_with_overlap_handling('"word" "word" "word"', pattern, r'"\1"')
        assert result == '"word" "word" "word"'


class TestBoundaryConditions:
    """Boundary and edge conditions."""

    def test_many_replacements(self):
        """Many single-character replacements."""
        pattern = re.compile(r"A")
        result = replace_with_overlap_handling("A" * 10, pattern, "B")
        assert result == "B" * 10

    def test_multiple_word_replacements(self):
        """Multiple word replacements."""
        pattern = re.compile(r"test")
        result = replace_with_overlap_handling("test test test", pattern, "demo")
        assert result == "demo demo demo"


class TestRegexFlagHandling:
    """Tests for different regex flags."""

    def test_global_replacement(self):
        """All occurrences should be replaced (Python default behavior)."""
        pattern = re.compile(r"test")
        result = replace_with_overlap_handling("test test test", pattern, "demo")
        assert result == "demo demo demo"

    def test_case_insensitive_flag(self):
        """Case-insensitive matching."""
        pattern = re.compile(r"test", re.IGNORECASE)
        result = replace_with_overlap_handling("Test TEST test", pattern, "demo")
        assert result == "demo demo demo"

    def test_multiline_flag(self):
        """Multiline matching with anchors."""
        pattern = re.compile(r"^test$", re.MULTILINE)
        result = replace_with_overlap_handling("line1\ntest\nline3", pattern, "demo")
        assert result == "line1\ndemo\nline3"


class TestOverlappingMultiplicationSign:
    """Specific tests for multiplication sign overlap handling."""

    MULTIPLICATION_CASES = [
        ("2 x 3 x 4", "2×3×4"),
        ("10 x 20 x 30", "10×20×30"),
        ("1x2x3", "1×2×3"),
    ]

    @pytest.mark.parametrize(("input_text", "expected"), MULTIPLICATION_CASES)
    def test_chained_multiplication(self, input_text, expected):
        """Chained multiplication signs should all be replaced."""
        pattern = re.compile(r"(\d+)\s*x\s*(\d+)")
        result = replace_with_overlap_handling(input_text, pattern, r"\1×\2")
        assert result == expected


class TestOverlappingDashSequences:
    """Specific tests for dash sequence overlap handling."""

    DASH_CASES = [
        ("1-2", "1–2"),
        ("1-2-3", "1–2–3"),
        ("1-2-3-4", "1–2–3–4"),
        ("1-2-3-4-5", "1–2–3–4–5"),
        ("10-20-30", "10–20–30"),
    ]

    @pytest.mark.parametrize(("input_text", "expected"), DASH_CASES)
    def test_chained_dashes(self, input_text, expected):
        """Chained dashes should all be converted to en-dashes."""
        pattern = re.compile(r"(\d+)-(\d+)")
        result = replace_with_overlap_handling(input_text, pattern, r"\1–\2")
        assert result == expected
