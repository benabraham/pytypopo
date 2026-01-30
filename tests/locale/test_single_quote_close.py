"""Test that closing single quote is LEFT SINGLE QUOTE for cs/de-de/sk."""


def test_cs_closing_single_quote_is_left_single_quote():
    from pytypopo.locale.base import Locale

    loc = Locale("cs")
    assert loc.single_quote_close == "\u2018"  # LEFT SINGLE QUOTE


def test_de_de_closing_single_quote_is_left_single_quote():
    from pytypopo.locale.base import Locale

    loc = Locale("de-de")
    assert loc.single_quote_close == "\u2018"  # LEFT SINGLE QUOTE


def test_sk_closing_single_quote_is_left_single_quote():
    from pytypopo.locale.base import Locale

    loc = Locale("sk")
    assert loc.single_quote_close == "\u2018"  # LEFT SINGLE QUOTE
