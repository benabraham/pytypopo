"""
Tests for publication identifier formatting (ISBN, ISSN).

Port of tests/words/pub-id.test.js from typopo.
"""

import pytest

from pytypopo.const import NBSP
from pytypopo.modules.words.pub_id import (
    fix_isbn10,
    fix_isbn13,
    fix_isbn_number,
    fix_issn,
    fix_pub_id,
)

# Test cases for ISSN formatting
# ISSN format: ISSN XXXX-XXXX (8 digits with hyphen in middle)
# From JS: issnSet
ISSN_TESTS = {
    # From JS tests
    "ISSN 0000 - 0000": f"ISSN{NBSP}0000-0000",
    "Issn 0000 - 0000": f"ISSN{NBSP}0000-0000",
    "issn 0000 - 0000": f"ISSN{NBSP}0000-0000",
    "ISSN 0000—0000": f"ISSN{NBSP}0000-0000",  # em-dash
    "ISSN: 0000 - 0000": f"ISSN:{NBSP}0000-0000",
    "ISSN:0000 - 0000": f"ISSN:{NBSP}0000-0000",
    # Additional edge cases
    "ISSN 0000-0000": f"ISSN{NBSP}0000-0000",  # already correct spacing
    "issn 0000-0000": f"ISSN{NBSP}0000-0000",  # lowercase
    "ISSN: 0000-0000": f"ISSN:{NBSP}0000-0000",  # with colon
    "ISSN 0000 – 0000": f"ISSN{NBSP}0000-0000",  # en-dash
    # Real ISSN examples
    "ISSN 1234-5678": f"ISSN{NBSP}1234-5678",
    "ISSN 2049-3630": f"ISSN{NBSP}2049-3630",
}

# Test cases for ISBN-10 formatting
# ISBN-10 format: ISBN X-XXX-XXXXX-X (10 digits with 3 hyphens)
# From JS: isbn10Set
ISBN10_TESTS = {
    # From JS tests
    "ISBN 80 - 902734 - 1 - 6": f"ISBN{NBSP}80-902734-1-6",
    "Isbn 80 - 902734 - 1 - 6": f"ISBN{NBSP}80-902734-1-6",
    "isbn 80 - 902734 - 1 - 6": f"ISBN{NBSP}80-902734-1-6",
    "ISBN 80—902734—1—6": f"ISBN{NBSP}80-902734-1-6",  # em-dash
    "ISBN: 80 - 902734 - 1 - 6": f"ISBN:{NBSP}80-902734-1-6",
    "ISBN:80 - 902734 - 1 - 6": f"ISBN:{NBSP}80-902734-1-6",
    "ISBN:0-9752298-0-X": f"ISBN:{NBSP}0-9752298-0-X",  # with X check digit
    # Additional edge cases
    "ISBN 80-902734-1-6": f"ISBN{NBSP}80-902734-1-6",  # already correct
    "isbn 80-902734-1-6": f"ISBN{NBSP}80-902734-1-6",
    "ISBN: 80-902734-1-6": f"ISBN:{NBSP}80-902734-1-6",
    "ISBN 80 – 902734 – 1 – 6": f"ISBN{NBSP}80-902734-1-6",  # en-dash
    # With X check digit
    "ISBN 0-596-52068-9": f"ISBN{NBSP}0-596-52068-9",
    "ISBN 0 - 596 - 52068 - X": f"ISBN{NBSP}0-596-52068-X",
}

# Test cases for ISBN-13 formatting
# ISBN-13 format: ISBN XXX-X-XXX-XXXXX-X (13 digits with 4 hyphens)
# From JS: isbn13Set
ISBN13_TESTS = {
    # From JS tests
    "ISBN 978 - 80 - 902734 - 1 - 6": f"ISBN{NBSP}978-80-902734-1-6",
    "Isbn 978 - 80 - 902734 - 1 - 6": f"ISBN{NBSP}978-80-902734-1-6",
    "isbn 978 - 80 - 902734 - 1 - 6": f"ISBN{NBSP}978-80-902734-1-6",
    "ISBN 978 - 80—902734—1—6": f"ISBN{NBSP}978-80-902734-1-6",  # mixed em-dash
    "ISBN: 978 - 80 - 902734 - 1 - 6": f"ISBN:{NBSP}978-80-902734-1-6",
    "ISBN:978 - 80 - 902734 - 1 - 6": f"ISBN:{NBSP}978-80-902734-1-6",
    "ISBN:978 - 0-9752298-0-X": f"ISBN:{NBSP}978-0-9752298-0-X",  # with X check digit
    # Additional edge cases
    "ISBN 978-80-902734-1-6": f"ISBN{NBSP}978-80-902734-1-6",
    "isbn 978-80-902734-1-6": f"ISBN{NBSP}978-80-902734-1-6",
    "ISBN: 978-80-902734-1-6": f"ISBN:{NBSP}978-80-902734-1-6",
    "ISBN 978 – 80 – 902734 – 1 – 6": f"ISBN{NBSP}978-80-902734-1-6",  # en-dash
    # Real examples
    "ISBN 978-0-596-52068-7": f"ISBN{NBSP}978-0-596-52068-7",
    "ISBN 978-3-16-148410-0": f"ISBN{NBSP}978-3-16-148410-0",
}

# Test cases for bare ISBN numbers (without ISBN prefix)
# From JS: isbnNumberSet
ISBN_NUMBER_TESTS = {
    # From JS tests
    "978 - 80 - 902734 - 1 - 6": "978-80-902734-1-6",
    "978- 80- 902734- 1- 6": "978-80-902734-1-6",
    "978 -80 -902734 -1 -6": "978-80-902734-1-6",
    "978 - 80—902734—1—6": "978-80-902734-1-6",  # mixed em-dash
    "978 - 0-9752298-0-X": "978-0-9752298-0-X",  # with X check digit
    "978 - 99921 - 58 - 10 - 7": "978-99921-58-10-7",
    "978 - 9971 - 5 - 0210 - 0": "978-9971-5-0210-0",
    "978 - 960 - 425 - 059 - 0": "978-960-425-059-0",
    "978 - 85 - 359 - 0277 - 5": "978-85-359-0277-5",
    "978 - 1 - 84356 - 028 - 3": "978-1-84356-028-3",
    "978 - 0 - 684 - 84328 - 5": "978-0-684-84328-5",
    "978 - 0 - 8044 - 2957 - X": "978-0-8044-2957-X",
    "978 - 0 - 85131 - 041 - 9": "978-0-85131-041-9",
    "978 - 93 - 86954 - 21 - 4": "978-93-86954-21-4",
    "978 - 0 - 943396 - 04 - 2": "978-0-943396-04-2",
    "978 - 0 - 9752298 - 0 - X": "978-0-9752298-0-X",
    # Already correct
    "978-80-902734-1-6": "978-80-902734-1-6",
    "978 – 80 – 902734 – 1 – 6": "978-80-902734-1-6",  # en-dash
    # International examples
    "978-0-596-52068-7": "978-0-596-52068-7",
    "978 - 0 - 596 - 52068 - 7": "978-0-596-52068-7",
    "978-3-16-148410-0": "978-3-16-148410-0",
    # With X check digit
    "978-80-902734-1-X": "978-80-902734-1-X",
    "979-10-90636-07-1": "979-10-90636-07-1",
}


class TestFixISSN:
    """Tests for ISSN formatting."""

    @pytest.mark.parametrize(("input_text", "expected"), ISSN_TESTS.items())
    def test_fix_issn(self, input_text, expected):
        """ISSN should be properly formatted with nbsp and correct hyphen."""
        result = fix_issn(input_text)
        assert result == expected


class TestFixISBN10:
    """Tests for ISBN-10 formatting."""

    @pytest.mark.parametrize(("input_text", "expected"), ISBN10_TESTS.items())
    def test_fix_isbn10(self, input_text, expected):
        """ISBN-10 should be properly formatted with nbsp and hyphens."""
        result = fix_isbn10(input_text)
        assert result == expected


class TestFixISBN13:
    """Tests for ISBN-13 formatting."""

    @pytest.mark.parametrize(("input_text", "expected"), ISBN13_TESTS.items())
    def test_fix_isbn13(self, input_text, expected):
        """ISBN-13 should be properly formatted with nbsp and hyphens."""
        result = fix_isbn13(input_text)
        assert result == expected


class TestFixISBNNumber:
    """Tests for bare ISBN number formatting."""

    @pytest.mark.parametrize(("input_text", "expected"), ISBN_NUMBER_TESTS.items())
    def test_fix_isbn_number(self, input_text, expected):
        """Bare ISBN numbers should have consistent hyphen formatting."""
        result = fix_isbn_number(input_text)
        assert result == expected


class TestFixPubId:
    """Tests for the combined fix_pub_id function."""

    def test_fix_issn_via_pub_id(self):
        """ISSN should be fixed via the main function."""
        result = fix_pub_id("ISSN 1234-5678")
        assert result == f"ISSN{NBSP}1234-5678"

    def test_fix_isbn10_via_pub_id(self):
        """ISBN-10 should be fixed via the main function."""
        result = fix_pub_id("ISBN 80-902734-1-6")
        assert result == f"ISBN{NBSP}80-902734-1-6"

    def test_fix_isbn13_via_pub_id(self):
        """ISBN-13 should be fixed via the main function."""
        result = fix_pub_id("ISBN 978-80-902734-1-6")
        assert result == f"ISBN{NBSP}978-80-902734-1-6"

    def test_fix_multiple_pub_ids(self):
        """Multiple publication IDs in text should all be fixed."""
        input_text = "See ISSN 1234-5678 and ISBN 978-80-902734-1-6."
        expected = f"See ISSN{NBSP}1234-5678 and ISBN{NBSP}978-80-902734-1-6."
        result = fix_pub_id(input_text)
        assert result == expected

    def test_no_change_on_regular_text(self):
        """Regular text should not be affected."""
        text = "This is regular text without any publication IDs."
        assert fix_pub_id(text) == text

    def test_empty_string(self):
        """Empty string should remain empty."""
        assert fix_pub_id("") == ""
