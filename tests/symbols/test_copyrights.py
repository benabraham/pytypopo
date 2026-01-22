"""
Tests for copyright symbol fixes: (c) → ©, (p) → ℗

Port of tests/symbols/copyrights.test.js from typopo.
"""

import pytest

from pytypopo.const import COPYRIGHT, NBSP, SOUND_RECORDING_COPYRIGHT
from pytypopo.modules.symbols.copyrights import _replace_copyright, fix_copyrights

# Test cases for copyright symbol (©)
# Format: {input: expected_output}
# Note: fix_copyrights now adds locale-specific spacing (NBSP for all locales)
COPYRIGHT_TESTS = {
    # Basic replacements - spacing is added after symbol
    "(c)2017": f"©{NBSP}2017",
    "(C)2017": f"©{NBSP}2017",
    # With company name before - space before symbol is added
    "Company (c)2017": f"Company ©{NBSP}2017",
    "Company (C)2017": f"Company ©{NBSP}2017",
    # With space after - spacing is normalized to nbsp
    "Company(c) 2017": f"Company ©{NBSP}2017",
    "Company(C) 2017": f"Company ©{NBSP}2017",
    # With spaces around - spacing normalized
    "Company (c) 2017": f"Company ©{NBSP}2017",
    "Company (C) 2017": f"Company ©{NBSP}2017",
    # False positives - section references should NOT be replaced
    "Section 7(c)": "Section 7(c)",
    "Section 7(C)": "Section 7(C)",
}


# Test cases for sound recording copyright symbol (℗)
# Format: {input: expected_output}
# Note: fix_copyrights now adds locale-specific spacing (NBSP for all locales)
SOUND_RECORDING_COPYRIGHT_TESTS = {
    # Basic replacements - spacing is added after symbol
    "(p)2017": f"℗{NBSP}2017",
    "(P)2017": f"℗{NBSP}2017",
    # With company name before - space before symbol is added
    "Company (p)2017": f"Company ℗{NBSP}2017",
    "Company (P)2017": f"Company ℗{NBSP}2017",
    # With space after - spacing is normalized to nbsp
    "Company(p) 2017": f"Company ℗{NBSP}2017",
    "Company(P) 2017": f"Company ℗{NBSP}2017",
    # With spaces around - spacing normalized
    "Company (p) 2017": f"Company ℗{NBSP}2017",
    "Company (P) 2017": f"Company ℗{NBSP}2017",
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
        assert result == expected


class TestFixSoundRecordingCopyright:
    """Tests for fixing sound recording copyright symbol (p) → ℗."""

    @pytest.mark.parametrize(("input_text", "expected"), SOUND_RECORDING_COPYRIGHT_TESTS.items())
    def test_fix_sound_recording_copyright(self, input_text, expected, locale):
        """Sound recording copyright (p) and (P) should be replaced with ℗."""
        result = fix_copyrights(input_text, locale)
        assert result == expected


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
