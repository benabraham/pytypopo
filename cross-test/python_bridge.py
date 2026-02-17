#!/usr/bin/env python3
"""
HTTP bridge for JS test suite to call pytypopo functions.

Exposes all pytypopo functions via HTTP POST for cross-testing
against the upstream typopo JavaScript test suite.

Usage: python python_bridge.py [port]
Default port: 9876
"""

import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

# Add src to path for development
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pytypopo import fix_typos
from pytypopo.locale import get_locale

# Punctuation modules
from pytypopo.modules.punctuation.dash import (
    fix_dash,
    fix_dash_between_cardinal_numbers,
    fix_dash_between_ordinal_numbers,
    fix_dash_between_percentage_range,
    fix_dash_between_word_and_brackets,
    fix_dash_between_word_and_punctuation,
    fix_dashes_between_words,
)
from pytypopo.modules.punctuation.double_quotes import fix_double_quotes_and_primes
from pytypopo.modules.punctuation.ellipsis import (
    fix_ellipsis,
    replace_three_chars_with_ellipsis,
)
from pytypopo.modules.punctuation.period import fix_period
from pytypopo.modules.punctuation.single_quotes import fix_single_quotes_primes_and_apostrophes

# Symbol modules
from pytypopo.modules.symbols.copyrights import fix_copyrights
from pytypopo.modules.symbols.exponents import fix_exponents
from pytypopo.modules.symbols.marks import fix_marks
from pytypopo.modules.symbols.multiplication_sign import fix_multiplication_sign
from pytypopo.modules.symbols.number_sign import fix_number_sign
from pytypopo.modules.symbols.numero_sign import fix_numero_sign
from pytypopo.modules.symbols.plus_minus import fix_plus_minus
from pytypopo.modules.symbols.section_sign import fix_section_sign

# Whitespace modules
from pytypopo.modules.whitespace.lines import fix_lines
from pytypopo.modules.whitespace.nbsp import fix_nbsp
from pytypopo.modules.whitespace.spaces import fix_spaces

# Word modules
from pytypopo.modules.words.abbreviations import (
    fix_abbreviations,
    fix_initials,
    fix_multiple_word_abbreviations,
    fix_single_word_abbreviations,
)
from pytypopo.modules.words.case import fix_case
from pytypopo.modules.words.exceptions import exclude_exceptions, place_exceptions
from pytypopo.modules.words.pub_id import fix_pub_id

# Map JS function names (camelCase) to Python functions
# Format: 'jsFunctionName': (python_func, needs_locale)
FUNCTION_MAP = {
    # Main API
    "fixTypos": (fix_typos, True),
    # Punctuation - dash
    "fixDash": (fix_dash, True),
    "fixDashesBetweenWords": (fix_dashes_between_words, True),
    "fixDashBetweenWordAndPunctuation": (fix_dash_between_word_and_punctuation, True),
    "fixDashBetweenWordAndBrackets": (fix_dash_between_word_and_brackets, True),
    "fixDashBetweenCardinalNumbers": (fix_dash_between_cardinal_numbers, False),
    "fixDashBetweenPercentageRange": (fix_dash_between_percentage_range, False),
    "fixDashBetweenOrdinalNumbers": (fix_dash_between_ordinal_numbers, True),
    # Punctuation - other
    "fixDoubleQuotes": (fix_double_quotes_and_primes, True),
    "fixDoubleQuotesAndPrimes": (fix_double_quotes_and_primes, True),
    "fixSingleQuotes": (fix_single_quotes_primes_and_apostrophes, True),
    "fixSingleQuotesPrimesAndApostrophes": (fix_single_quotes_primes_and_apostrophes, True),
    "fixEllipsis": (fix_ellipsis, True),
    "replaceThreeCharsWithEllipsis": (replace_three_chars_with_ellipsis, False),
    "fixPeriod": (fix_period, True),
    # Symbols
    "fixCopyrights": (fix_copyrights, True),
    "fixExponents": (fix_exponents, True),
    "fixMarks": (fix_marks, True),
    "fixMultiplicationSign": (fix_multiplication_sign, True),
    "fixNumberSign": (fix_number_sign, True),
    "fixNumeroSign": (fix_numero_sign, True),
    "fixPlusMinus": (fix_plus_minus, True),
    "fixSectionSign": (fix_section_sign, True),
    # Whitespace
    "fixLines": (fix_lines, True),
    "fixNbsp": (fix_nbsp, True),
    "fixSpaces": (fix_spaces, True),
    # Words
    "fixAbbreviations": (fix_abbreviations, True),
    "fixInitials": (fix_initials, True),
    "fixSingleWordAbbreviations": (fix_single_word_abbreviations, True),
    "fixMultipleWordAbbreviations": (fix_multiple_word_abbreviations, True),
    "fixCase": (fix_case, False),
    "fixPubId": (fix_pub_id, False),
    # Exceptions
    "excludeExceptions": (exclude_exceptions, False),
    "placeExceptions": (place_exceptions, False),
}


class BridgeHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress default logging for cleaner output
        pass

    def do_POST(self):
        try:
            content_length = int(self.headers["Content-Length"])
            body = json.loads(self.rfile.read(content_length))

            func_name = body["function"]
            text = body["text"]
            locale_str = body.get("locale", "en-us")
            config = body.get("config", {})

            if func_name not in FUNCTION_MAP:
                self.send_error(404, f"Unknown function: {func_name}")
                return

            func, needs_locale = FUNCTION_MAP[func_name]

            # Build arguments
            if func_name == "fixTypos":
                # Main API has keyword arguments
                result = fix_typos(
                    text,
                    locale_str,
                    remove_lines=config.get("removeLines", True),
                )
            elif needs_locale:
                loc = get_locale(locale_str)
                result = func(text, loc)
            else:
                result = func(text)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"result": result}).encode())

        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 9876
    server = HTTPServer(("127.0.0.1", port), BridgeHandler)
    print(f"🐍 Python bridge listening on http://127.0.0.1:{port}")
    print(f"   Exposing {len(FUNCTION_MAP)} functions")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Shutting down")
        server.shutdown()


if __name__ == "__main__":
    main()
