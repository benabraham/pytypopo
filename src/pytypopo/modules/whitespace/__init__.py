"""
Whitespace module for pytypopo.

Handles line normalization, space fixes, and non-breaking space rules.
"""

from pytypopo.modules.whitespace.lines import fix_lines
from pytypopo.modules.whitespace.nbsp import fix_nbsp
from pytypopo.modules.whitespace.spaces import fix_spaces

__all__ = ["fix_lines", "fix_spaces", "fix_nbsp"]
