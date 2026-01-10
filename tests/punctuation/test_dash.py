"""
Tests for dash fixes: hyphens to en/em dashes, spacing around dashes.

Port of tests/punctuation/dash.test.js from typopo.
"""

import pytest

from pytypopo.const import (
    EM_DASH,
    EN_DASH,
    HAIR_SPACE,
    NARROW_NBSP,
    NBSP,
    PERMILLE,
    PERMYRIAD,
)
from pytypopo.locale.base import get_locale
from pytypopo.modules.punctuation.dash import (
    fix_dash,
    fix_dash_between_cardinal_numbers,
    fix_dash_between_ordinal_numbers,
    fix_dash_between_percentage_range,
    fix_dash_between_word_and_brackets,
    fix_dash_between_word_and_punctuation,
    fix_dashes_between_words,
)

# =============================================================================
# Template expansion helper
# =============================================================================


def expand_template(template, locale_id):
    """
    Expand template placeholders to locale-specific values.

    Replaces:
    - ${spaceBeforeDash} -> locale.dash_space_before
    - ${dash} -> locale.dash_char
    - ${spaceAfterDash} -> locale.dash_space_after
    """
    if "${" not in template:
        return template

    loc = get_locale(locale_id)
    result = template
    result = result.replace("${spaceBeforeDash}", loc.dash_space_before)
    result = result.replace("${dash}", loc.dash_char)
    result = result.replace("${spaceAfterDash}", loc.dash_space_after)
    return result


# Helper to get locale-specific expected output for dashes between words
def expected_dash_between_words(locale_id):
    """Get expected output for dash between words based on locale."""
    loc = get_locale(locale_id)
    return f"{loc.dash_space_before}{loc.dash_char}{loc.dash_space_after}"


def expected_dash_before_punctuation(locale_id):
    """Get expected output for dash before punctuation (no space after)."""
    loc = get_locale(locale_id)
    return f"{loc.dash_space_before}{loc.dash_char}"


# =============================================================================
# Test Data Sets - ported from dash.test.js
# =============================================================================

# False positives - should NOT be modified
# Ported from dashFalsePositives in dash.test.js
DASH_FALSE_POSITIVES = {
    # False positive: compound words
    "e -shop": "e -shop",
    "e- shop": "e- shop",
    f"e-{NBSP}shop": f"e-{NBSP}shop",  # nbsp
    f"e-{HAIR_SPACE}shop": f"e-{HAIR_SPACE}shop",  # hairSpace
    f"e-{NARROW_NBSP}shop": f"e-{NARROW_NBSP}shop",  # narrowNbsp
    # False positive: hyphen at the beginning of the paragraph
    "- she said": "- she said",
    " - she said": " - she said",
    "  - she said": "  - she said",
    "\t- she said": "\t- she said",
    "\t\t- she said": "\t\t- she said",
    "+-": "+-",
    "{{test-variable}}": "{{test-variable}}",
    "---": "---",  # standalone hyphens for <hr> in markdown
}


# Dashes between words - locale-specific output
# Ported from dashesBetweenWordsSet in dash.test.js
DASHES_BETWEEN_WORDS = {
    "and - she said": "and${spaceBeforeDash}${dash}${spaceAfterDash}she said",
    f"and {EN_DASH} she said": "and${spaceBeforeDash}${dash}${spaceAfterDash}she said",
    f"and  {EN_DASH}  she said": "and${spaceBeforeDash}${dash}${spaceAfterDash}she said",
    f"and {EM_DASH} she said": "and${spaceBeforeDash}${dash}${spaceAfterDash}she said",
    f"and  {EM_DASH}  she said": "and${spaceBeforeDash}${dash}${spaceAfterDash}she said",
    f"and{NBSP}{EM_DASH} she said": "and${spaceBeforeDash}${dash}${spaceAfterDash}she said",  # mixed spaces
    f"and{EM_DASH}{NBSP}she said": "and${spaceBeforeDash}${dash}${spaceAfterDash}she said",  # mixed spaces
    f"and {EM_DASH}she said": "and${spaceBeforeDash}${dash}${spaceAfterDash}she said",
    f"and{EM_DASH}she said": "and${spaceBeforeDash}${dash}${spaceAfterDash}she said",
    f"word{NBSP}-{NBSP}word": "word${spaceBeforeDash}${dash}${spaceAfterDash}word",  # nbsp
    f"word{HAIR_SPACE}-{HAIR_SPACE}word": "word${spaceBeforeDash}${dash}${spaceAfterDash}word",  # hairSpace
    f"word{NARROW_NBSP}-{NARROW_NBSP}word": "word${spaceBeforeDash}${dash}${spaceAfterDash}word",  # narrowNbsp
    "pta\u0161k\u0177 -  \u010dadi\u010d": "pta\u0161k\u0177${spaceBeforeDash}${dash}${spaceAfterDash}\u010dadi\u010d",  # non-latin chars
    "\u0445\u043e\u0442\u0457\u0432 - \u043d\u0438\u044f\u043a\u0435": "\u0445\u043e\u0442\u0457\u0432${spaceBeforeDash}${dash}${spaceAfterDash}\u043d\u0438\u044f\u043a\u0435",  # non-latin chars
    "\u2026the top 10 - and explore\u2026": "\u2026the top 10${spaceBeforeDash}${dash}${spaceAfterDash}and explore\u2026",
    f"\u2026the top 10 {EN_DASH} and explore\u2026": "\u2026the top 10${spaceBeforeDash}${dash}${spaceAfterDash}and explore\u2026",
    f"\u2026the top 10 {EN_DASH}  and explore\u2026": "\u2026the top 10${spaceBeforeDash}${dash}${spaceAfterDash}and explore\u2026",
    f"\u2026the top 10{EN_DASH}and explore\u2026": "\u2026the top 10${spaceBeforeDash}${dash}${spaceAfterDash}and explore\u2026",
    f"\u2026the top 10 {EM_DASH} and explore\u2026": "\u2026the top 10${spaceBeforeDash}${dash}${spaceAfterDash}and explore\u2026",
    "\u2026like to see - 7 wonders\u2026": "\u2026like to see${spaceBeforeDash}${dash}${spaceAfterDash}7 wonders\u2026",
    f"\u2026like to see {EN_DASH} 7 wonders\u2026": "\u2026like to see${spaceBeforeDash}${dash}${spaceAfterDash}7 wonders\u2026",
    f"\u2026like to see {EN_DASH}  7 wonders\u2026": "\u2026like to see${spaceBeforeDash}${dash}${spaceAfterDash}7 wonders\u2026",
    f"\u2026like to see{EN_DASH}7 wonders\u2026": "\u2026like to see${spaceBeforeDash}${dash}${spaceAfterDash}7 wonders\u2026",
    f"\u2026like to see {EM_DASH} 7 wonders\u2026": "\u2026like to see${spaceBeforeDash}${dash}${spaceAfterDash}7 wonders\u2026",
    "word -- word": "word${spaceBeforeDash}${dash}${spaceAfterDash}word",
    "word --- word": "word${spaceBeforeDash}${dash}${spaceAfterDash}word",
    f"word {EN_DASH}{EN_DASH} word": "word${spaceBeforeDash}${dash}${spaceAfterDash}word",
    f"word {EN_DASH}{EN_DASH}word": "word${spaceBeforeDash}${dash}${spaceAfterDash}word",
    f"word{EN_DASH}{EN_DASH} word": "word${spaceBeforeDash}${dash}${spaceAfterDash}word",
    f"word{EN_DASH}{EN_DASH}word": "word${spaceBeforeDash}${dash}${spaceAfterDash}word",
    f"word {EN_DASH}{EN_DASH}{EN_DASH} word": "word${spaceBeforeDash}${dash}${spaceAfterDash}word",
    f"word {EM_DASH}{EM_DASH} word": "word${spaceBeforeDash}${dash}${spaceAfterDash}word",
    f"word {EM_DASH}{EM_DASH}word": "word${spaceBeforeDash}${dash}${spaceAfterDash}word",
    f"word{EM_DASH}{EM_DASH} word": "word${spaceBeforeDash}${dash}${spaceAfterDash}word",
    f"word{EM_DASH}{EM_DASH}word": "word${spaceBeforeDash}${dash}${spaceAfterDash}word",
    f"word {EM_DASH}{EM_DASH}{EM_DASH} word": "word${spaceBeforeDash}${dash}${spaceAfterDash}word",
    # false positive
    # leave four and more dashes as they are, maybe that's intentional
    "word ---- word": "word ---- word",
    "word ----- word": "word ----- word",
    f"word {EN_DASH}{EN_DASH}{EN_DASH}{EN_DASH} word": f"word {EN_DASH}{EN_DASH}{EN_DASH}{EN_DASH} word",
    f"word {EM_DASH}{EM_DASH}{EM_DASH}{EM_DASH} word": f"word {EM_DASH}{EM_DASH}{EM_DASH}{EM_DASH} word",
}


# Dash between word and punctuation - locale-specific output
# Ported from dashBetweenWordAndPunctuation in dash.test.js
DASH_BETWEEN_WORD_AND_PUNCTUATION = {
    "so there is a dash - ,": "so there is a dash${spaceBeforeDash}${dash},",
    "so there is a dash -,": "so there is a dash${spaceBeforeDash}${dash},",
    "so there is a dash-,": "so there is a dash${spaceBeforeDash}${dash},",
    "so there is a dash -:": "so there is a dash${spaceBeforeDash}${dash}:",
    "so there is a dash -;": "so there is a dash${spaceBeforeDash}${dash};",
    "so there is a dash -.": "so there is a dash${spaceBeforeDash}${dash}.",
    "so there is a dash -?": "so there is a dash${spaceBeforeDash}${dash}?",
    "so there is a dash -!": "so there is a dash${spaceBeforeDash}${dash}!",
    "so there is a dash -\n": "so there is a dash${spaceBeforeDash}${dash}\n",
    f"so there is a dash {EN_DASH} ,": "so there is a dash${spaceBeforeDash}${dash},",
    f"so there is a dash {EN_DASH},": "so there is a dash${spaceBeforeDash}${dash},",
    f"so there is a dash{EN_DASH},": "so there is a dash${spaceBeforeDash}${dash},",
    f"so there is a dash {EN_DASH}:": "so there is a dash${spaceBeforeDash}${dash}:",
    f"so there is a dash {EN_DASH};": "so there is a dash${spaceBeforeDash}${dash};",
    f"so there is a dash {EN_DASH}.": "so there is a dash${spaceBeforeDash}${dash}.",
    f"so there is a dash {EN_DASH}?": "so there is a dash${spaceBeforeDash}${dash}?",
    f"so there is a dash {EN_DASH}!": "so there is a dash${spaceBeforeDash}${dash}!",
    f"so there is a dash {EN_DASH}\n": "so there is a dash${spaceBeforeDash}${dash}\n",
    f"so there is a dash {EM_DASH} ,": "so there is a dash${spaceBeforeDash}${dash},",
    f"so there is a dash {EM_DASH},": "so there is a dash${spaceBeforeDash}${dash},",
    f"so there is a dash{EM_DASH},": "so there is a dash${spaceBeforeDash}${dash},",
    f"so there is a dash {EM_DASH}:": "so there is a dash${spaceBeforeDash}${dash}:",
    f"so there is a dash {EM_DASH};": "so there is a dash${spaceBeforeDash}${dash};",
    f"so there is a dash {EM_DASH}.": "so there is a dash${spaceBeforeDash}${dash}.",
    f"so there is a dash {EM_DASH}?": "so there is a dash${spaceBeforeDash}${dash}?",
    f"so there is a dash {EM_DASH}!": "so there is a dash${spaceBeforeDash}${dash}!",
    f"so there is a dash {EM_DASH}\n": "so there is a dash${spaceBeforeDash}${dash}\n",
    "word -- !": "word${spaceBeforeDash}${dash}!",
    "word --- !": "word${spaceBeforeDash}${dash}!",
    f"word {EN_DASH}{EN_DASH} !": "word${spaceBeforeDash}${dash}!",
    f"word {EN_DASH}{EN_DASH}!": "word${spaceBeforeDash}${dash}!",
    f"word{EN_DASH}{EN_DASH} !": "word${spaceBeforeDash}${dash}!",
    f"word{EN_DASH}{EN_DASH}!": "word${spaceBeforeDash}${dash}!",
    f"word {EN_DASH}{EN_DASH}{EN_DASH} !": "word${spaceBeforeDash}${dash}!",
    f"word {EM_DASH}{EM_DASH} !": "word${spaceBeforeDash}${dash}!",
    f"word {EM_DASH}{EM_DASH}!": "word${spaceBeforeDash}${dash}!",
    f"word{EM_DASH}{EM_DASH} !": "word${spaceBeforeDash}${dash}!",
    f"word{EM_DASH}{EM_DASH}!": "word${spaceBeforeDash}${dash}!",
    f"word {EM_DASH}{EM_DASH}{EM_DASH} !": "word${spaceBeforeDash}${dash}!",
    # false positive
    # leave four and more dashes as they are, maybe that's intentional
    "word ----!": "word ----!",
    "word -----!": "word -----!",
    f"word {EN_DASH}{EN_DASH}{EN_DASH}{EN_DASH}!": f"word {EN_DASH}{EN_DASH}{EN_DASH}{EN_DASH}!",
    f"word {EM_DASH}{EM_DASH}{EM_DASH}{EM_DASH}!": f"word {EM_DASH}{EM_DASH}{EM_DASH}{EM_DASH}!",
}


# Dash between word and brackets - locale-specific output
# Ported from dashBetweenWordAndBrackets in dash.test.js
DASH_BETWEEN_WORD_AND_BRACKETS = {
    # word - (bracket patterns
    "word - (bracket": "word${spaceBeforeDash}${dash}${spaceAfterDash}(bracket",
    "word -(bracket": "word${spaceBeforeDash}${dash}${spaceAfterDash}(bracket",
    "word- (bracket": "word${spaceBeforeDash}${dash}${spaceAfterDash}(bracket",
    "word-(bracket": "word${spaceBeforeDash}${dash}${spaceAfterDash}(bracket",
    "word - [bracket": "word${spaceBeforeDash}${dash}${spaceAfterDash}[bracket",
    "word -[bracket": "word${spaceBeforeDash}${dash}${spaceAfterDash}[bracket",
    "word- [bracket": "word${spaceBeforeDash}${dash}${spaceAfterDash}[bracket",
    "word-[bracket": "word${spaceBeforeDash}${dash}${spaceAfterDash}[bracket",
    "word - {bracket": "word${spaceBeforeDash}${dash}${spaceAfterDash}{bracket",
    "word -{bracket": "word${spaceBeforeDash}${dash}${spaceAfterDash}{bracket",
    "word- {bracket": "word${spaceBeforeDash}${dash}${spaceAfterDash}{bracket",
    "word-{bracket": "word${spaceBeforeDash}${dash}${spaceAfterDash}{bracket",
    f"word {EN_DASH} (bracket": "word${spaceBeforeDash}${dash}${spaceAfterDash}(bracket",
    f"word {EN_DASH}(bracket": "word${spaceBeforeDash}${dash}${spaceAfterDash}(bracket",
    f"word{EN_DASH} (bracket": "word${spaceBeforeDash}${dash}${spaceAfterDash}(bracket",
    f"word{EN_DASH}(bracket": "word${spaceBeforeDash}${dash}${spaceAfterDash}(bracket",
    f"word {EN_DASH} [bracket": "word${spaceBeforeDash}${dash}${spaceAfterDash}[bracket",
    f"word {EN_DASH}[bracket": "word${spaceBeforeDash}${dash}${spaceAfterDash}[bracket",
    f"word{EN_DASH} [bracket": "word${spaceBeforeDash}${dash}${spaceAfterDash}[bracket",
    f"word{EN_DASH}[bracket": "word${spaceBeforeDash}${dash}${spaceAfterDash}[bracket",
    f"word {EN_DASH} {{bracket": "word${spaceBeforeDash}${dash}${spaceAfterDash}{bracket",
    f"word {EN_DASH}{{bracket": "word${spaceBeforeDash}${dash}${spaceAfterDash}{bracket",
    f"word{EN_DASH} {{bracket": "word${spaceBeforeDash}${dash}${spaceAfterDash}{bracket",
    f"word{EN_DASH}{{bracket": "word${spaceBeforeDash}${dash}${spaceAfterDash}{bracket",
    f"word {EM_DASH} (bracket": "word${spaceBeforeDash}${dash}${spaceAfterDash}(bracket",
    f"word {EM_DASH}(bracket": "word${spaceBeforeDash}${dash}${spaceAfterDash}(bracket",
    f"word{EM_DASH} (bracket": "word${spaceBeforeDash}${dash}${spaceAfterDash}(bracket",
    f"word{EM_DASH}(bracket": "word${spaceBeforeDash}${dash}${spaceAfterDash}(bracket",
    f"word {EM_DASH} [bracket": "word${spaceBeforeDash}${dash}${spaceAfterDash}[bracket",
    f"word {EM_DASH}[bracket": "word${spaceBeforeDash}${dash}${spaceAfterDash}[bracket",
    f"word{EM_DASH} [bracket": "word${spaceBeforeDash}${dash}${spaceAfterDash}[bracket",
    f"word{EM_DASH}[bracket": "word${spaceBeforeDash}${dash}${spaceAfterDash}[bracket",
    f"word {EM_DASH} {{bracket": "word${spaceBeforeDash}${dash}${spaceAfterDash}{bracket",
    f"word {EM_DASH}{{bracket": "word${spaceBeforeDash}${dash}${spaceAfterDash}{bracket",
    f"word{EM_DASH} {{bracket": "word${spaceBeforeDash}${dash}${spaceAfterDash}{bracket",
    f"word{EM_DASH}{{bracket": "word${spaceBeforeDash}${dash}${spaceAfterDash}{bracket",
    f"word {EM_DASH}   (bracket": "word${spaceBeforeDash}${dash}${spaceAfterDash}(bracket",
    "word -- (bracket": "word${spaceBeforeDash}${dash}${spaceAfterDash}(bracket",
    "word --- (bracket": "word${spaceBeforeDash}${dash}${spaceAfterDash}(bracket",
    f"word {EN_DASH}{EN_DASH} (bracket": "word${spaceBeforeDash}${dash}${spaceAfterDash}(bracket",
    f"word {EM_DASH}{EM_DASH} (bracket": "word${spaceBeforeDash}${dash}${spaceAfterDash}(bracket",
    f"word {EM_DASH}{EM_DASH}{EM_DASH} (bracket": "word${spaceBeforeDash}${dash}${spaceAfterDash}(bracket",
    # false positives - leave four and more dashes
    "word ---- (bracket": "word ---- (bracket",
    f"word {EN_DASH}{EN_DASH}{EN_DASH}{EN_DASH} (bracket": f"word {EN_DASH}{EN_DASH}{EN_DASH}{EN_DASH} (bracket",
    f"word {EM_DASH}{EM_DASH}{EM_DASH}{EM_DASH} (bracket": f"word {EM_DASH}{EM_DASH}{EM_DASH}{EM_DASH} (bracket",
    # bracket) - word patterns
    "bracket) - word": "bracket)${spaceBeforeDash}${dash}${spaceAfterDash}word",
    "bracket) -word": "bracket)${spaceBeforeDash}${dash}${spaceAfterDash}word",
    "bracket)- word": "bracket)${spaceBeforeDash}${dash}${spaceAfterDash}word",
    "bracket)-word": "bracket)${spaceBeforeDash}${dash}${spaceAfterDash}word",
    "bracket] - word": "bracket]${spaceBeforeDash}${dash}${spaceAfterDash}word",
    "bracket] -word": "bracket]${spaceBeforeDash}${dash}${spaceAfterDash}word",
    "bracket]- word": "bracket]${spaceBeforeDash}${dash}${spaceAfterDash}word",
    "bracket]-word": "bracket]${spaceBeforeDash}${dash}${spaceAfterDash}word",
    "bracket} - word": "bracket}${spaceBeforeDash}${dash}${spaceAfterDash}word",
    "bracket} -word": "bracket}${spaceBeforeDash}${dash}${spaceAfterDash}word",
    "bracket}- word": "bracket}${spaceBeforeDash}${dash}${spaceAfterDash}word",
    "bracket}-word": "bracket}${spaceBeforeDash}${dash}${spaceAfterDash}word",
    f"bracket) {EN_DASH} word": "bracket)${spaceBeforeDash}${dash}${spaceAfterDash}word",
    f"bracket) {EN_DASH}word": "bracket)${spaceBeforeDash}${dash}${spaceAfterDash}word",
    f"bracket){EN_DASH} word": "bracket)${spaceBeforeDash}${dash}${spaceAfterDash}word",
    f"bracket){EN_DASH}word": "bracket)${spaceBeforeDash}${dash}${spaceAfterDash}word",
    f"bracket] {EN_DASH} word": "bracket]${spaceBeforeDash}${dash}${spaceAfterDash}word",
    f"bracket] {EN_DASH}word": "bracket]${spaceBeforeDash}${dash}${spaceAfterDash}word",
    f"bracket]{EN_DASH} word": "bracket]${spaceBeforeDash}${dash}${spaceAfterDash}word",
    f"bracket]{EN_DASH}word": "bracket]${spaceBeforeDash}${dash}${spaceAfterDash}word",
    f"bracket}} {EN_DASH} word": "bracket}${spaceBeforeDash}${dash}${spaceAfterDash}word",
    f"bracket}} {EN_DASH}word": "bracket}${spaceBeforeDash}${dash}${spaceAfterDash}word",
    f"bracket}}{EN_DASH} word": "bracket}${spaceBeforeDash}${dash}${spaceAfterDash}word",
    f"bracket}}{EN_DASH}word": "bracket}${spaceBeforeDash}${dash}${spaceAfterDash}word",
    f"bracket) {EM_DASH} word": "bracket)${spaceBeforeDash}${dash}${spaceAfterDash}word",
    f"bracket) {EM_DASH}word": "bracket)${spaceBeforeDash}${dash}${spaceAfterDash}word",
    f"bracket){EM_DASH} word": "bracket)${spaceBeforeDash}${dash}${spaceAfterDash}word",
    f"bracket){EM_DASH}word": "bracket)${spaceBeforeDash}${dash}${spaceAfterDash}word",
    f"bracket] {EM_DASH} word": "bracket]${spaceBeforeDash}${dash}${spaceAfterDash}word",
    f"bracket] {EM_DASH}word": "bracket]${spaceBeforeDash}${dash}${spaceAfterDash}word",
    f"bracket]{EM_DASH} word": "bracket]${spaceBeforeDash}${dash}${spaceAfterDash}word",
    f"bracket]{EM_DASH}word": "bracket]${spaceBeforeDash}${dash}${spaceAfterDash}word",
    f"bracket}} {EM_DASH} word": "bracket}${spaceBeforeDash}${dash}${spaceAfterDash}word",
    f"bracket}} {EM_DASH}word": "bracket}${spaceBeforeDash}${dash}${spaceAfterDash}word",
    f"bracket}}{EM_DASH} word": "bracket}${spaceBeforeDash}${dash}${spaceAfterDash}word",
    f"bracket}}{EM_DASH}word": "bracket}${spaceBeforeDash}${dash}${spaceAfterDash}word",
    f"bracket) {EM_DASH}   word": "bracket)${spaceBeforeDash}${dash}${spaceAfterDash}word",
    "bracket) -- word": "bracket)${spaceBeforeDash}${dash}${spaceAfterDash}word",
    "bracket) --- word": "bracket)${spaceBeforeDash}${dash}${spaceAfterDash}word",
    f"bracket) {EN_DASH}{EN_DASH} word": "bracket)${spaceBeforeDash}${dash}${spaceAfterDash}word",
    f"bracket) {EM_DASH}{EM_DASH} word": "bracket)${spaceBeforeDash}${dash}${spaceAfterDash}word",
    f"bracket) {EM_DASH}{EM_DASH}{EM_DASH} word": "bracket)${spaceBeforeDash}${dash}${spaceAfterDash}word",
    # false positives - leave four and more dashes
    "bracket) ---- word": "bracket) ---- word",
    f"bracket) {EN_DASH}{EN_DASH}{EN_DASH}{EN_DASH} word": f"bracket) {EN_DASH}{EN_DASH}{EN_DASH}{EN_DASH} word",
    f"bracket) {EM_DASH}{EM_DASH}{EM_DASH}{EM_DASH} word": f"bracket) {EM_DASH}{EM_DASH}{EM_DASH}{EM_DASH} word",
    # word - ) patterns
    "word - )": "word${spaceBeforeDash}${dash}${spaceAfterDash})",
    "word -)": "word${spaceBeforeDash}${dash}${spaceAfterDash})",
    "word- )": "word${spaceBeforeDash}${dash}${spaceAfterDash})",
    "word-)": "word${spaceBeforeDash}${dash}${spaceAfterDash})",
    "word - ]": "word${spaceBeforeDash}${dash}${spaceAfterDash}]",
    "word -]": "word${spaceBeforeDash}${dash}${spaceAfterDash}]",
    "word- ]": "word${spaceBeforeDash}${dash}${spaceAfterDash}]",
    "word-]": "word${spaceBeforeDash}${dash}${spaceAfterDash}]",
    "word - }": "word${spaceBeforeDash}${dash}${spaceAfterDash}}",
    "word -}": "word${spaceBeforeDash}${dash}${spaceAfterDash}}",
    "word- }": "word${spaceBeforeDash}${dash}${spaceAfterDash}}",
    "word-}": "word${spaceBeforeDash}${dash}${spaceAfterDash}}",
    f"word {EN_DASH} )": "word${spaceBeforeDash}${dash}${spaceAfterDash})",
    f"word {EN_DASH})": "word${spaceBeforeDash}${dash}${spaceAfterDash})",
    f"word{EN_DASH} )": "word${spaceBeforeDash}${dash}${spaceAfterDash})",
    f"word{EN_DASH})": "word${spaceBeforeDash}${dash}${spaceAfterDash})",
    f"word {EN_DASH} ]": "word${spaceBeforeDash}${dash}${spaceAfterDash}]",
    f"word {EN_DASH}]": "word${spaceBeforeDash}${dash}${spaceAfterDash}]",
    f"word{EN_DASH} ]": "word${spaceBeforeDash}${dash}${spaceAfterDash}]",
    f"word{EN_DASH}]": "word${spaceBeforeDash}${dash}${spaceAfterDash}]",
    f"word {EN_DASH} }}": "word${spaceBeforeDash}${dash}${spaceAfterDash}}",
    f"word {EN_DASH}}}": "word${spaceBeforeDash}${dash}${spaceAfterDash}}",
    f"word{EN_DASH} }}": "word${spaceBeforeDash}${dash}${spaceAfterDash}}",
    f"word{EN_DASH}}}": "word${spaceBeforeDash}${dash}${spaceAfterDash}}",
    f"word {EM_DASH} )": "word${spaceBeforeDash}${dash}${spaceAfterDash})",
    f"word {EM_DASH})": "word${spaceBeforeDash}${dash}${spaceAfterDash})",
    f"word{EM_DASH} )": "word${spaceBeforeDash}${dash}${spaceAfterDash})",
    f"word{EM_DASH})": "word${spaceBeforeDash}${dash}${spaceAfterDash})",
    f"word {EM_DASH} ]": "word${spaceBeforeDash}${dash}${spaceAfterDash}]",
    f"word {EM_DASH}]": "word${spaceBeforeDash}${dash}${spaceAfterDash}]",
    f"word{EM_DASH} ]": "word${spaceBeforeDash}${dash}${spaceAfterDash}]",
    f"word{EM_DASH}]": "word${spaceBeforeDash}${dash}${spaceAfterDash}]",
    f"word {EM_DASH} }}": "word${spaceBeforeDash}${dash}${spaceAfterDash}}",
    f"word {EM_DASH}}}": "word${spaceBeforeDash}${dash}${spaceAfterDash}}",
    f"word{EM_DASH} }}": "word${spaceBeforeDash}${dash}${spaceAfterDash}}",
    f"word{EM_DASH}}}": "word${spaceBeforeDash}${dash}${spaceAfterDash}}",
    f"word {EM_DASH}   )": "word${spaceBeforeDash}${dash}${spaceAfterDash})",
    "word -- )": "word${spaceBeforeDash}${dash}${spaceAfterDash})",
    "word --- )": "word${spaceBeforeDash}${dash}${spaceAfterDash})",
    f"word {EN_DASH}{EN_DASH} )": "word${spaceBeforeDash}${dash}${spaceAfterDash})",
    f"word {EM_DASH}{EM_DASH} )": "word${spaceBeforeDash}${dash}${spaceAfterDash})",
    f"word {EM_DASH}{EM_DASH}{EM_DASH} )": "word${spaceBeforeDash}${dash}${spaceAfterDash})",
    # false positives - leave four and more dashes
    "word ----)": "word ----)",
    f"word {EN_DASH}{EN_DASH}{EN_DASH}{EN_DASH})": f"word {EN_DASH}{EN_DASH}{EN_DASH}{EN_DASH})",
    f"word {EM_DASH}{EM_DASH}{EM_DASH}{EM_DASH})": f"word {EM_DASH}{EM_DASH}{EM_DASH}{EM_DASH})",
    # ( - word patterns
    "( - word": "(${spaceBeforeDash}${dash}${spaceAfterDash}word",
    "( -word": "(${spaceBeforeDash}${dash}${spaceAfterDash}word",
    "(- word": "(${spaceBeforeDash}${dash}${spaceAfterDash}word",
    "(-word": "(${spaceBeforeDash}${dash}${spaceAfterDash}word",
    "[ - word": "[${spaceBeforeDash}${dash}${spaceAfterDash}word",
    "[ -word": "[${spaceBeforeDash}${dash}${spaceAfterDash}word",
    "[- word": "[${spaceBeforeDash}${dash}${spaceAfterDash}word",
    "[-word": "[${spaceBeforeDash}${dash}${spaceAfterDash}word",
    "{ - word": "{${spaceBeforeDash}${dash}${spaceAfterDash}word",
    "{ -word": "{${spaceBeforeDash}${dash}${spaceAfterDash}word",
    "{- word": "{${spaceBeforeDash}${dash}${spaceAfterDash}word",
    "{-word": "{${spaceBeforeDash}${dash}${spaceAfterDash}word",
    f"( {EN_DASH} word": "(${spaceBeforeDash}${dash}${spaceAfterDash}word",
    f"( {EN_DASH}word": "(${spaceBeforeDash}${dash}${spaceAfterDash}word",
    f"({EN_DASH} word": "(${spaceBeforeDash}${dash}${spaceAfterDash}word",
    f"({EN_DASH}word": "(${spaceBeforeDash}${dash}${spaceAfterDash}word",
    f"[ {EN_DASH} word": "[${spaceBeforeDash}${dash}${spaceAfterDash}word",
    f"[ {EN_DASH}word": "[${spaceBeforeDash}${dash}${spaceAfterDash}word",
    f"[{EN_DASH} word": "[${spaceBeforeDash}${dash}${spaceAfterDash}word",
    f"[{EN_DASH}word": "[${spaceBeforeDash}${dash}${spaceAfterDash}word",
    f"{{ {EN_DASH} word": "{${spaceBeforeDash}${dash}${spaceAfterDash}word",
    f"{{ {EN_DASH}word": "{${spaceBeforeDash}${dash}${spaceAfterDash}word",
    f"{{{EN_DASH} word": "{${spaceBeforeDash}${dash}${spaceAfterDash}word",
    f"{{{EN_DASH}word": "{${spaceBeforeDash}${dash}${spaceAfterDash}word",
    f"( {EM_DASH} word": "(${spaceBeforeDash}${dash}${spaceAfterDash}word",
    f"( {EM_DASH}word": "(${spaceBeforeDash}${dash}${spaceAfterDash}word",
    f"({EM_DASH} word": "(${spaceBeforeDash}${dash}${spaceAfterDash}word",
    f"({EM_DASH}word": "(${spaceBeforeDash}${dash}${spaceAfterDash}word",
    f"[ {EM_DASH} word": "[${spaceBeforeDash}${dash}${spaceAfterDash}word",
    f"[ {EM_DASH}word": "[${spaceBeforeDash}${dash}${spaceAfterDash}word",
    f"[{EM_DASH} word": "[${spaceBeforeDash}${dash}${spaceAfterDash}word",
    f"[{EM_DASH}word": "[${spaceBeforeDash}${dash}${spaceAfterDash}word",
    f"{{ {EM_DASH} word": "{${spaceBeforeDash}${dash}${spaceAfterDash}word",
    f"{{ {EM_DASH}word": "{${spaceBeforeDash}${dash}${spaceAfterDash}word",
    f"{{{EM_DASH} word": "{${spaceBeforeDash}${dash}${spaceAfterDash}word",
    f"{{{EM_DASH}word": "{${spaceBeforeDash}${dash}${spaceAfterDash}word",
    f"( {EM_DASH}   word": "(${spaceBeforeDash}${dash}${spaceAfterDash}word",
    "( -- word": "(${spaceBeforeDash}${dash}${spaceAfterDash}word",
    "( --- word": "(${spaceBeforeDash}${dash}${spaceAfterDash}word",
    f"( {EN_DASH}{EN_DASH} word": "(${spaceBeforeDash}${dash}${spaceAfterDash}word",
    f"( {EM_DASH}{EM_DASH} word": "(${spaceBeforeDash}${dash}${spaceAfterDash}word",
    f"( {EM_DASH}{EM_DASH}{EM_DASH} word": "(${spaceBeforeDash}${dash}${spaceAfterDash}word",
    # false positives - leave four and more dashes
    "(---- word": "(---- word",
    f"({EN_DASH}{EN_DASH}{EN_DASH}{EN_DASH} word": f"({EN_DASH}{EN_DASH}{EN_DASH}{EN_DASH} word",
    f"({EM_DASH}{EM_DASH}{EM_DASH}{EM_DASH} word": f"({EM_DASH}{EM_DASH}{EM_DASH}{EM_DASH} word",
    # word) - (word patterns
    "word) - (word": "word)${spaceBeforeDash}${dash}${spaceAfterDash}(word",
    "word) -(word": "word)${spaceBeforeDash}${dash}${spaceAfterDash}(word",
    "word)- (word": "word)${spaceBeforeDash}${dash}${spaceAfterDash}(word",
    "word)-(word": "word)${spaceBeforeDash}${dash}${spaceAfterDash}(word",
    "word] - [word": "word]${spaceBeforeDash}${dash}${spaceAfterDash}[word",
    "word] -[word": "word]${spaceBeforeDash}${dash}${spaceAfterDash}[word",
    "word]- [word": "word]${spaceBeforeDash}${dash}${spaceAfterDash}[word",
    "word]-[word": "word]${spaceBeforeDash}${dash}${spaceAfterDash}[word",
    "word} - {word": "word}${spaceBeforeDash}${dash}${spaceAfterDash}{word",
    "word} -{word": "word}${spaceBeforeDash}${dash}${spaceAfterDash}{word",
    "word}- {word": "word}${spaceBeforeDash}${dash}${spaceAfterDash}{word",
    "word}-{word": "word}${spaceBeforeDash}${dash}${spaceAfterDash}{word",
    f"word) {EN_DASH} (word": "word)${spaceBeforeDash}${dash}${spaceAfterDash}(word",
    f"word) {EN_DASH}(word": "word)${spaceBeforeDash}${dash}${spaceAfterDash}(word",
    f"word){EN_DASH} (word": "word)${spaceBeforeDash}${dash}${spaceAfterDash}(word",
    f"word){EN_DASH}(word": "word)${spaceBeforeDash}${dash}${spaceAfterDash}(word",
    f"word] {EN_DASH} [word": "word]${spaceBeforeDash}${dash}${spaceAfterDash}[word",
    f"word] {EN_DASH}[word": "word]${spaceBeforeDash}${dash}${spaceAfterDash}[word",
    f"word]{EN_DASH} [word": "word]${spaceBeforeDash}${dash}${spaceAfterDash}[word",
    f"word]{EN_DASH}[word": "word]${spaceBeforeDash}${dash}${spaceAfterDash}[word",
    f"word}} {EN_DASH} {{word": "word}${spaceBeforeDash}${dash}${spaceAfterDash}{word",
    f"word}}{EN_DASH} {{word": "word}${spaceBeforeDash}${dash}${spaceAfterDash}{word",
    f"word}}{EN_DASH}{{word": "word}${spaceBeforeDash}${dash}${spaceAfterDash}{word",
    f"word) {EM_DASH} (word": "word)${spaceBeforeDash}${dash}${spaceAfterDash}(word",
    f"word) {EM_DASH}(word": "word)${spaceBeforeDash}${dash}${spaceAfterDash}(word",
    f"word){EM_DASH} (word": "word)${spaceBeforeDash}${dash}${spaceAfterDash}(word",
    f"word){EM_DASH}(word": "word)${spaceBeforeDash}${dash}${spaceAfterDash}(word",
    f"word] {EM_DASH} [word": "word]${spaceBeforeDash}${dash}${spaceAfterDash}[word",
    f"word] {EM_DASH}[word": "word]${spaceBeforeDash}${dash}${spaceAfterDash}[word",
    f"word]{EM_DASH} [word": "word]${spaceBeforeDash}${dash}${spaceAfterDash}[word",
    f"word]{EM_DASH}[word": "word]${spaceBeforeDash}${dash}${spaceAfterDash}[word",
    f"word}} {EM_DASH} {{word": "word}${spaceBeforeDash}${dash}${spaceAfterDash}{word",
    f"word}} {EM_DASH}{{word": "word}${spaceBeforeDash}${dash}${spaceAfterDash}{word",
    f"word}}{EM_DASH} {{word": "word}${spaceBeforeDash}${dash}${spaceAfterDash}{word",
    f"word}}{EM_DASH}{{word": "word}${spaceBeforeDash}${dash}${spaceAfterDash}{word",
    # different spacing
    f"word) {EN_DASH}{NBSP}(word": "word)${spaceBeforeDash}${dash}${spaceAfterDash}(word",  # nbsp
    f"word){NBSP}{EN_DASH} (word": "word)${spaceBeforeDash}${dash}${spaceAfterDash}(word",  # nbsp
    f"word){HAIR_SPACE}{EN_DASH}{HAIR_SPACE}(word": "word)${spaceBeforeDash}${dash}${spaceAfterDash}(word",  # hairSpace
    # only fix spaces, but not hyphens, en dash or em dash
    "( - )": "(-)",
    "[ - ]": "[-]",
    "{ - }": "{-}",
    f"( {EN_DASH} )": f"({EN_DASH})",
    f"[ {EN_DASH} ]": f"[{EN_DASH}]",
    f"{{ {EN_DASH} }}": f"{{{EN_DASH}}}",
    f"( {EM_DASH} )": f"({EM_DASH})",
    f"[ {EM_DASH} ]": f"[{EM_DASH}]",
    f"{{ {EM_DASH} }}": f"{{{EM_DASH}}}",
    "( -)": "(-)",
    "[ -]": "[-]",
    "{ -}": "{-}",
    f"( {EN_DASH})": f"({EN_DASH})",
    f"[ {EN_DASH}]": f"[{EN_DASH}]",
    f"{{ {EN_DASH}}}": f"{{{EN_DASH}}}",
    f"( {EM_DASH})": f"({EM_DASH})",
    f"[ {EM_DASH}]": f"[{EM_DASH}]",
    f"{{ {EM_DASH}}}": f"{{{EM_DASH}}}",
    "(- )": "(-)",
    "[- ]": "[-]",
    "{- }": "{-}",
    f"({EN_DASH} )": f"({EN_DASH})",
    f"[{EN_DASH} ]": f"[{EN_DASH}]",
    f"{{{EN_DASH} }}": f"{{{EN_DASH}}}",
    f"({EM_DASH} )": f"({EM_DASH})",
    f"[{EM_DASH} ]": f"[{EM_DASH}]",
    f"{{{EM_DASH} }}": f"{{{EM_DASH}}}",
    "( -- )": "(--)",
    "( ----- )": "(-----)",
    "( --     )": "(--)",
    "(    --  )": "(--)",
    "( --)": "(--)",
    "(-- )": "(--)",
    # false positives, don't fix
    "(-)": "(-)",
    "[-]": "[-]",
    "{-}": "{-}",
    f"({EN_DASH})": f"({EN_DASH})",
    f"[{EN_DASH}]": f"[{EN_DASH}]",
    f"{{{EN_DASH}}}": f"{{{EN_DASH}}}",
    f"({EM_DASH})": f"({EM_DASH})",
    f"[{EM_DASH}]": f"[{EM_DASH}]",
    f"{{{EM_DASH}}}": f"{{{EM_DASH}}}",
    "(--)": "(--)",
    f"({EN_DASH}{EN_DASH})": f"({EN_DASH}{EN_DASH})",
    f"({EM_DASH}{EM_DASH})": f"({EM_DASH}{EM_DASH})",
    f"(-{EN_DASH}{EM_DASH})": f"(-{EN_DASH}{EM_DASH})",
}


# Cardinal numbers - always uses en dash (locale independent)
# Ported from dashCardinalNumbersSet in dash.test.js
DASH_CARDINAL_NUMBERS = {
    "5-6 eggs": f"5{EN_DASH}6 eggs",
    "15-16 eggs": f"15{EN_DASH}16 eggs",
    "5 -6 eggs": f"5{EN_DASH}6 eggs",
    "5- 6 eggs": f"5{EN_DASH}6 eggs",
    "5 - 6 eggs": f"5{EN_DASH}6 eggs",
    f"5{EM_DASH}6 eggs": f"5{EN_DASH}6 eggs",
    "5-12\u2033 long": f"5{EN_DASH}12\u2033 long",
    "In 5.25-10.75 range": f"In 5.25{EN_DASH}10.75 range",
    "In 5,000.25-10,000.75 range": f"In 5,000.25{EN_DASH}10,000.75 range",
    "v rozmedzí 5,25-10,75": f"v rozmedzí 5,25{EN_DASH}10,75",
    f"v rozmedzí 5{NBSP}000,25-10{NBSP}000,75": f"v rozmedzí 5{NBSP}000,25{EN_DASH}10{NBSP}000,75",
    "2-3 Eier": f"2{EN_DASH}3 Eier",
    "2 -3 Eier": f"2{EN_DASH}3 Eier",
    "2- 3 Eier": f"2{EN_DASH}3 Eier",
    "2 - 3 Eier": f"2{EN_DASH}3 Eier",
    f"2{EM_DASH}3 Eier": f"2{EN_DASH}3 Eier",
    "im Bereich von 5.000,25-10.000,75": f"im Bereich von 5.000,25{EN_DASH}10.000,75",
    # date formats
    "2019-02-03": f"2019{EN_DASH}02{EN_DASH}03",
    "2019 - 02 - 03": f"2019{EN_DASH}02{EN_DASH}03",
    "2019- 02 -03": f"2019{EN_DASH}02{EN_DASH}03",
    "2019-02": f"2019{EN_DASH}02",
    "2019 -02": f"2019{EN_DASH}02",
    "2019 - 02": f"2019{EN_DASH}02",
    "2019- 02": f"2019{EN_DASH}02",
    "19 - 02 - 03": f"19{EN_DASH}02{EN_DASH}03",
    "19- 02 -03": f"19{EN_DASH}02{EN_DASH}03",
    # telephone numbers
    f"1{EN_DASH}2{EN_DASH}3": f"1{EN_DASH}2{EN_DASH}3",  # correct
    f"1 {EN_DASH} 2 {EN_DASH} 3": f"1{EN_DASH}2{EN_DASH}3",
    f"1{EN_DASH} 2 {EN_DASH}3": f"1{EN_DASH}2{EN_DASH}3",
    "1-2-3": f"1{EN_DASH}2{EN_DASH}3",
    "1 - 2 - 3": f"1{EN_DASH}2{EN_DASH}3",
    "1- 2 -3": f"1{EN_DASH}2{EN_DASH}3",
    f"1{EM_DASH}2{EM_DASH}3": f"1{EN_DASH}2{EN_DASH}3",
    f"1 {EM_DASH} 2 {EM_DASH} 3": f"1{EN_DASH}2{EN_DASH}3",
    f"1{EM_DASH} 2 {EM_DASH}3": f"1{EN_DASH}2{EN_DASH}3",
    "154-123-4567": f"154{EN_DASH}123{EN_DASH}4567",
    # multiple dashes
    "2 -- 3": f"2{EN_DASH}3",
    "2 --- 3": f"2{EN_DASH}3",
    f"2 {EN_DASH}{EN_DASH} 3": f"2{EN_DASH}3",
    f"2 {EN_DASH}{EN_DASH}{EN_DASH} 3": f"2{EN_DASH}3",
    f"2 {EM_DASH}{EM_DASH} 3": f"2{EN_DASH}3",
    f"2 {EM_DASH}{EM_DASH}{EM_DASH} 3": f"2{EN_DASH}3",
}


# Percentage ranges - always uses en dash (locale independent)
# Ported from dashPercentageRangeSet in dash.test.js
DASH_PERCENTAGE_RANGE = {
    "20%-30%": f"20%{EN_DASH}30%",
    "20% -30%": f"20%{EN_DASH}30%",
    "20% - 30%": f"20%{EN_DASH}30%",
    "20%- 30%": f"20%{EN_DASH}30%",
    f"20%{EN_DASH}30%": f"20%{EN_DASH}30%",
    f"20%{EM_DASH}30%": f"20%{EN_DASH}30%",
    "20 %-30 %": f"20 %{EN_DASH}30 %",
    "20 % -30 %": f"20 %{EN_DASH}30 %",
    "20 % - 30 %": f"20 %{EN_DASH}30 %",
    "20 %- 30 %": f"20 %{EN_DASH}30 %",
    f"20 {PERMILLE} - 30 {PERMILLE}": f"20 {PERMILLE}{EN_DASH}30 {PERMILLE}",
    f"20 {PERMYRIAD} - 30 {PERMYRIAD}": f"20 {PERMYRIAD}{EN_DASH}30 {PERMYRIAD}",
    "2 % -- 3 %": f"2 %{EN_DASH}3 %",
    "2 % --- 3 %": f"2 %{EN_DASH}3 %",
    f"2 % {EN_DASH}{EN_DASH} 3 %": f"2 %{EN_DASH}3 %",
    f"2 % {EN_DASH}{EN_DASH}{EN_DASH} 3 %": f"2 %{EN_DASH}3 %",
    f"2 % {EM_DASH}{EM_DASH} 3 %": f"2 %{EN_DASH}3 %",
    f"2 % {EM_DASH}{EM_DASH}{EM_DASH} 3 %": f"2 %{EN_DASH}3 %",
}


# English ordinal numbers
# Ported from dashOrdinalNumbersEnUsSet in dash.test.js
DASH_ORDINAL_NUMBERS_EN_US = {
    "1st-5th August": f"1st{EN_DASH}5th August",
    "1st -5th August": f"1st{EN_DASH}5th August",
    "1st- 5th August": f"1st{EN_DASH}5th August",
    "1st - 5th August": f"1st{EN_DASH}5th August",
    "1st -- 5th August": f"1st{EN_DASH}5th August",
    "1st --- 5th August": f"1st{EN_DASH}5th August",
}


# Other locales ordinal numbers (use . after number)
# Ported from dashOrdinalNumbersOtherLocalesSet in dash.test.js
DASH_ORDINAL_NUMBERS_OTHER_LOCALES = {
    "1.-5. augusta": f"1.{EN_DASH}5. augusta",
    "1. -5. augusta": f"1.{EN_DASH}5. augusta",
    "1.- 5. augusta": f"1.{EN_DASH}5. augusta",
    "1. - 5. augusta": f"1.{EN_DASH}5. augusta",
    "1. -- 5. augusta": f"1.{EN_DASH}5. augusta",
    "1. --- 5. augusta": f"1.{EN_DASH}5. augusta",
}


# =============================================================================
# Test Classes - Data-driven parametrized tests
# =============================================================================


class TestDashFalsePositives:
    """Tests for cases that should NOT be modified."""

    @pytest.mark.parametrize(("input_text", "expected"), DASH_FALSE_POSITIVES.items())
    def test_false_positives_fix_dash(self, input_text, expected, locale):
        """Patterns that look like dashes but should not be modified by fix_dash."""
        result = fix_dash(input_text, locale)
        assert result == expected

    @pytest.mark.parametrize(("input_text", "expected"), DASH_FALSE_POSITIVES.items())
    def test_false_positives_fix_dashes_between_words(self, input_text, expected, locale):
        """Patterns that look like dashes but should not be modified by fix_dashes_between_words."""
        result = fix_dashes_between_words(input_text, locale)
        assert result == expected


class TestDashesBetweenWords:
    """
    Tests for fix_dashes_between_words function.

    Ported from dashesBetweenWordsSet in dash.test.js.
    """

    @pytest.mark.parametrize(("input_text", "expected_template"), DASHES_BETWEEN_WORDS.items())
    def test_dashes_between_words(self, input_text, expected_template, locale):
        """Test all dash between words cases with locale-specific output."""
        expected = expand_template(expected_template, locale)
        result = fix_dashes_between_words(input_text, locale)
        assert result == expected

    @pytest.mark.parametrize(("input_text", "expected_template"), DASHES_BETWEEN_WORDS.items())
    def test_dashes_between_words_via_fix_dash(self, input_text, expected_template, locale):
        """Test all dash between words cases via main fix_dash function."""
        expected = expand_template(expected_template, locale)
        result = fix_dash(input_text, locale)
        assert result == expected


class TestDashBetweenWordAndPunctuation:
    """
    Tests for fix_dash_between_word_and_punctuation function.

    Ported from dashBetweenWordAndPunctuation in dash.test.js.
    """

    @pytest.mark.parametrize(("input_text", "expected_template"), DASH_BETWEEN_WORD_AND_PUNCTUATION.items())
    def test_dash_between_word_and_punctuation(self, input_text, expected_template, locale):
        """Test all dash between word and punctuation cases."""
        expected = expand_template(expected_template, locale)
        result = fix_dash_between_word_and_punctuation(input_text, locale)
        assert result == expected

    @pytest.mark.parametrize(("input_text", "expected_template"), DASH_BETWEEN_WORD_AND_PUNCTUATION.items())
    def test_dash_between_word_and_punctuation_via_fix_dash(self, input_text, expected_template, locale):
        """Test all dash between word and punctuation cases via main fix_dash function."""
        expected = expand_template(expected_template, locale)
        result = fix_dash(input_text, locale)
        assert result == expected

    # Also include false positives for this function
    @pytest.mark.parametrize(("input_text", "expected"), DASH_FALSE_POSITIVES.items())
    def test_false_positives(self, input_text, expected, locale):
        """False positives should remain unchanged."""
        result = fix_dash_between_word_and_punctuation(input_text, locale)
        assert result == expected


class TestDashBetweenWordAndBrackets:
    """
    Tests for fix_dash_between_word_and_brackets function.

    Ported from dashBetweenWordAndBrackets in dash.test.js.
    """

    @pytest.mark.parametrize(("input_text", "expected_template"), DASH_BETWEEN_WORD_AND_BRACKETS.items())
    def test_dash_between_word_and_brackets(self, input_text, expected_template, locale):
        """Test all dash between word and brackets cases."""
        expected = expand_template(expected_template, locale)
        result = fix_dash_between_word_and_brackets(input_text, locale)
        assert result == expected

    @pytest.mark.parametrize(("input_text", "expected_template"), DASH_BETWEEN_WORD_AND_BRACKETS.items())
    def test_dash_between_word_and_brackets_via_fix_dash(self, input_text, expected_template, locale):
        """Test all dash between word and brackets cases via main fix_dash function."""
        expected = expand_template(expected_template, locale)
        result = fix_dash(input_text, locale)
        assert result == expected

    # Also include false positives for this function
    @pytest.mark.parametrize(("input_text", "expected"), DASH_FALSE_POSITIVES.items())
    def test_false_positives(self, input_text, expected, locale):
        """False positives should remain unchanged."""
        result = fix_dash_between_word_and_brackets(input_text, locale)
        assert result == expected


class TestDashBetweenCardinalNumbers:
    """
    Tests for fix_dash_between_cardinal_numbers function.

    Ported from dashCardinalNumbersSet in dash.test.js.
    Note: This function is locale-independent (always uses en dash).
    """

    @pytest.mark.parametrize(("input_text", "expected"), DASH_CARDINAL_NUMBERS.items())
    def test_dash_between_cardinal_numbers(self, input_text, expected):
        """Test all cardinal number range cases."""
        result = fix_dash_between_cardinal_numbers(input_text)
        assert result == expected

    @pytest.mark.parametrize(("input_text", "expected"), DASH_CARDINAL_NUMBERS.items())
    def test_dash_between_cardinal_numbers_via_fix_dash(self, input_text, expected, locale):
        """Test all cardinal number range cases via main fix_dash function."""
        result = fix_dash(input_text, locale)
        assert result == expected


class TestDashBetweenPercentageRange:
    """
    Tests for fix_dash_between_percentage_range function.

    Ported from dashPercentageRangeSet in dash.test.js.
    Note: This function is locale-independent (always uses en dash).
    """

    @pytest.mark.parametrize(("input_text", "expected"), DASH_PERCENTAGE_RANGE.items())
    def test_dash_between_percentage_range(self, input_text, expected):
        """Test all percentage range cases."""
        result = fix_dash_between_percentage_range(input_text)
        assert result == expected

    @pytest.mark.parametrize(("input_text", "expected"), DASH_PERCENTAGE_RANGE.items())
    def test_dash_between_percentage_range_via_fix_dash(self, input_text, expected, locale):
        """Test all percentage range cases via main fix_dash function."""
        result = fix_dash(input_text, locale)
        assert result == expected


class TestDashBetweenOrdinalNumbers:
    """
    Tests for fix_dash_between_ordinal_numbers function.

    Ported from dashOrdinalNumbersEnUsSet and dashOrdinalNumbersOtherLocalesSet
    in dash.test.js.
    """

    @pytest.mark.parametrize(("input_text", "expected"), DASH_ORDINAL_NUMBERS_EN_US.items())
    def test_ordinal_numbers_english(self, input_text, expected):
        """Test English ordinal number ranges."""
        result = fix_dash_between_ordinal_numbers(input_text, "en-us")
        assert result == expected

    @pytest.mark.parametrize(("input_text", "expected"), DASH_ORDINAL_NUMBERS_EN_US.items())
    def test_ordinal_numbers_english_via_fix_dash(self, input_text, expected):
        """Test English ordinal number ranges via main fix_dash function."""
        result = fix_dash(input_text, "en-us")
        assert result == expected

    @pytest.mark.parametrize(("input_text", "expected"), DASH_ORDINAL_NUMBERS_OTHER_LOCALES.items())
    @pytest.mark.parametrize("loc", ["de-de", "cs", "sk", "rue"])
    def test_ordinal_numbers_other_locales(self, input_text, expected, loc):
        """Test European ordinal number ranges (period after number)."""
        result = fix_dash_between_ordinal_numbers(input_text, loc)
        assert result == expected

    @pytest.mark.parametrize(("input_text", "expected"), DASH_ORDINAL_NUMBERS_OTHER_LOCALES.items())
    @pytest.mark.parametrize("loc", ["de-de", "cs", "sk", "rue"])
    def test_ordinal_numbers_other_locales_via_fix_dash(self, input_text, expected, loc):
        """Test European ordinal number ranges via main fix_dash function."""
        result = fix_dash(input_text, loc)
        assert result == expected


class TestFixDash:
    """Integration tests for the main fix_dash function."""

    def test_combined_fixes(self, locale):
        """fix_dash should apply all dash fixes in sequence."""
        dash = expected_dash_between_words(locale)

        # Words with dash
        assert fix_dash("and - she said", locale) == f"and{dash}she said"

        # Cardinal number range (always en dash)
        assert fix_dash("5-6 eggs", locale) == f"5{EN_DASH}6 eggs"

        # Percentage range (always en dash)
        assert fix_dash("20%-30%", locale) == f"20%{EN_DASH}30%"

    def test_false_positives_preserved(self, locale):
        """False positives should remain unchanged."""
        assert fix_dash("e -shop", locale) == "e -shop"
        assert fix_dash("- she said", locale) == "- she said"
        assert fix_dash("{{test-variable}}", locale) == "{{test-variable}}"
        assert fix_dash("---", locale) == "---"

    def test_complex_sentence(self, locale):
        """Complex sentences with multiple dash patterns."""
        dash = expected_dash_between_words(locale)

        # Sentence with word dash and number range
        input_text = "We had 5-6 people - and they were happy."
        result = fix_dash(input_text, locale)
        expected = f"We had 5{EN_DASH}6 people{dash}and they were happy."
        assert result == expected
