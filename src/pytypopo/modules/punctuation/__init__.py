"""
Punctuation module for pytypopo.

Provides functions for fixing punctuation issues including periods,
ellipsis, dashes, and quotes.
"""

from pytypopo.modules.punctuation.dash import fix_dash
from pytypopo.modules.punctuation.double_quotes import fix_double_quotes_and_primes
from pytypopo.modules.punctuation.ellipsis import fix_ellipsis
from pytypopo.modules.punctuation.period import fix_period
from pytypopo.modules.punctuation.single_quotes import fix_single_quotes_primes_and_apostrophes

# Aliases for simpler names
fix_double_quotes = fix_double_quotes_and_primes
fix_single_quotes = fix_single_quotes_primes_and_apostrophes

__all__ = [
    "fix_dash",
    "fix_double_quotes",
    "fix_double_quotes_and_primes",
    "fix_ellipsis",
    "fix_period",
    "fix_single_quotes",
    "fix_single_quotes_primes_and_apostrophes",
]
