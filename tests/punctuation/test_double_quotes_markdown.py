"""Tests for double quotes with markdown code block preservation."""


def test_double_backticks_preserved_with_config():
    """Double backticks should be preserved when keepMarkdownCodeBlocks is True."""
    from pytypopo.locale.base import Locale
    from pytypopo.modules.punctuation.double_quotes import fix_double_quotes_and_primes

    loc = Locale("cs")
    # With keep_markdown_code_blocks=True, backticks should be preserved
    result = fix_double_quotes_and_primes("``code``", loc, keep_markdown_code_blocks=True)
    assert result == "``code``"


def test_double_backticks_replaced_without_config():
    """Double backticks are replaced when keepMarkdownCodeBlocks is False."""
    from pytypopo.locale.base import Locale
    from pytypopo.modules.punctuation.double_quotes import fix_double_quotes_and_primes

    loc = Locale("cs")
    # Without preservation, backticks should be treated as quotes
    result = fix_double_quotes_and_primes("``code``", loc, keep_markdown_code_blocks=False)
    # Should convert to proper quotes
    assert "``" not in result


def test_single_backtick_preserved_with_config():
    """Single backticks should also be preserved."""
    from pytypopo.locale.base import Locale
    from pytypopo.modules.punctuation.double_quotes import fix_double_quotes_and_primes

    loc = Locale("cs")
    # Single backticks for inline code
    result = fix_double_quotes_and_primes("`code`", loc, keep_markdown_code_blocks=True)
    assert result == "`code`"
