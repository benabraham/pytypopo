"""
Fix accidental uppercase errors.

Best-effort function to fix most common accidental uppercase errors:
1. Two first uppercase letters (UPpercase -> Uppercase)
2. Swapped cases (uPPERCASE -> UPPERCASE)

Does not fix mixed case (UppERcaSe) as these are often intentional brand names.

Port of src/modules/words/case.js from typopo.
"""

import re

from pytypopo.const import ALL_CHARS, LOWERCASE_CHARS, UPPERCASE_CHARS


def fix_case(text):
    """
    Correct accidental uppercase in text.

    Fixes two patterns:
    1. Two first uppercase letters followed by lowercase (UPpercase -> Uppercase)
    2. Swapped cases - lowercase then uppercase (uPPERCASE -> UPPERCASE)

    Excludes known brand names like iOS, iPhone, macOS from modification.

    Args:
        text: Input text to fix

    Returns:
        Text with accidental uppercase corrected
    """
    # Pattern [1]: Two first uppercase letters (UPpercase -> Uppercase)
    # Matches: (non-letter or start) + (2 uppercase) + (2+ lowercase)
    # Example: "JEnnifer" -> "Jennifer"
    pattern1 = re.compile(
        rf"([^{ALL_CHARS}]|^)"  # Non-letter boundary or start
        rf"([{UPPERCASE_CHARS}]{{2}})"  # Two uppercase letters
        rf"([{LOWERCASE_CHARS}]{{2,}})",  # Two or more lowercase letters
        re.UNICODE,
    )

    def fix_double_caps(match):
        prefix = match.group(1)
        caps = match.group(2)
        rest = match.group(3)
        # Keep first char uppercase, lowercase the second
        return f"{prefix}{caps[0]}{caps[1].lower()}{rest}"

    text = pattern1.sub(fix_double_caps, text)

    # Pattern [2]: Swapped cases (uPPERCASE -> UPPERCASE)
    # Matches: word boundary + (lowercase) + (2+ uppercase)
    # Excludes: iOS (and similar patterns)
    # Example: "cAPSLOCK" -> "Capslock"
    pattern2 = re.compile(
        r"(\b)"  # Word boundary
        rf"(?!iOS)"  # Negative lookahead for iOS (special case)
        rf"([{LOWERCASE_CHARS}])"  # One lowercase letter
        rf"([{UPPERCASE_CHARS}]{{2,}})",  # Two or more uppercase letters
        re.UNICODE,
    )

    def fix_swapped_case(match):
        boundary = match.group(1)
        first_lower = match.group(2)
        rest_upper = match.group(3)
        # Uppercase the first letter, lowercase the rest
        return f"{boundary}{first_lower.upper()}{rest_upper.lower()}"

    text = pattern2.sub(fix_swapped_case, text)

    return text
