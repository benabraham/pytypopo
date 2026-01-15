"""
Fix numero sign (No) spacing.

Port of src/lib/symbols/numero-sign.js from typopo.
"""

from pytypopo.const import NUMERO_SIGN
from pytypopo.modules.symbols.section_sign import fix_spacing_around_symbol


def fix_numero_sign(text, locale):
    """
    Fix spacing around the numero sign (No).

    Ensures proper spacing before and after the numero sign,
    using locale-appropriate spacing after the symbol.

    Args:
        text: Input text to fix
        locale: Locale instance (determines spacing after symbol)

    Returns:
        Text with numero sign spacing fixed
    """
    # Use locale-specific spacing after numero sign
    space_after = locale.space_after_numero_sign

    return fix_spacing_around_symbol(text, NUMERO_SIGN, space_after)
