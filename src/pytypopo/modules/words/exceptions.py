"""
Exception handling for URLs, emails, and filenames.

These elements should be protected from typography modifications.

Port of src/modules/words/exceptions.js from typopo.
"""

import re

# Email pattern - matches standard email addresses
# Supports: local+tag@domain.co.uk format with various TLDs
EMAIL_PATTERN = r"[a-zA-Z0-9\+\.\_%\-]{1,256}@[a-zA-Z0-9][a-zA-Z0-9\-]{0,64}(?:\.[a-zA-Z0-9][a-zA-Z0-9\-]{0,25})+"

# URL pattern - matches HTTP/HTTPS URLs with optional paths, queries, and fragments
# Supports: protocols, authentication, domains, IPs, ports, paths, query strings, anchors
# TLD list covers common extensions plus country codes
_TLD_LIST = (
    r"(?:aero|arpa|asia|agency|a[cdefgilmnoqrstuwxz])|"
    r"(?:biz|b[abdefghijmnorstvwyz])|"
    r"(?:cat|cloud|com|company|coop|c[acdfghiklmnoruvxyz])|"
    r"(?:dev|d[ejkmoz])|"
    r"(?:edu|e[cegrstu])|"
    r"f[ijkmor]|"
    r"(?:gov|guide|g[abdefghilmnpqrstuwy])|"
    r"h[kmnrtu]|"
    r"(?:info|int|i[delmnoqrst])|"
    r"(?:jobs|j[emop])|"
    r"k[eghimnrwyz]|"
    r"l[abcikrstuvy]|"
    r"(?:mil|mobi|museum|m[acdghklmnopqrstuvwxyz])|"
    r"(?:name|net|n[acefgilopruz])|"
    r"(?:org|om|one)|"
    r"(?:pro|p[aefghklmnrstwy])|"
    r"qa|r[eouw]|"
    r"(?:shop|store|s[abcdeghijklmnortuvyz])|"
    r"(?:tel|travel|team|t[cdfghjklmnoprtvwz])|"
    r"u[agkmsyz]|"
    r"v[aceginu]|"
    r"(?:work|w[fs])|"
    r"(?:xyz)|"
    r"y[etu]|"
    r"z[amw]"
)

# IPv4 address pattern
_IPV4_PATTERN = (
    r"(?:25[0-5]|2[0-4][0-9]|[0-1]?[0-9]{1,2})\."
    r"(?:25[0-5]|2[0-4][0-9]|[0-1]?[0-9]{1,2})\."
    r"(?:25[0-5]|2[0-4][0-9]|[0-1]?[0-9]{1,2})\."
    r"(?:25[0-5]|2[0-4][0-9]|[0-1]?[0-9]{1,2})"
)

# URL encoded char or allowed URL characters
_URL_CHAR = r"[a-zA-Z0-9\$\-\_\.\+\!\*\'\(\)\,\;\?\&\=]|(?:%[a-fA-F0-9]{2})"

# Full URL pattern
URL_PATTERN = (
    # Protocol (optional but commonly present)
    r"(?:(?:https?|rtsp)://"
    # Optional authentication (user:pass@)
    rf"(?:(?:{_URL_CHAR}){{1,64}}(?::(?:{_URL_CHAR}){{1,25}})?@)?)?"
    # Domain or IP address
    r"(?:"
    # Domain name with TLD
    rf"(?:[a-zA-Z0-9][a-zA-Z0-9\-]{{0,64}}\.)+(?:{_TLD_LIST})"
    r"|"
    # Or IPv4 address
    rf"{_IPV4_PATTERN}"
    r")"
    # Optional port
    r"(?::\d{1,5})?"
    # Optional path, query string, anchor
    r"(?:/(?:[a-zA-Z0-9\;\\/\?\:\@\&\=\#\~\-\.\+\!\*\'\(\)\,\_]|(?:%[a-fA-F0-9]{2}))*)?(?:\b|$)"
)

# Filename pattern - matches common file extensions
# File extensions cover: source code, documents, images, archives, etc.
_FILE_EXTENSIONS = (
    r"ai|asm|bat|bmp|c|cpp|cs|css|csv|dart|doc|docx|exe|gif|go|html|ics|"
    r"java|jpeg|jpg|js|json|key|kt|less|lua|log|md|mp4|odp|ods|odt|pdf|php|pl|png|ppt|pptx|psd|"
    r"py|r|rar|rb|rs|scala|scss|sh|svg|sql|swift|tar\.gz|tar|tex|tiff|ts|txt|vbs|xml|xls|xlsx|"
    r"yaml|yml|zip"
)
FILENAME_PATTERN = rf"\b[a-zA-Z0-9_%\-]+\.(?:{_FILE_EXTENSIONS})\b"

# Compiled patterns for efficiency
_EMAIL_RE = re.compile(EMAIL_PATTERN, re.IGNORECASE)
_URL_RE = re.compile(URL_PATTERN, re.IGNORECASE)
_FILENAME_RE = re.compile(FILENAME_PATTERN, re.IGNORECASE)


def _collect_exceptions(text, pattern, exceptions):
    """
    Find all matches of pattern in text and add them to exceptions list.

    Args:
        text: Input text to search
        pattern: Compiled regex pattern
        exceptions: List to append found matches to

    Returns:
        The exceptions list (modified in place)
    """
    matches = pattern.findall(text)
    for match in matches:
        # findall returns tuples for patterns with groups, we want the full match
        if isinstance(match, tuple):
            # For patterns with groups, the full match is usually the first element
            # But for URL pattern, we need the whole match string
            # Re-search to get the actual match
            pass
        exceptions.append(match)
    return exceptions


def _replace_with_placeholders(text, exceptions):
    """
    Replace exception strings in text with numbered placeholders.

    Args:
        text: Input text with exceptions
        exceptions: List of exception strings in order

    Returns:
        Text with placeholders instead of exceptions
    """
    result = text
    for i, exception in enumerate(exceptions):
        placeholder = f"{{{{typopo__exception-{i}}}}}"
        result = result.replace(exception, placeholder, 1)
    return result


def exclude_exceptions(text):
    """
    Identify and exclude URLs, emails, and filenames from text.

    Replaces exception patterns with placeholders to protect them
    from typography modifications.

    Args:
        text: Input text to process

    Returns:
        Dict with:
            - processed_text: Text with placeholders
            - exceptions: List of original exception strings
    """
    # Collect all matches with their spans (start, end, match_string)
    # Priority order: emails first, then URLs, then filenames
    # This ensures emails take precedence over partial URL matches within them
    all_matches = []

    for match in _EMAIL_RE.finditer(text):
        all_matches.append((match.start(), match.end(), match.group()))

    for match in _URL_RE.finditer(text):
        all_matches.append((match.start(), match.end(), match.group()))

    for match in _FILENAME_RE.finditer(text):
        all_matches.append((match.start(), match.end(), match.group()))

    # Sort by start position, then by length (longer matches first)
    # This prioritizes longer matches when they start at the same position
    all_matches.sort(key=lambda x: (x[0], -(x[1] - x[0])))

    # Filter out overlapping matches - keep only non-overlapping ones
    exceptions = []
    covered_ranges = []

    for start, end, match_str in all_matches:
        # Check if this range overlaps with any already covered range
        is_overlapping = False
        for covered_start, covered_end in covered_ranges:
            # Overlap if ranges intersect
            if start < covered_end and end > covered_start:
                is_overlapping = True
                break

        if not is_overlapping:
            exceptions.append(match_str)
            covered_ranges.append((start, end))

    # Replace exceptions with placeholders
    processed_text = _replace_with_placeholders(text, exceptions)

    return {
        "processed_text": processed_text,
        "exceptions": exceptions,
    }


def place_exceptions(text, exceptions):
    """
    Restore original exceptions in text by replacing placeholders.

    Args:
        text: Text with placeholders
        exceptions: List of original exception strings

    Returns:
        Text with placeholders replaced by original exceptions
    """
    result = text
    for i, exception in enumerate(exceptions):
        placeholder = f"{{{{typopo__exception-{i}}}}}"
        # Use regex to handle global replacement
        result = re.sub(re.escape(placeholder), exception.replace("\\", "\\\\"), result)
    return result
