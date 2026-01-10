"""
Locale module for pytypopo.

Provides locale-specific typography settings including quote characters
and ordinal indicators for supported languages.

Supported locales:
    - en-us: English (US) - curly quotes
    - de-de: German - low-high quotes
    - cs: Czech - low-high quotes
    - sk: Slovak - low-high quotes
    - rue: Rusyn - guillemets
"""

from pytypopo.locale.base import Locale, get_locale

__all__ = ["Locale", "get_locale"]
