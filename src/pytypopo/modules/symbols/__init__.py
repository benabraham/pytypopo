"""
Symbol fixing modules.

Handles copyright, trademark, exponents, multiplication signs,
number signs, numero signs, plus-minus, and section signs.
"""

from pytypopo.modules.symbols.copyrights import fix_copyrights
from pytypopo.modules.symbols.exponents import fix_exponents
from pytypopo.modules.symbols.marks import fix_marks
from pytypopo.modules.symbols.multiplication_sign import fix_multiplication_sign
from pytypopo.modules.symbols.number_sign import fix_number_sign, remove_extra_spaces_after_number_sign
from pytypopo.modules.symbols.numero_sign import fix_numero_sign
from pytypopo.modules.symbols.plus_minus import fix_plus_minus
from pytypopo.modules.symbols.section_sign import fix_section_sign

__all__ = [
    "fix_copyrights",
    "fix_exponents",
    "fix_marks",
    "fix_multiplication_sign",
    "fix_number_sign",
    "fix_numero_sign",
    "fix_plus_minus",
    "fix_section_sign",
    "remove_extra_spaces_after_number_sign",
]
