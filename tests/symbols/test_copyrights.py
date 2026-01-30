"""
Tests for copyright symbol fixes: (c) → ©, (p) → ℗

Port of tests/symbols/copyrights.test.js from typopo.
"""

import pytest

from pytypopo.const import COPYRIGHT, NBSP, SOUND_RECORDING_COPYRIGHT
from pytypopo.modules.symbols.copyrights import _replace_copyright, fix_copyrights
from tests.conftest import transform_test_value

# Test cases for copyright symbol (©)
# Format: {input: expected_output}
# Note: fix_copyrights adds locale-specific spacing ({copyright_space} token)
COPYRIGHT_TESTS = {
    # Basic replacements - spacing is added after symbol
    "(c)2017": "©{copyright_space}2017",
    "(C)2017": "©{copyright_space}2017",
    # With company name before - space before symbol is added
    "Company (c)2017": "Company ©{copyright_space}2017",
    "Company (C)2017": "Company ©{copyright_space}2017",
    # With space after - spacing is normalized to locale-specific
    "Company(c) 2017": "Company ©{copyright_space}2017",
    "Company(C) 2017": "Company ©{copyright_space}2017",
    # With spaces around - spacing normalized
    "Company (c) 2017": "Company ©{copyright_space}2017",
    "Company (C) 2017": "Company ©{copyright_space}2017",
    # False positives - section references should NOT be replaced
    "Section 7(c)": "Section 7(c)",
    "Section 7(C)": "Section 7(C)",
}


# Test cases for sound recording copyright symbol (℗)
# Format: {input: expected_output}
# Note: fix_copyrights adds locale-specific spacing ({copyright_space} token)
SOUND_RECORDING_COPYRIGHT_TESTS = {
    # Basic replacements - spacing is added after symbol
    "(p)2017": "℗{copyright_space}2017",
    "(P)2017": "℗{copyright_space}2017",
    # With company name before - space before symbol is added
    "Company (p)2017": "Company ℗{copyright_space}2017",
    "Company (P)2017": "Company ℗{copyright_space}2017",
    # With space after - spacing is normalized to locale-specific
    "Company(p) 2017": "Company ℗{copyright_space}2017",
    "Company(P) 2017": "Company ℗{copyright_space}2017",
    # With spaces around - spacing normalized
    "Company (p) 2017": "Company ℗{copyright_space}2017",
    "Company (P) 2017": "Company ℗{copyright_space}2017",
    # False positives - section references should NOT be replaced
    "Section 7(p)": "Section 7(p)",
    "Section 7(P)": "Section 7(P)",
}


class TestFixCopyright:
    """Tests for fixing copyright symbol (c) → ©."""

    @pytest.mark.parametrize(("input_text", "expected"), COPYRIGHT_TESTS.items())
    def test_fix_copyright(self, input_text, expected, locale):
        """Copyright (c) and (C) should be replaced with ©."""
        result = fix_copyrights(input_text, locale)
        expected_transformed = transform_test_value(expected, locale)
        assert result == expected_transformed


class TestFixSoundRecordingCopyright:
    """Tests for fixing sound recording copyright symbol (p) → ℗."""

    @pytest.mark.parametrize(("input_text", "expected"), SOUND_RECORDING_COPYRIGHT_TESTS.items())
    def test_fix_sound_recording_copyright(self, input_text, expected, locale):
        """Sound recording copyright (p) and (P) should be replaced with ℗."""
        result = fix_copyrights(input_text, locale)
        expected_transformed = transform_test_value(expected, locale)
        assert result == expected_transformed


# ============================================================================
# Helper function tests (unit tests for internal functions)
# ============================================================================

# Test data for _replace_copyright helper (no spacing changes, just symbol replacement)
REPLACE_COPYRIGHT_TESTS = {
    "(c)2017": "©2017",
    "(C)2017": "©2017",
    "Company (c)2017": "Company ©2017",
    "Company (C)2017": "Company ©2017",
    "Company(c) 2017": "Company© 2017",
    "Company(C) 2017": "Company© 2017",
    "Company (c) 2017": "Company © 2017",
    "Company (C) 2017": "Company © 2017",
    "Section 7(c)": "Section 7(c)",
    "Section 7(C)": "Section 7(C)",
}

REPLACE_SOUND_RECORDING_COPYRIGHT_TESTS = {
    "(p)2017": "℗2017",
    "(P)2017": "℗2017",
    "Company (p)2017": "Company ℗2017",
    "Company (P)2017": "Company ℗2017",
    "Company(p) 2017": "Company℗ 2017",
    "Company(P) 2017": "Company℗ 2017",
    "Company (p) 2017": "Company ℗ 2017",
    "Company (P) 2017": "Company ℗ 2017",
    "Section 7(p)": "Section 7(p)",
    "Section 7(P)": "Section 7(P)",
}


class TestHelperReplaceCopyright:
    """Unit tests for _replace_copyright helper function."""

    @pytest.mark.parametrize(("input_text", "expected"), REPLACE_COPYRIGHT_TESTS.items())
    def test_helper_replace_copyright_c(self, input_text, expected):
        """Test _replace_copyright with 'c' for copyright symbol."""
        result = _replace_copyright(input_text, "c", COPYRIGHT)
        assert result == expected

    @pytest.mark.parametrize(("input_text", "expected"), REPLACE_SOUND_RECORDING_COPYRIGHT_TESTS.items())
    def test_helper_replace_copyright_p(self, input_text, expected):
        """Test _replace_copyright with 'p' for sound recording copyright symbol."""
        result = _replace_copyright(input_text, "p", SOUND_RECORDING_COPYRIGHT)
        assert result == expected


class TestCzechCopyrightSpacing:
    """Czech locale uses regular space (not NBSP) after copyright symbols."""

    def test_copyright_uses_regular_space_for_czech(self):
        """Czech: © should be followed by regular space, not NBSP."""
        from pytypopo import fix_typos

        result = fix_typos("Company© 2017", "cs")
        # Czech uses regular space, not NBSP
        assert result == "Company © 2017"
        assert NBSP not in result

    def test_sound_recording_copyright_uses_regular_space_for_czech(self):
        """Czech: ℗ should be followed by regular space, not NBSP."""
        from pytypopo import fix_typos

        result = fix_typos("Company℗ 2017", "cs")
        # Czech uses regular space, not NBSP
        assert result == "Company ℗ 2017"
        assert NBSP not in result
