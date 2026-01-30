"""Tests for regnal number NBSP handling across locales."""


def test_nbsp_for_name_with_regnal_number_en_us():
    """en-us should add nbsp between name and roman numeral even without ordinal indicator."""
    from pytypopo.locale.base import Locale
    from pytypopo.modules.whitespace.nbsp import fix_nbsp

    loc = Locale("en-us")
    # Should add nbsp between name and roman numeral
    assert fix_nbsp("Karel IV", loc) == "Karel\u00a0IV"
    assert fix_nbsp("Henry VIII", loc) == "Henry\u00a0VIII"
    assert fix_nbsp("Louis XIV", loc) == "Louis\u00a0XIV"


def test_nbsp_for_name_with_regnal_number_cs():
    """cs locale should handle regnal numbers with ordinal indicator."""
    from pytypopo.locale.base import Locale
    from pytypopo.modules.whitespace.nbsp import fix_nbsp

    loc = Locale("cs")
    # Czech uses . as ordinal indicator
    assert fix_nbsp("Karel IV.", loc) == "Karel\u00a0IV."


def test_nbsp_for_name_with_regnal_number_de():
    """de-de locale should handle regnal numbers with ordinal indicator."""
    from pytypopo.locale.base import Locale
    from pytypopo.modules.whitespace.nbsp import fix_nbsp

    loc = Locale("de-de")
    # German uses . as ordinal indicator
    assert fix_nbsp("Heinrich VIII.", loc) == "Heinrich\u00a0VIII."
