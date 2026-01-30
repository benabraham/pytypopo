"""
Locale class for pytypopo - defines quote characters and ordinal indicators per locale.

Based on: https://github.com/surfinzap/typopo/tree/main/src/locale
"""

# Quote character constants
# Unicode code points to avoid any encoding issues

# Curly quotes (English style)
LEFT_DOUBLE_QUOTE = "\u201c"  # " LEFT DOUBLE QUOTATION MARK
RIGHT_DOUBLE_QUOTE = "\u201d"  # " RIGHT DOUBLE QUOTATION MARK
LEFT_SINGLE_QUOTE = "\u2018"  # ' LEFT SINGLE QUOTATION MARK
RIGHT_SINGLE_QUOTE = "\u2019"  # ' RIGHT SINGLE QUOTATION MARK

# Low-9 quotes (German/Czech/Slovak style)
DOUBLE_LOW_9_QUOTE = "\u201e"  # „ DOUBLE LOW-9 QUOTATION MARK
SINGLE_LOW_9_QUOTE = "\u201a"  # ‚ SINGLE LOW-9 QUOTATION MARK

# Guillemets (Rusyn style)
LEFT_GUILLEMET = "\u00ab"  # « LEFT-POINTING DOUBLE ANGLE QUOTATION MARK
RIGHT_GUILLEMET = "\u00bb"  # » RIGHT-POINTING DOUBLE ANGLE QUOTATION MARK
LEFT_SINGLE_GUILLEMET = "\u2039"  # ‹ SINGLE LEFT-POINTING ANGLE QUOTATION MARK
RIGHT_SINGLE_GUILLEMET = "\u203a"  # › SINGLE RIGHT-POINTING ANGLE QUOTATION MARK

# Space constants for locale-specific spacing
SPACE = " "
NBSP = "\u00a0"  # Non-breaking space
NARROW_NBSP = "\u202f"  # Narrow non-breaking space
HAIR_SPACE = "\u200a"  # Hair space

# Dash constants
EN_DASH = "\u2013"  # En dash
EM_DASH = "\u2014"  # Em dash

# Default locale when none specified or invalid
DEFAULT_LOCALE = "en-us"

# Locale configurations
# Each locale defines quote characters, ordinal indicators, and nbsp settings
LOCALE_CONFIGS = {
    "en-us": {
        "double_quote_open": LEFT_DOUBLE_QUOTE,
        "double_quote_close": RIGHT_DOUBLE_QUOTE,
        "single_quote_open": LEFT_SINGLE_QUOTE,
        "single_quote_close": RIGHT_SINGLE_QUOTE,
        "ordinal_indicator": "st|nd|rd|th",
        "roman_ordinal_indicator": "",  # en-us doesn't use ordinal after roman numerals
        "ordinal_date_first_space": NBSP,
        "ordinal_date_second_space": NBSP,
        "space_before_percent": "",  # en-us: no space before %
        # en-us uses em dash without spaces
        "dash_space_before": "",
        "dash_char": EM_DASH,
        "dash_space_after": "",
        # Space between abbreviated words: F.{space}X. Salda, e.{space}g.
        # en-us uses no space (empty string) - matches upstream typopo
        "space_after_abbreviation": "",
        # Symbol spacing
        "space_after_copyright": NBSP,
        "space_after_sound_recording_copyright": NBSP,
        "space_after_numero_sign": NBSP,
        "space_after_section_sign": NBSP,
        "space_after_paragraph_sign": NBSP,
    },
    "de-de": {
        "double_quote_open": DOUBLE_LOW_9_QUOTE,
        "double_quote_close": LEFT_DOUBLE_QUOTE,  # German uses „…" style
        "single_quote_open": SINGLE_LOW_9_QUOTE,
        "single_quote_close": LEFT_SINGLE_QUOTE,
        "ordinal_indicator": r"\.",
        "roman_ordinal_indicator": r"\.",
        "ordinal_date_first_space": NBSP,
        "ordinal_date_second_space": SPACE,  # German: nbsp after day, space after month
        "space_before_percent": NARROW_NBSP,  # de-de: narrow nbsp before %
        # de-de uses en dash with hair spaces
        "dash_space_before": HAIR_SPACE,
        "dash_char": EN_DASH,
        "dash_space_after": HAIR_SPACE,
        # Space between abbreviated words: F.{space}X. Salda, e.{space}g.
        "space_after_abbreviation": NBSP,
        # Symbol spacing
        "space_after_copyright": NBSP,
        "space_after_sound_recording_copyright": NBSP,
        "space_after_numero_sign": NBSP,
        "space_after_section_sign": NBSP,
        "space_after_paragraph_sign": NBSP,
    },
    "cs": {
        "double_quote_open": DOUBLE_LOW_9_QUOTE,
        "double_quote_close": LEFT_DOUBLE_QUOTE,  # Czech uses „…" style
        "single_quote_open": SINGLE_LOW_9_QUOTE,
        "single_quote_close": LEFT_SINGLE_QUOTE,
        "ordinal_indicator": r"\.",
        "roman_ordinal_indicator": r"\.",
        "ordinal_date_first_space": NBSP,
        "ordinal_date_second_space": NBSP,
        "space_before_percent": NBSP,  # cs: nbsp before %
        # cs uses en dash with nbsp before and space after
        "dash_space_before": NBSP,
        "dash_char": EN_DASH,
        "dash_space_after": SPACE,
        # Space between abbreviated words: F.{space}X. Salda, e.{space}g.
        "space_after_abbreviation": NBSP,
        # Symbol spacing - cs uses regular space for copyright symbols
        "space_after_copyright": SPACE,
        "space_after_sound_recording_copyright": SPACE,
        "space_after_numero_sign": NBSP,
        "space_after_section_sign": NBSP,
        "space_after_paragraph_sign": NBSP,
    },
    "sk": {
        "double_quote_open": DOUBLE_LOW_9_QUOTE,
        "double_quote_close": LEFT_DOUBLE_QUOTE,  # Slovak uses „…" style
        "single_quote_open": SINGLE_LOW_9_QUOTE,
        "single_quote_close": LEFT_SINGLE_QUOTE,
        "ordinal_indicator": r"\.",
        "roman_ordinal_indicator": r"\.",
        "ordinal_date_first_space": NBSP,
        "ordinal_date_second_space": NBSP,
        "space_before_percent": NBSP,  # sk: nbsp before %
        # sk uses em dash with hair spaces (matches upstream typopo)
        "dash_space_before": HAIR_SPACE,
        "dash_char": EM_DASH,
        "dash_space_after": HAIR_SPACE,
        # Space between abbreviated words: F.{space}X. Salda, e.{space}g.
        "space_after_abbreviation": NBSP,
        # Symbol spacing - sk uses narrow nbsp for section/paragraph
        "space_after_copyright": NBSP,
        "space_after_sound_recording_copyright": NBSP,
        "space_after_numero_sign": NBSP,
        "space_after_section_sign": NARROW_NBSP,
        "space_after_paragraph_sign": NARROW_NBSP,
    },
    "rue": {
        "double_quote_open": LEFT_GUILLEMET,
        "double_quote_close": RIGHT_GUILLEMET,
        "single_quote_open": LEFT_SINGLE_GUILLEMET,
        "single_quote_close": RIGHT_SINGLE_GUILLEMET,
        "ordinal_indicator": r"\.",
        "roman_ordinal_indicator": r"\.",
        "ordinal_date_first_space": NBSP,
        "ordinal_date_second_space": NBSP,
        "space_before_percent": NBSP,  # rue: nbsp before %
        # rue uses em dash with hair spaces
        "dash_space_before": HAIR_SPACE,
        "dash_char": EM_DASH,
        "dash_space_after": HAIR_SPACE,
        # Space between abbreviated words: F.{space}X. Salda, e.{space}g.
        "space_after_abbreviation": NBSP,
        # Symbol spacing - rue uses narrow nbsp for section/paragraph
        "space_after_copyright": NBSP,
        "space_after_sound_recording_copyright": NBSP,
        "space_after_numero_sign": NBSP,
        "space_after_section_sign": NARROW_NBSP,
        "space_after_paragraph_sign": NARROW_NBSP,
    },
}

# Set of supported locale IDs for quick lookup
SUPPORTED_LOCALES = frozenset(LOCALE_CONFIGS.keys())


class Locale:
    """
    Locale configuration for typography fixes.

    Provides locale-specific quote characters, ordinal indicators,
    and non-breaking space settings.
    Invalid or None locale IDs default to 'en-us'.
    """

    def __init__(self, locale_id=None):
        # Normalize locale_id: handle None, empty string, and case variations
        normalized_id = self._normalize_locale_id(locale_id)

        # Load configuration for this locale
        config = LOCALE_CONFIGS[normalized_id]

        self._locale_id = normalized_id
        self._double_quote_open = config["double_quote_open"]
        self._double_quote_close = config["double_quote_close"]
        self._single_quote_open = config["single_quote_open"]
        self._single_quote_close = config["single_quote_close"]
        self._ordinal_indicator = config["ordinal_indicator"]
        self._roman_ordinal_indicator = config["roman_ordinal_indicator"]
        self._ordinal_date_first_space = config["ordinal_date_first_space"]
        self._ordinal_date_second_space = config["ordinal_date_second_space"]
        self._space_before_percent = config["space_before_percent"]
        self._dash_space_before = config["dash_space_before"]
        self._dash_char = config["dash_char"]
        self._dash_space_after = config["dash_space_after"]
        self._space_after_abbreviation = config["space_after_abbreviation"]
        self._space_after_copyright = config["space_after_copyright"]
        self._space_after_sound_recording_copyright = config["space_after_sound_recording_copyright"]
        self._space_after_numero_sign = config["space_after_numero_sign"]
        self._space_after_section_sign = config["space_after_section_sign"]
        self._space_after_paragraph_sign = config["space_after_paragraph_sign"]

        # terminal_quotes: combined closing quotes for pattern matching
        self._terminal_quotes = self._double_quote_close + self._single_quote_close

    def _normalize_locale_id(self, locale_id):
        """Normalize locale ID to lowercase, defaulting to en-us if invalid."""
        if not locale_id:
            return DEFAULT_LOCALE

        normalized = locale_id.lower()
        if normalized not in SUPPORTED_LOCALES:
            return DEFAULT_LOCALE

        return normalized

    @property
    def locale_id(self):
        """The normalized locale identifier."""
        return self._locale_id

    @property
    def double_quote_open(self):
        """Opening double quote character for this locale."""
        return self._double_quote_open

    @property
    def double_quote_close(self):
        """Closing double quote character for this locale."""
        return self._double_quote_close

    @property
    def single_quote_open(self):
        """Opening single quote character for this locale."""
        return self._single_quote_open

    @property
    def single_quote_close(self):
        """Closing single quote character for this locale."""
        return self._single_quote_close

    @property
    def terminal_quotes(self):
        """Combined closing quote characters for pattern matching."""
        return self._terminal_quotes

    @property
    def ordinal_indicator(self):
        """Regex pattern for ordinal suffixes in this locale."""
        return self._ordinal_indicator

    @property
    def roman_ordinal_indicator(self):
        """Regex pattern for roman numeral ordinal suffixes (e.g., IV.)"""
        return self._roman_ordinal_indicator

    @property
    def ordinal_date_first_space(self):
        """Space character to use after day in ordinal dates (e.g., 1. 2.)"""
        return self._ordinal_date_first_space

    @property
    def ordinal_date_second_space(self):
        """Space character to use after month in ordinal dates."""
        return self._ordinal_date_second_space

    @property
    def space_before_percent(self):
        """Space character to use before percent sign (empty for en-us)."""
        return self._space_before_percent

    @property
    def dash_space_before(self):
        """Space character to use before dash between words."""
        return self._dash_space_before

    @property
    def dash_char(self):
        """Dash character to use between words (em dash or en dash)."""
        return self._dash_char

    @property
    def dash_space_after(self):
        """Space character to use after dash between words."""
        return self._dash_space_after

    @property
    def space_after_abbreviation(self):
        """Space character between abbreviated words (e.g., F.{space}X. Salda, e.{space}g.)."""
        return self._space_after_abbreviation

    @property
    def space_after_copyright(self):
        """Space character after copyright sign (©)."""
        return self._space_after_copyright

    @property
    def space_after_sound_recording_copyright(self):
        """Space character after sound recording copyright sign (℗)."""
        return self._space_after_sound_recording_copyright

    @property
    def space_after_numero_sign(self):
        """Space character after numero sign (№)."""
        return self._space_after_numero_sign

    @property
    def space_after_section_sign(self):
        """Space character after section sign (§)."""
        return self._space_after_section_sign

    @property
    def space_after_paragraph_sign(self):
        """Space character after paragraph sign (¶)."""
        return self._space_after_paragraph_sign

    def __repr__(self):
        return f"Locale({self._locale_id!r})"


def get_locale(locale_id="en-us"):
    """
    Get a Locale instance for the given locale ID.

    Args:
        locale_id: Language locale identifier (en-us, de-de, cs, sk, rue),
                   or an existing Locale instance.
                   Case-insensitive. Defaults to 'en-us'.

    Returns:
        Locale instance with appropriate quote characters and settings.
        If locale_id is already a Locale instance, returns it unchanged.
    """
    # If already a Locale instance, return unchanged
    if isinstance(locale_id, Locale):
        return locale_id

    return Locale(locale_id)
