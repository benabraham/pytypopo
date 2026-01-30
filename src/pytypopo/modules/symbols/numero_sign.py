"""
Fix numero sign (No) spacing.

Port of src/lib/symbols/numero-sign.js from typopo.
"""

from pytypopo.const import NUMERO_SIGN
from pytypopo.locale.base import get_locale
from pytypopo.modules.symbols.section_sign import fix_spacing_around_symbol


def fix_numero_sign(text, locale):
    """
    Fix spacing around the numero sign (No).

    Ensures proper spacing before and after the numero sign,
    using locale-appropriate spacing after the symbol.

    Args:
        text: Input text to fix
        locale: Language locale string or Locale instance (determines spacing after symbol)

    Returns:
        Text with numero sign spacing fixed
    """
    loc = get_locale(locale)
    # Use locale-specific spacing after numero sign
    space_after = loc.space_after_numero_sign

    return fix_spacing_around_symbol(text, NUMERO_SIGN, space_after)
