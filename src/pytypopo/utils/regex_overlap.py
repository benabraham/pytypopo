"""
Regex overlap handling utility.

Port of src/utils/regex-overlap.js from typopo.

This module provides a function to handle regex replacements where matches
can overlap (e.g., in "1-2-3", the pattern (\\d)-(\\d) matches "1-2" and "2-3",
but a standard replace only catches every other match).
"""

MAX_ITERATIONS = 50


def replace_with_overlap_handling(text, pattern, replacement):
    """
    Replace pattern matches in text, handling overlapping matches.

    Standard regex replace can miss overlapping matches. For example,
    in "1-2-3" with pattern (\\d)-(\\d), only "1-2" gets replaced because
    after that replacement, "2" is already consumed. This function
    iteratively applies the replacement until no more matches are found.

    Args:
        text: The input text to process
        pattern: Compiled regex pattern (re.Pattern)
        replacement: String (with \\1 backrefs) or callable

    Returns:
        Text with all overlapping matches replaced
    """
    iterations = 0
    result = text
    previous_result = ""

    # Keep applying replacements until no more changes occur or max iterations reached
    while result != previous_result and iterations < MAX_ITERATIONS:
        previous_result = result
        result = pattern.sub(replacement, result)
        iterations += 1

    return result
