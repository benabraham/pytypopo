"""
Tests for exponent symbol fixes: m2 → m², m3 → m³

Port of tests/symbols/exponents.test.js from typopo.
"""

import pytest

from pytypopo.modules.symbols.exponents import _fix_exponent, fix_exponents

# Test cases for square exponents (²)
# Format: {input: expected_output}
SQUARE_TESTS = {
    # Standard metric prefixes - larger
    "100 m2": "100 m²",
    "100 dam2": "100 dam²",
    "100 hm2": "100 hm²",
    "100 km2": "100 km²",
    "100 Mm2": "100 Mm²",
    "100 Gm2": "100 Gm²",
    "100 Tm2": "100 Tm²",
    "100 Pm2": "100 Pm²",
    "100 Em2": "100 Em²",
    "100 Zm2": "100 Zm²",
    "100 Ym2": "100 Ym²",
    # Standard metric prefixes - smaller
    "100 dm2": "100 dm²",
    "100 cm2": "100 cm²",
    "100 mm2": "100 mm²",
    "100 µm2": "100 µm²",
    "100 nm2": "100 nm²",
    "100 pm2": "100 pm²",
    "100 fm2": "100 fm²",
    "100 am2": "100 am²",
    "100 zm2": "100 zm²",
    "100 ym2": "100 ym²",
    # With units in denominator
    "Holmen 80 g/m2": "Holmen 80 g/m²",
    # False positive - should NOT match within words
    "Madam2": "Madam2",
}


# Test cases for cube exponents (³)
# Format: {input: expected_output}
CUBE_TESTS = {
    # Standard metric prefixes - larger
    "100 m3": "100 m³",
    "100 dam3": "100 dam³",
    "100 hm3": "100 hm³",
    "100 km3": "100 km³",
    "100 Mm3": "100 Mm³",
    "100 Gm3": "100 Gm³",
    "100 Tm3": "100 Tm³",
    "100 Pm3": "100 Pm³",
    "100 Em3": "100 Em³",
    "100 Zm3": "100 Zm³",
    "100 Ym3": "100 Ym³",
    # Standard metric prefixes - smaller
    "100 dm3": "100 dm³",
    "100 cm3": "100 cm³",
    "100 mm3": "100 mm³",
    "100 µm3": "100 µm³",
    "100 nm3": "100 nm³",
    "100 pm3": "100 pm³",
    "100 fm3": "100 fm³",
    "100 am3": "100 am³",
    "100 zm3": "100 zm³",
    "100 ym3": "100 ym³",
    # With units in denominator
    "Holmen 80 g/m3": "Holmen 80 g/m³",
    # False positive - should NOT match within words
    "Madam3": "Madam3",
}


class TestFixSquares:
    """Tests for fixing square exponents: m2 → m²."""

    @pytest.mark.parametrize(("input_text", "expected"), SQUARE_TESTS.items())
    def test_fix_squares(self, input_text, expected, locale):
        """Square exponent 2 should be replaced with ²."""
        result = fix_exponents(input_text, locale)
        assert result == expected


class TestFixCubes:
    """Tests for fixing cube exponents: m3 → m³."""

    @pytest.mark.parametrize(("input_text", "expected"), CUBE_TESTS.items())
    def test_fix_cubes(self, input_text, expected, locale):
        """Cube exponent 3 should be replaced with ³."""
        result = fix_exponents(input_text, locale)
        assert result == expected


# ============================================================================
# Helper function tests (unit tests for internal functions)
# ============================================================================

# Superscript characters
SUPERSCRIPT_TWO = "\u00b2"  # ²
SUPERSCRIPT_THREE = "\u00b3"  # ³


class TestHelperFixExponent:
    """Unit tests for _fix_exponent helper function."""

    @pytest.mark.parametrize(("input_text", "expected"), SQUARE_TESTS.items())
    def test_helper_fix_exponent_squares(self, input_text, expected):
        """Test _fix_exponent with '2' for square exponents."""
        result = _fix_exponent(input_text, "2", SUPERSCRIPT_TWO)
        assert result == expected

    @pytest.mark.parametrize(("input_text", "expected"), CUBE_TESTS.items())
    def test_helper_fix_exponent_cubes(self, input_text, expected):
        """Test _fix_exponent with '3' for cube exponents."""
        result = _fix_exponent(input_text, "3", SUPERSCRIPT_THREE)
        assert result == expected
