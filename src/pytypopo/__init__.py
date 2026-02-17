"""
pytypopo - Multilingual typography fixer

Python port of typopo (https://github.com/surfinzap/typopo/)
"""

__version__ = "3.0.0+py0"

from pytypopo.locale import get_locale
from pytypopo.modules.punctuation import (
    fix_dash,
    fix_double_quotes,
    fix_ellipsis,
    fix_period,
    fix_single_quotes,
)
from pytypopo.modules.symbols import (
    fix_copyrights,
    fix_exponents,
    fix_marks,
    fix_multiplication_sign,
    fix_number_sign,
    fix_numero_sign,
    fix_plus_minus,
    fix_section_sign,
)
from pytypopo.modules.whitespace import fix_lines, fix_nbsp, fix_spaces
from pytypopo.modules.words import (
    exclude_exceptions,
    fix_abbreviations,
    fix_case,
    fix_pub_id,
    place_exceptions,
)


def fix_typos(
    text,
    locale="en-us",
    *,
    remove_lines=True,
):
    """
    Fix typography issues in text.

    Applies a comprehensive set of typography corrections including:
    - Whitespace normalization (multiple spaces, empty lines)
    - Punctuation fixes (periods, ellipsis, dashes, quotes)
    - Symbol corrections (copyright, trademark, multiplication, etc.)
    - Word-level fixes (abbreviations, accidental caps)
    - Non-breaking space rules (locale-specific)

    The function protects certain patterns from modification:
    - URLs, email addresses, and filenames

    Args:
        text: Input text to fix
        locale: Language locale identifier. Supported values:
            - 'en-us' (English, US) - default
            - 'de-de' (German)
            - 'cs' (Czech)
            - 'sk' (Slovak)
            - 'rue' (Rusyn)
        remove_lines: If True (default), collapse multiple empty lines
            into single newlines. Set to False to preserve line spacing.

    Returns:
        Text with typography fixes applied.

    Examples:
        >>> fix_typos('Hello   world')
        'Hello world'

        >>> fix_typos('Visit http://example.com for info')
        'Visit http://example.com for info'

        >>> fix_typos('First.\\n\\n\\nSecond.', remove_lines=True)
        'First.\\nSecond.'
    """
    # Handle empty or whitespace-only input
    if not text or not text.strip():
        return ""

    # Get locale configuration
    loc = get_locale(locale)

    # Step 1: Exclude exceptions (URLs, emails, filenames)
    # These are replaced with placeholders to protect from modification
    exception_result = exclude_exceptions(text)
    text = exception_result["processed_text"]
    exceptions = exception_result["exceptions"]

    # Step 2: Remove empty lines (optional)
    # Must run early to avoid interfering with other patterns
    if remove_lines:
        text = fix_lines(text, loc)

    # Step 3: Fix ellipsis
    # Must run before space cleanup due to variable spacing in source
    text = fix_ellipsis(text, loc)

    # Step 4: Fix general whitespace (spaces, leading/trailing)
    text = fix_spaces(text, loc)

    # Step 5: Fix punctuation
    # Order: periods, dashes, double quotes, single quotes
    text = fix_period(text, loc)
    text = fix_dash(text, loc)
    text = fix_double_quotes(text, loc)
    text = fix_single_quotes(text, loc)

    # Step 6: Fix symbols
    # Order follows typopo.js: multiplication, section, copyrights,
    # numero, plus-minus, marks, exponents, number sign
    text = fix_multiplication_sign(text, loc)
    text = fix_section_sign(text, loc)
    text = fix_copyrights(text, loc)
    text = fix_numero_sign(text, loc)
    text = fix_plus_minus(text, loc)
    text = fix_marks(text, loc)
    text = fix_exponents(text, loc)
    text = fix_number_sign(text, loc)

    # Step 7: Fix words
    # Order: case, pub_id, abbreviations
    # Note: fix_case and fix_pub_id are locale-independent
    text = fix_case(text)
    text = fix_pub_id(text)
    text = fix_abbreviations(text, loc)

    # Step 8: Apply non-breaking space rules (locale-specific)
    text = fix_nbsp(text, loc)

    # Step 9: Restore exceptions (URLs, emails, filenames)
    text = place_exceptions(text, exceptions)

    return text


__all__ = ["fix_typos", "__version__"]
