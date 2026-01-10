"""
Markdown code block identification and restoration utilities.

Port of src/utils/markdown.js from typopo.

These functions protect markdown code blocks (``` and `) from being modified
by typography fixes by extracting entire code blocks and replacing them
with placeholders, then restoring them after processing.
"""

import re

# Use a placeholder format that won't be affected by typography rules
# No curly braces (caught by bracket rules) or standard punctuation
_MARKDOWN_PLACEHOLDER_PREFIX = "\x00TYPOPO_MD_"
_MARKDOWN_PLACEHOLDER_SUFFIX = "_DM_OPYPOT\x00"


def identify_markdown_code_ticks(text, keep_markdown_code_blocks=True):
    """
    Extract and protect markdown code blocks from typography modifications.

    Replaces entire code blocks (backticks + content) with indexed placeholders.

    Args:
        text: Input text containing markdown code blocks
        keep_markdown_code_blocks: If True, protect code blocks.
                                   If False, return text unchanged and empty list.

    Returns:
        Tuple of (processed_text, code_blocks_list)
        - processed_text: Text with code blocks replaced by placeholders
        - code_blocks_list: List of extracted code block strings
    """
    if not keep_markdown_code_blocks:
        return text, []

    code_blocks = []

    def make_placeholder(index):
        return f"{_MARKDOWN_PLACEHOLDER_PREFIX}{index}{_MARKDOWN_PLACEHOLDER_SUFFIX}"

    def extract_block(match):
        block = match.group(0)
        index = len(code_blocks)
        code_blocks.append(block)
        return make_placeholder(index)

    # Order matters: fenced (```) -> double (``) -> single (`)
    # to avoid matching single/double inside fenced blocks

    # Fenced code blocks: ``` ... ``` (multiline, non-greedy)
    # Includes optional language identifier after opening ```
    result = re.sub(r"```.*?```", extract_block, text, flags=re.DOTALL)

    # Double backticks: `` ... `` (inline, non-greedy)
    result = re.sub(r"``.*?``", extract_block, result, flags=re.DOTALL)

    # Single backticks: ` ... ` (inline, non-greedy, same line)
    result = re.sub(r"`[^`\n]+`", extract_block, result)

    return result, code_blocks


def place_markdown_code_ticks(text, code_blocks, keep_markdown_code_blocks=True):
    """
    Restore code blocks from placeholders.

    Args:
        text: Text with placeholders
        code_blocks: List of original code block strings
        keep_markdown_code_blocks: If True, restore code blocks.
                                   If False, return text unchanged.

    Returns:
        Text with placeholders replaced by original code blocks
    """
    if not keep_markdown_code_blocks:
        return text

    def make_placeholder(index):
        return f"{_MARKDOWN_PLACEHOLDER_PREFIX}{index}{_MARKDOWN_PLACEHOLDER_SUFFIX}"

    result = text
    for i, block in enumerate(code_blocks):
        placeholder = make_placeholder(i)
        result = result.replace(placeholder, block)

    return result
