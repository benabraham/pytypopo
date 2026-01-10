"""
Fix numero sign (No) spacing.

Port of src/lib/symbols/numero-sign.js from typopo.
"""

from pytypopo.const import NARROW_NBSP, NUMERO_SIGN
from pytypopo.modules.symbols.section_sign import fix_spacing_around_symbol


def fix_numero_sign(text, locale):
    """
    Fix spacing around the numero sign (No).

    Ensures proper spacing before and after the numero sign,
    using locale-appropriate spacing after the symbol.

    Args:
        text: Input text to fix
        locale: Language locale (determines spacing after symbol)

    Returns:
        Text with numero sign spacing fixed
    """
    # For all locales, use narrow nbsp after numero sign
    space_after = NARROW_NBSP

    return fix_spacing_around_symbol(text, NUMERO_SIGN, space_after)
