"""
Character constants for pytypopo.

Port of src/const.js from typopo.
"""

# Letters - for regex character classes
# Non-Latin characters commonly used in supported locales
NON_LATIN_LOWERCASE = "áäčďéěíĺľňóôöőŕřšťúüűůýŷžабвгґдезіийклмнопрстуфъыьцчжшїщёєюях"
NON_LATIN_UPPERCASE = "ÁÄČĎÉĚÍĹĽŇÓÔÖŐŔŘŠŤÚÜŰŮÝŶŽАБВГҐДЕЗІИЙКЛМНОПРСТУФЪЫЬЦЧЖШЇЩЁЄЮЯХ"
NON_LATIN_CHARS = NON_LATIN_LOWERCASE + NON_LATIN_UPPERCASE
LOWERCASE_CHARS = "a-z" + NON_LATIN_LOWERCASE
UPPERCASE_CHARS = "A-Z" + NON_LATIN_UPPERCASE
ALL_CHARS = "a-z" + NON_LATIN_LOWERCASE + "A-Z" + NON_LATIN_UPPERCASE

# Spaces
SPACE = " "
NBSP = "\u00a0"  # Non-breaking space
HAIR_SPACE = "\u200a"  # Hair space
NARROW_NBSP = "\u202f"  # Narrow non-breaking space
SPACES = SPACE + NBSP + HAIR_SPACE + NARROW_NBSP

# Punctuation
TERMINAL_PUNCTUATION = r"\.\!\?"
SENTENCE_PAUSE_PUNCTUATION = r"\,\:\;"
SENTENCE_PUNCTUATION = SENTENCE_PAUSE_PUNCTUATION + TERMINAL_PUNCTUATION
OPENING_BRACKETS = r"\(\[\{"
CLOSING_BRACKETS = r"\)\]\}"
ELLIPSIS = "\u2026"  # Horizontal ellipsis
HYPHEN = "-"
EN_DASH = "\u2013"  # En dash
EM_DASH = "\u2014"  # Em dash
SLASH = "/"

# Symbols
DEGREE = "\u00b0"  # Degree sign
MULTIPLICATION_SIGN = "\u00d7"  # Multiplication sign
AMPERSAND = "&"
SECTION_SIGN = "\u00a7"  # Section sign
PARAGRAPH_SIGN = "\u00b6"  # Paragraph/pilcrow sign
COPYRIGHT = "\u00a9"  # Copyright sign
SOUND_RECORDING_COPYRIGHT = "\u2117"  # Sound recording copyright
REGISTERED_TRADEMARK = "\u00ae"  # Registered trademark
SERVICE_MARK = "\u2120"  # Service mark
TRADEMARK = "\u2122"  # Trademark
PLUS = "+"
MINUS = "\u2212"  # Minus sign (not hyphen)
PLUS_MINUS = "\u00b1"  # Plus-minus sign
PERCENT = "%"
PERMILLE = "\u2030"  # Per mille sign
PERMYRIAD = "\u2031"  # Per ten thousand sign
NUMBER_SIGN = "#"
NUMERO_SIGN = "\u2116"  # Numero sign

# Numbers
ROMAN_NUMERALS = "IVXLCDM"

# Quotes
APOSTROPHE = "\u2019"  # Right single quotation mark (typographic apostrophe)
SINGLE_PRIME = "\u2032"  # Prime
DOUBLE_PRIME = "\u2033"  # Double prime
BACKTICK = "`"
