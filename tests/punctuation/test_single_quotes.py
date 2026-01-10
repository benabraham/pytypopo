"""
Tests for single quotes, primes, and apostrophes fixes.

Port of tests/punctuation/single-quotes.test.js from typopo.
"""

import pytest

from pytypopo.const import APOSTROPHE, NBSP, SINGLE_PRIME
from pytypopo.locale import Locale
from pytypopo.modules.punctuation.single_quotes import (
    fix_single_quotes_primes_and_apostrophes,
    identify_contracted_and,
    identify_contracted_beginnings,
    identify_contracted_ends,
    identify_contracted_years,
    identify_in_word_contractions,
    identify_residual_apostrophes,
    identify_single_prime_as_feet,
    identify_single_quote_pair_around_single_word,
    identify_single_quote_pairs,
    identify_single_quotes_within_double_quotes,
    identify_unpaired_left_single_quote,
    identify_unpaired_right_single_quote,
    place_locale_single_quotes,
    remove_extra_space_around_single_prime,
    replace_single_prime_with_single_quote,
    swap_single_quotes_and_terminal_punctuation,
)
from tests.conftest import ALL_LOCALES


def get_quotes(locale_id):
    """Get locale-specific quote characters."""
    loc = Locale(locale_id)
    return {
        "lsq": loc.single_quote_open,
        "rsq": loc.single_quote_close,
        "ldq": loc.double_quote_open,
        "rdq": loc.double_quote_close,
    }


class TestIdentifyContractedAnd:
    """Identify 'n' contractions as apostrophes (rock 'n' roll)."""

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_rock_n_roll_with_spaces(self, locale_id):
        text = "rock 'n' roll"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"rock{NBSP}{APOSTROPHE}n{APOSTROPHE}{NBSP}roll"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_rock_n_roll_no_spaces(self, locale_id):
        text = "rock'n'roll"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"rock{NBSP}{APOSTROPHE}n{APOSTROPHE}{NBSP}roll"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_rock_n_roll_left_space(self, locale_id):
        text = "rock 'n'roll"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"rock{NBSP}{APOSTROPHE}n{APOSTROPHE}{NBSP}roll"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_rock_n_roll_right_space(self, locale_id):
        text = "rock'n' roll"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"rock{NBSP}{APOSTROPHE}n{APOSTROPHE}{NBSP}roll"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_rock_n_roll_low9_quote(self, locale_id):
        text = "rock \u201an\u2019 roll"  # low-9 and right single quote
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"rock{NBSP}{APOSTROPHE}n{APOSTROPHE}{NBSP}roll"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_rock_n_roll_modifier_letter_apostrophe(self, locale_id):
        text = "rock \u2019n\u02bc roll"  # right single quote and modifier letter apostrophe
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"rock{NBSP}{APOSTROPHE}n{APOSTROPHE}{NBSP}roll"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_rock_n_roll_reversed_prime(self, locale_id):
        text = "rock \u201bn\u2032 roll"  # high-reversed-9 and prime
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"rock{NBSP}{APOSTROPHE}n{APOSTROPHE}{NBSP}roll"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_rock_n_roll_guillemets(self, locale_id):
        text = "rock \u2039n\u203a roll"  # single guillemets
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"rock{NBSP}{APOSTROPHE}n{APOSTROPHE}{NBSP}roll"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_rock_n_roll_acute_backtick(self, locale_id):
        text = "rock \u00b4n` roll"  # acute accent and backtick
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"rock{NBSP}{APOSTROPHE}n{APOSTROPHE}{NBSP}roll"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_rock_n_roll_uppercase(self, locale_id):
        text = "ROCK 'N' ROLL"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"ROCK{NBSP}{APOSTROPHE}N{APOSTROPHE}{NBSP}ROLL"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_dead_n_buried(self, locale_id):
        text = "dead 'n' buried"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"dead{NBSP}{APOSTROPHE}n{APOSTROPHE}{NBSP}buried"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_drill_n_bass(self, locale_id):
        text = "drill 'n' bass"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"drill{NBSP}{APOSTROPHE}n{APOSTROPHE}{NBSP}bass"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_drum_n_bass(self, locale_id):
        text = "drum 'n' bass"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"drum{NBSP}{APOSTROPHE}n{APOSTROPHE}{NBSP}bass"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_pick_n_mix(self, locale_id):
        text = "pick 'n' mix"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"pick{NBSP}{APOSTROPHE}n{APOSTROPHE}{NBSP}mix"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_fish_n_chips(self, locale_id):
        text = "fish 'n' chips"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"fish{NBSP}{APOSTROPHE}n{APOSTROPHE}{NBSP}chips"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_salt_n_shake(self, locale_id):
        text = "salt 'n' shake"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"salt{NBSP}{APOSTROPHE}n{APOSTROPHE}{NBSP}shake"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_mac_n_cheese(self, locale_id):
        text = "mac 'n' cheese"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"mac{NBSP}{APOSTROPHE}n{APOSTROPHE}{NBSP}cheese"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_pork_n_beans(self, locale_id):
        text = "pork 'n' beans"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"pork{NBSP}{APOSTROPHE}n{APOSTROPHE}{NBSP}beans"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_drag_n_drop(self, locale_id):
        text = "drag 'n' drop"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"drag{NBSP}{APOSTROPHE}n{APOSTROPHE}{NBSP}drop"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_rake_n_scrape(self, locale_id):
        text = "rake 'n' scrape"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"rake{NBSP}{APOSTROPHE}n{APOSTROPHE}{NBSP}scrape"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_hook_n_kill(self, locale_id):
        text = "hook 'n' kill"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"hook{NBSP}{APOSTROPHE}n{APOSTROPHE}{NBSP}kill"


class TestIdentifyContractedBeginnings:
    """Identify common contractions at word beginning as apostrophes."""

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_cause(self, locale_id):
        text = "Just 'cause we wanna."
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"Just {APOSTROPHE}cause we wanna."

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_tis(self, locale_id):
        text = "'Tis the season"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"{APOSTROPHE}Tis the season"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_sblood(self, locale_id):
        text = "'sblood"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"{APOSTROPHE}sblood"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_mongst(self, locale_id):
        text = "'mongst"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"{APOSTROPHE}mongst"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_prentice(self, locale_id):
        text = "'prentice"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"{APOSTROPHE}prentice"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_slight(self, locale_id):
        text = "'slight"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"{APOSTROPHE}slight"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_strewth(self, locale_id):
        text = "'Strewth"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"{APOSTROPHE}Strewth"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_twixt(self, locale_id):
        text = "'Twixt"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"{APOSTROPHE}Twixt"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_shun(self, locale_id):
        text = "'shun"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"{APOSTROPHE}shun"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_slid(self, locale_id):
        text = "'slid"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"{APOSTROPHE}slid"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_em(self, locale_id):
        text = "Find 'em!"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"Find {APOSTROPHE}em!"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_twas(self, locale_id):
        text = "'Twas the Night Before Christmas"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"{APOSTROPHE}Twas the Night Before Christmas"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_til_and_round(self, locale_id):
        text = "'Til The Season Comes 'Round Again"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"{APOSTROPHE}Til The Season Comes {APOSTROPHE}Round Again"


class TestIdentifyContractedEnds:
    """Identify contractions at word end (e.g., nothin')."""

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_nottin(self, locale_id):
        text = "nottin'"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"nottin{APOSTROPHE}"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_gettin(self, locale_id):
        text = "gettin'"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"gettin{APOSTROPHE}"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_nottin_uppercase(self, locale_id):
        text = "NOTTIN'"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"NOTTIN{APOSTROPHE}"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_gettin_uppercase(self, locale_id):
        text = "GETTIN'"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"GETTIN{APOSTROPHE}"


class TestIdentifyInWordContractions:
    """Identify in-word contractions as apostrophes (don't, I'm, O'Doole)."""

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_69ers(self, locale_id):
        text = "69'ers"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"69{APOSTROPHE}ers"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_iphone6s(self, locale_id):
        text = "iPhone6's"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"iPhone6{APOSTROPHE}s"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_1990s(self, locale_id):
        text = "1990's"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"1990{APOSTROPHE}s"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_dont(self, locale_id):
        text = "don't"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"don{APOSTROPHE}t"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_dont_double_quote(self, locale_id):
        text = "don''t"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"don{APOSTROPHE}t"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_dont_triple_quote(self, locale_id):
        text = "don'''t"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"don{APOSTROPHE}t"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_pauls_diner_straight_quote(self, locale_id):
        text = "Paul's Diner"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"Paul{APOSTROPHE}s Diner"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_pauls_diner_modifier_apostrophe(self, locale_id):
        text = "Paul\u02bcs Diner"  # modifier letter apostrophe
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"Paul{APOSTROPHE}s Diner"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_pauls_diner_reversed_9(self, locale_id):
        text = "Paul\u201bs Diner"  # high-reversed-9 quotation mark
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"Paul{APOSTROPHE}s Diner"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_pauls_diner_backtick(self, locale_id):
        text = "Paul`s Diner"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"Paul{APOSTROPHE}s Diner"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_pauls_diner_low9(self, locale_id):
        text = "Paul\u201as Diner"  # low-9 quotation mark
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"Paul{APOSTROPHE}s Diner"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_pauls_diner_acute(self, locale_id):
        text = "Paul\u00b4s Diner"  # acute accent
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"Paul{APOSTROPHE}s Diner"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_im_quadruple_quote(self, locale_id):
        text = "I''''m"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"I{APOSTROPHE}m"


class TestIdentifyContractedYears:
    """Identify contracted years (e.g., '70s, '89)."""

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_incheba_89(self, locale_id):
        text = "INCHEBA '89"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"INCHEBA {APOSTROPHE}89"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_in_70s(self, locale_id):
        text = "in '70s"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"in {APOSTROPHE}70s"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_q1_23(self, locale_id):
        text = "Q1 '23"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"Q1 {APOSTROPHE}23"


class TestIdentifySinglePrimes:
    """Identify feet and arcminutes following numbers."""

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_12_feet_45_inches_with_space(self, locale_id):
        text = "12 ' 45\u2033"  # 12 ' 45″
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"12{SINGLE_PRIME} 45\u2033"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_12_feet_reversed_9(self, locale_id):
        text = "12 \u201b 45\u2033"  # 12 ‛ 45″
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"12{SINGLE_PRIME} 45\u2033"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_12_feet_prime(self, locale_id):
        text = "12 \u2032 45\u2033"  # 12 ′ 45″
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"12{SINGLE_PRIME} 45\u2033"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_12_feet_reversed_9_no_space(self, locale_id):
        text = "12 \u201b45\u2033"  # 12 ‛45″
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"12{SINGLE_PRIME}45\u2033"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_12_feet_straight_no_space(self, locale_id):
        text = "12 '45\u2033"  # 12 '45″
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"12{SINGLE_PRIME}45\u2033"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_12_feet_adjacent(self, locale_id):
        text = "12' 45\u2033"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"12{SINGLE_PRIME} 45\u2033"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_12_feet_reversed_9_adjacent(self, locale_id):
        text = "12\u201b 45\u2033"  # 12‛ 45″
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"12{SINGLE_PRIME} 45\u2033"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_12_feet_prime_adjacent(self, locale_id):
        text = "12\u2032 45\u2033"  # 12′ 45″ (already correct)
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"12{SINGLE_PRIME} 45\u2033"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_12_feet_no_space_after(self, locale_id):
        text = "12'45\u2033"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"12{SINGLE_PRIME}45\u2033"


class TestIdentifyResidualApostrophes:
    """Identify residual apostrophes."""

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_hers(self, locale_id):
        text = "Hers'"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"Hers{APOSTROPHE}"


class TestRemoveExtraSpaceAroundSinglePrime:
    """Remove extra space around single primes."""

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_remove_space_before_prime(self, locale_id):
        text = f"12 {SINGLE_PRIME} 45\u2033"  # 12 ′ 45″
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"12{SINGLE_PRIME} 45\u2033"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_remove_space_before_prime_no_trailing_space(self, locale_id):
        text = f"12 {SINGLE_PRIME}45\u2033"  # 12 ′45″
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"12{SINGLE_PRIME}45\u2033"


class TestIdentifySingleQuotePairAroundSingleWord:
    """Identify single quote pairs around single words."""

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_single_word(self, locale_id):
        q = get_quotes(locale_id)
        text = "'word'"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"{q['lsq']}word{q['rsq']}"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_two_single_words(self, locale_id):
        q = get_quotes(locale_id)
        text = "'word' 'word'"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"{q['lsq']}word{q['rsq']} {q['lsq']}word{q['rsq']}"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_single_letter_n(self, locale_id):
        q = get_quotes(locale_id)
        text = "Press 'N' to get started"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"Press {q['lsq']}N{q['rsq']} to get started"


class TestIdentifySingleQuotePairAroundSingleWordFalsePositives:
    """False positives for single quote pairs around single word."""

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_dont_at_end(self, locale_id):
        """Don't treat apostrophe in don't as closing quote."""
        text = "... don't'"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        # The apostrophe in don't should remain an apostrophe
        assert f"don{APOSTROPHE}t{APOSTROPHE}" in result

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_dont_at_start(self, locale_id):
        """Don't treat apostrophe in don't as opening quote."""
        text = "'don't ..."
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        # The apostrophe in don't should remain an apostrophe
        assert f"{APOSTROPHE}don{APOSTROPHE}t" in result

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_multiple_words(self, locale_id):
        """Multiple words not identified as single word quote pair."""
        text = "'word word'"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        # This should become apostrophes, not quotes, without double quote context
        assert f"{APOSTROPHE}word word{APOSTROPHE}" in result


class TestSwapSingleQuotesAndTerminalPunctuation:
    """Swap single quotes and terminal punctuation."""

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_quoted_part_period_inside(self, locale_id):
        """Move period outside of quoted part."""
        q = get_quotes(locale_id)
        text = f"Sometimes it can be only a {q['lsq']}quoted part.{q['rsq']}"
        expected = f"Sometimes it can be only a {q['lsq']}quoted part{q['rsq']}."
        result = swap_single_quotes_and_terminal_punctuation(text, Locale(locale_id))
        assert result == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_two_quoted_parts(self, locale_id):
        """Move periods outside of two quoted parts."""
        q = get_quotes(locale_id)
        text = f"Sometimes it can be only a {q['lsq']}quoted{q['rsq']} {q['lsq']}part.{q['rsq']}"
        expected = f"Sometimes it can be only a {q['lsq']}quoted{q['rsq']} {q['lsq']}part{q['rsq']}."
        result = swap_single_quotes_and_terminal_punctuation(text, Locale(locale_id))
        assert result == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_whole_sentence_then_quoted_part(self, locale_id):
        """Whole sentence keeps period, quoted part moves it."""
        q = get_quotes(locale_id)
        text = f"{q['lsq']}A whole sentence.{q['rsq']} Only a {q['lsq']}quoted part.{q['rsq']}"
        expected = f"{q['lsq']}A whole sentence.{q['rsq']} Only a {q['lsq']}quoted part{q['rsq']}."
        result = swap_single_quotes_and_terminal_punctuation(text, Locale(locale_id))
        assert result == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_question_outside_quoted_part(self, locale_id):
        """Question mark stays outside quoted part."""
        q = get_quotes(locale_id)
        text = f"Is it {q['lsq']}Amores Perros{q['rsq']}?"
        # Question mark stays outside
        result = swap_single_quotes_and_terminal_punctuation(text, Locale(locale_id))
        assert result == text

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_period_outside_title(self, locale_id):
        """Period stays outside quoted title."""
        q = get_quotes(locale_id)
        text = f"Look for {q['lsq']}Anguanga{q['rsq']}."
        # Period stays outside
        result = swap_single_quotes_and_terminal_punctuation(text, Locale(locale_id))
        assert result == text

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_two_quoted_parts_periods(self, locale_id):
        """Two quoted parts both move periods outside."""
        q = get_quotes(locale_id)
        text = f"a {q['lsq']}quoted part.{q['rsq']} A {q['lsq']}quoted part.{q['rsq']}"
        expected = f"a {q['lsq']}quoted part{q['rsq']}. A {q['lsq']}quoted part{q['rsq']}."
        result = swap_single_quotes_and_terminal_punctuation(text, Locale(locale_id))
        assert result == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_quoted_part_then_whole_sentence(self, locale_id):
        """Quoted part moves period, whole sentence keeps it."""
        q = get_quotes(locale_id)
        text = f"Only a {q['lsq']}quoted part.{q['rsq']} {q['lsq']}A whole sentence.{q['rsq']}"
        expected = f"Only a {q['lsq']}quoted part{q['rsq']}. {q['lsq']}A whole sentence.{q['rsq']}"
        result = swap_single_quotes_and_terminal_punctuation(text, Locale(locale_id))
        assert result == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_quoted_part_in_sentence_then_whole_sentence(self, locale_id):
        """Quoted part in middle, then whole sentence at end."""
        q = get_quotes(locale_id)
        text = f"Only a {q['lsq']}quoted part{q['rsq']} in a sentence. {q['lsq']}A whole sentence.{q['rsq']}"
        # No change - first is not followed by punct, second is whole sentence
        result = swap_single_quotes_and_terminal_punctuation(text, Locale(locale_id))
        assert result == text

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_question_inside_quoted_part(self, locale_id):
        """Move question mark inside when followed by lowercase."""
        q = get_quotes(locale_id)
        text = f"Ask {q['lsq']}What{APOSTROPHE}s going on in here{q['rsq']}? so you can dig deeper."
        expected = f"Ask {q['lsq']}What{APOSTROPHE}s going on in here?{q['rsq']} so you can dig deeper."
        result = swap_single_quotes_and_terminal_punctuation(text, Locale(locale_id))
        assert result == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_ellipsis_in_quoted_part_at_end(self, locale_id):
        """Ellipsis inside quoted part stays inside."""
        q = get_quotes(locale_id)
        text = f"Before you ask the {q['lsq']}How often\u2026{q['rsq']} question"
        # No change
        result = swap_single_quotes_and_terminal_punctuation(text, Locale(locale_id))
        assert result == text

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_ellipsis_at_start(self, locale_id):
        """Ellipsis at start of quoted part stays."""
        q = get_quotes(locale_id)
        text = f"{q['lsq']}\u2026example{q['rsq']}"
        result = swap_single_quotes_and_terminal_punctuation(text, Locale(locale_id))
        assert result == text

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_ellipsis_at_start_with_prefix(self, locale_id):
        """Ellipsis at start of quoted part with prefix stays."""
        q = get_quotes(locale_id)
        text = f"abc {q['lsq']}\u2026example{q['rsq']}"
        result = swap_single_quotes_and_terminal_punctuation(text, Locale(locale_id))
        assert result == text

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_whole_sentence_after_period(self, locale_id):
        """Whole quoted sentence after period moves punct inside."""
        q = get_quotes(locale_id)
        text = f"He was ok. {q['lsq']}He was ok{q['rsq']}."
        expected = f"He was ok. {q['lsq']}He was ok.{q['rsq']}"
        result = swap_single_quotes_and_terminal_punctuation(text, Locale(locale_id))
        assert result == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_whole_sentence_middle(self, locale_id):
        """Whole quoted sentence in middle moves punct inside."""
        q = get_quotes(locale_id)
        text = f"He was ok. {q['lsq']}He was ok{q['rsq']}. He was ok."
        expected = f"He was ok. {q['lsq']}He was ok.{q['rsq']} He was ok."
        result = swap_single_quotes_and_terminal_punctuation(text, Locale(locale_id))
        assert result == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_whole_sentence_after_question(self, locale_id):
        """Whole quoted sentence after question moves punct inside."""
        q = get_quotes(locale_id)
        text = f"He was ok? {q['lsq']}He was ok{q['rsq']}."
        expected = f"He was ok? {q['lsq']}He was ok.{q['rsq']}"
        result = swap_single_quotes_and_terminal_punctuation(text, Locale(locale_id))
        assert result == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_whole_sentence_at_start_period(self, locale_id):
        """Whole quoted sentence at start moves period inside."""
        q = get_quotes(locale_id)
        text = f"{q['lsq']}He was ok{q['rsq']}."
        expected = f"{q['lsq']}He was ok.{q['rsq']}"
        result = swap_single_quotes_and_terminal_punctuation(text, Locale(locale_id))
        assert result == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_whole_sentence_at_start_question(self, locale_id):
        """Whole quoted sentence at start moves question inside."""
        q = get_quotes(locale_id)
        text = f"{q['lsq']}He was ok{q['rsq']}?"
        expected = f"{q['lsq']}He was ok?{q['rsq']}"
        result = swap_single_quotes_and_terminal_punctuation(text, Locale(locale_id))
        assert result == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_whole_sentence_at_start_followed_by_sentence(self, locale_id):
        """Whole quoted sentence at start followed by another sentence."""
        q = get_quotes(locale_id)
        text = f"{q['lsq']}He was ok{q['rsq']}. He was ok."
        expected = f"{q['lsq']}He was ok.{q['rsq']} He was ok."
        result = swap_single_quotes_and_terminal_punctuation(text, Locale(locale_id))
        assert result == expected


class TestIdentifyUnpairedLeftSingleQuote:
    """Unit tests for identify_unpaired_left_single_quote."""

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_space_straight_quote(self, locale_id):
        text = '" \'word"'
        result = identify_unpaired_left_single_quote(text, Locale(locale_id))
        assert "{{typopo__lsq--unpaired}}" in result

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_space_low9_quote(self, locale_id):
        text = '" \u201aword"'  # low-9 quotation mark
        result = identify_unpaired_left_single_quote(text, Locale(locale_id))
        assert "{{typopo__lsq--unpaired}}" in result

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_space_right_single_quote(self, locale_id):
        text = " 'word"  # right single quotation mark
        result = identify_unpaired_left_single_quote(text, Locale(locale_id))
        assert "{{typopo__lsq--unpaired}}" in result

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_en_dash(self, locale_id):
        text = "\u2013'word"  # en dash
        result = identify_unpaired_left_single_quote(text, Locale(locale_id))
        assert "{{typopo__lsq--unpaired}}" in result

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_em_dash(self, locale_id):
        text = "\u2014'word"  # em dash
        result = identify_unpaired_left_single_quote(text, Locale(locale_id))
        assert "{{typopo__lsq--unpaired}}" in result


class TestIdentifyUnpairedRightSingleQuote:
    """Unit tests for identify_unpaired_right_single_quote."""

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_word_straight_quote(self, locale_id):
        text = '"word\'"'
        result = identify_unpaired_right_single_quote(text, Locale(locale_id))
        assert "{{typopo__rsq--unpaired}}" in result

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_word_low9_quote(self, locale_id):
        text = '"word\u201a"'  # low-9 quotation mark
        result = identify_unpaired_right_single_quote(text, Locale(locale_id))
        assert "{{typopo__rsq--unpaired}}" in result

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_word_quote(self, locale_id):
        text = "word'"
        result = identify_unpaired_right_single_quote(text, Locale(locale_id))
        assert "{{typopo__rsq--unpaired}}" in result

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_word_period_quote(self, locale_id):
        text = "word.'"
        result = identify_unpaired_right_single_quote(text, Locale(locale_id))
        assert "{{typopo__rsq--unpaired}}" in result

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_word_exclamation_quote(self, locale_id):
        text = "word!'"
        result = identify_unpaired_right_single_quote(text, Locale(locale_id))
        assert "{{typopo__rsq--unpaired}}" in result


class TestIdentifySingleQuotePairs:
    """Unit tests for identify_single_quote_pairs."""

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_unpaired_to_paired(self, locale_id):
        text = "{{typopo__lsq--unpaired}}word{{typopo__rsq--unpaired}}"
        result = identify_single_quote_pairs(text, Locale(locale_id))
        assert result == "{{typopo__lsq}}word{{typopo__rsq}}"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_unpaired_multiple_words_to_paired(self, locale_id):
        text = "{{typopo__lsq--unpaired}}word word{{typopo__rsq--unpaired}}"
        result = identify_single_quote_pairs(text, Locale(locale_id))
        assert result == "{{typopo__lsq}}word word{{typopo__rsq}}"


class TestReplaceSinglePrimeWithSingleQuote:
    """Unit tests for replace_single_prime_with_single_quote."""

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_unpaired_left_and_prime(self, locale_id):
        text = "{{typopo__lsq--unpaired}}word{{typopo__single-prime}}"
        result = replace_single_prime_with_single_quote(text, Locale(locale_id))
        assert result == "{{typopo__lsq}}word{{typopo__rsq}}"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_prime_and_unpaired_right(self, locale_id):
        text = "{{typopo__single-prime}}word{{typopo__rsq--unpaired}}"
        result = replace_single_prime_with_single_quote(text, Locale(locale_id))
        assert result == "{{typopo__lsq}}word{{typopo__rsq}}"


class TestPlaceLocaleSingleQuotes:
    """Unit tests for place_locale_single_quotes."""

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_place_quote_pair(self, locale_id):
        q = get_quotes(locale_id)
        text = "{{typopo__lsq}}word{{typopo__rsq}}"
        result = place_locale_single_quotes(text, Locale(locale_id))
        assert result == f"{q['lsq']}word{q['rsq']}"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_place_apostrophe(self, locale_id):
        text = "{{typopo__apostrophe}}"
        result = place_locale_single_quotes(text, Locale(locale_id))
        assert result == APOSTROPHE

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_place_single_prime(self, locale_id):
        text = "{{typopo__single-prime}}"
        result = place_locale_single_quotes(text, Locale(locale_id))
        assert result == SINGLE_PRIME


# =============================================================================
# Unit tests for helper functions (testing intermediate placeholder states)
# =============================================================================


class TestIdentifyContractedAndUnit:
    """Unit tests for identify_contracted_and function."""

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_rock_n_roll_with_spaces(self, locale_id):
        text = "rock 'n' roll"
        result = identify_contracted_and(text, Locale(locale_id))
        assert "{{typopo__apostrophe}}" in result
        assert f"rock{NBSP}{{{{typopo__apostrophe}}}}n{{{{typopo__apostrophe}}}}{NBSP}roll" == result

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_rock_n_roll_no_spaces(self, locale_id):
        text = "rock'n'roll"
        result = identify_contracted_and(text, Locale(locale_id))
        assert f"rock{NBSP}{{{{typopo__apostrophe}}}}n{{{{typopo__apostrophe}}}}{NBSP}roll" == result

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_rock_n_roll_left_space_only(self, locale_id):
        text = "rock 'n'roll"
        result = identify_contracted_and(text, Locale(locale_id))
        assert f"rock{NBSP}{{{{typopo__apostrophe}}}}n{{{{typopo__apostrophe}}}}{NBSP}roll" == result

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_rock_n_roll_right_space_only(self, locale_id):
        text = "rock'n' roll"
        result = identify_contracted_and(text, Locale(locale_id))
        assert f"rock{NBSP}{{{{typopo__apostrophe}}}}n{{{{typopo__apostrophe}}}}{NBSP}roll" == result

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_rock_n_roll_low9_quote(self, locale_id):
        text = "rock \u201an\u2019 roll"  # low-9 and right single quote
        result = identify_contracted_and(text, Locale(locale_id))
        assert f"rock{NBSP}{{{{typopo__apostrophe}}}}n{{{{typopo__apostrophe}}}}{NBSP}roll" == result

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_rock_n_roll_guillemets(self, locale_id):
        text = "rock \u2039n\u203a roll"  # single guillemets
        result = identify_contracted_and(text, Locale(locale_id))
        assert f"rock{NBSP}{{{{typopo__apostrophe}}}}n{{{{typopo__apostrophe}}}}{NBSP}roll" == result

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_rock_n_roll_acute_backtick(self, locale_id):
        text = "rock \u00b4n` roll"  # acute accent and backtick
        result = identify_contracted_and(text, Locale(locale_id))
        assert f"rock{NBSP}{{{{typopo__apostrophe}}}}n{{{{typopo__apostrophe}}}}{NBSP}roll" == result

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_uppercase(self, locale_id):
        text = "ROCK 'N' ROLL"
        result = identify_contracted_and(text, Locale(locale_id))
        assert f"ROCK{NBSP}{{{{typopo__apostrophe}}}}N{{{{typopo__apostrophe}}}}{NBSP}ROLL" == result

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_fish_n_chips(self, locale_id):
        text = "fish 'n' chips"
        result = identify_contracted_and(text, Locale(locale_id))
        assert f"fish{NBSP}{{{{typopo__apostrophe}}}}n{{{{typopo__apostrophe}}}}{NBSP}chips" == result

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_mac_n_cheese(self, locale_id):
        text = "mac 'n' cheese"
        result = identify_contracted_and(text, Locale(locale_id))
        assert f"mac{NBSP}{{{{typopo__apostrophe}}}}n{{{{typopo__apostrophe}}}}{NBSP}cheese" == result

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_drag_n_drop(self, locale_id):
        text = "drag 'n' drop"
        result = identify_contracted_and(text, Locale(locale_id))
        assert f"drag{NBSP}{{{{typopo__apostrophe}}}}n{{{{typopo__apostrophe}}}}{NBSP}drop" == result

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_false_positive_n_button(self, locale_id):
        """Press 'n' button should NOT be matched as contracted and."""
        text = "Press 'n' button"
        result = identify_contracted_and(text, Locale(locale_id))
        # Should remain unchanged - not a known 'n' contraction
        assert result == text


class TestIdentifyContractedBeginningsUnit:
    """Unit tests for identify_contracted_beginnings function."""

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_cause(self, locale_id):
        text = "Just 'cause we wanna."
        result = identify_contracted_beginnings(text, Locale(locale_id))
        assert result == "Just {{typopo__apostrophe}}cause we wanna."

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_tis(self, locale_id):
        text = "'Tis the season"
        result = identify_contracted_beginnings(text, Locale(locale_id))
        assert result == "{{typopo__apostrophe}}Tis the season"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_sblood(self, locale_id):
        text = "'sblood"
        result = identify_contracted_beginnings(text, Locale(locale_id))
        assert result == "{{typopo__apostrophe}}sblood"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_mongst(self, locale_id):
        text = "'mongst"
        result = identify_contracted_beginnings(text, Locale(locale_id))
        assert result == "{{typopo__apostrophe}}mongst"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_prentice(self, locale_id):
        text = "'prentice"
        result = identify_contracted_beginnings(text, Locale(locale_id))
        assert result == "{{typopo__apostrophe}}prentice"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_slight(self, locale_id):
        text = "'slight"
        result = identify_contracted_beginnings(text, Locale(locale_id))
        assert result == "{{typopo__apostrophe}}slight"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_strewth(self, locale_id):
        text = "'Strewth"
        result = identify_contracted_beginnings(text, Locale(locale_id))
        assert result == "{{typopo__apostrophe}}Strewth"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_twixt(self, locale_id):
        text = "'Twixt"
        result = identify_contracted_beginnings(text, Locale(locale_id))
        assert result == "{{typopo__apostrophe}}Twixt"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_shun(self, locale_id):
        text = "'shun"
        result = identify_contracted_beginnings(text, Locale(locale_id))
        assert result == "{{typopo__apostrophe}}shun"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_slid(self, locale_id):
        text = "'slid"
        result = identify_contracted_beginnings(text, Locale(locale_id))
        assert result == "{{typopo__apostrophe}}slid"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_em(self, locale_id):
        text = "Find 'em!"
        result = identify_contracted_beginnings(text, Locale(locale_id))
        assert result == "Find {{typopo__apostrophe}}em!"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_twas(self, locale_id):
        text = "'Twas the Night Before Christmas"
        result = identify_contracted_beginnings(text, Locale(locale_id))
        assert result == "{{typopo__apostrophe}}Twas the Night Before Christmas"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_til_and_round(self, locale_id):
        text = "'Til The Season Comes 'Round Again"
        result = identify_contracted_beginnings(text, Locale(locale_id))
        assert result == "{{typopo__apostrophe}}Til The Season Comes {{typopo__apostrophe}}Round Again"


class TestIdentifyContractedEndsUnit:
    """Unit tests for identify_contracted_ends function."""

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_nottin(self, locale_id):
        text = "nottin'"
        result = identify_contracted_ends(text, Locale(locale_id))
        assert result == "nottin{{typopo__apostrophe}}"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_gettin(self, locale_id):
        text = "gettin'"
        result = identify_contracted_ends(text, Locale(locale_id))
        assert result == "gettin{{typopo__apostrophe}}"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_nottin_uppercase(self, locale_id):
        text = "NOTTIN'"
        result = identify_contracted_ends(text, Locale(locale_id))
        assert result == "NOTTIN{{typopo__apostrophe}}"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_gettin_uppercase(self, locale_id):
        text = "GETTIN'"
        result = identify_contracted_ends(text, Locale(locale_id))
        assert result == "GETTIN{{typopo__apostrophe}}"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_false_positive_something_in(self, locale_id):
        """'something in' should NOT be matched as contracted end.

        The word 'in' at the end is a separate word, not a contracted -ing ending.
        Only words like nottin' (nottin+g) and gettin' (gettin+g) should match.
        """
        text = "'something in'"
        result = identify_contracted_ends(text, Locale(locale_id))
        # The 'in' here is a standalone word, not a contracted end like nottin'
        # So it should remain unchanged
        assert result == text


class TestIdentifyInWordContractionsUnit:
    """Unit tests for identify_in_word_contractions function."""

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_69ers(self, locale_id):
        text = "69'ers"
        result = identify_in_word_contractions(text, Locale(locale_id))
        assert result == "69{{typopo__apostrophe}}ers"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_iphone6s(self, locale_id):
        text = "iPhone6's"
        result = identify_in_word_contractions(text, Locale(locale_id))
        assert result == "iPhone6{{typopo__apostrophe}}s"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_1990s(self, locale_id):
        text = "1990's"
        result = identify_in_word_contractions(text, Locale(locale_id))
        assert result == "1990{{typopo__apostrophe}}s"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_dont(self, locale_id):
        text = "don't"
        result = identify_in_word_contractions(text, Locale(locale_id))
        assert result == "don{{typopo__apostrophe}}t"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_dont_double_quote(self, locale_id):
        text = "don''t"
        result = identify_in_word_contractions(text, Locale(locale_id))
        assert result == "don{{typopo__apostrophe}}t"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_dont_triple_quote(self, locale_id):
        text = "don'''t"
        result = identify_in_word_contractions(text, Locale(locale_id))
        assert result == "don{{typopo__apostrophe}}t"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_pauls_diner_straight(self, locale_id):
        text = "Paul's Diner"
        result = identify_in_word_contractions(text, Locale(locale_id))
        assert result == "Paul{{typopo__apostrophe}}s Diner"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_pauls_diner_curly(self, locale_id):
        text = "Paul\u2019s Diner"  # right single quotation mark
        result = identify_in_word_contractions(text, Locale(locale_id))
        assert result == "Paul{{typopo__apostrophe}}s Diner"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_pauls_diner_modifier_apostrophe(self, locale_id):
        text = "Paul\u02bcs Diner"  # modifier letter apostrophe
        result = identify_in_word_contractions(text, Locale(locale_id))
        assert result == "Paul{{typopo__apostrophe}}s Diner"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_pauls_diner_reversed_9(self, locale_id):
        text = "Paul\u201bs Diner"  # high-reversed-9 quotation mark
        result = identify_in_word_contractions(text, Locale(locale_id))
        assert result == "Paul{{typopo__apostrophe}}s Diner"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_pauls_diner_backtick(self, locale_id):
        text = "Paul`s Diner"
        result = identify_in_word_contractions(text, Locale(locale_id))
        assert result == "Paul{{typopo__apostrophe}}s Diner"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_pauls_diner_low9(self, locale_id):
        text = "Paul\u201as Diner"  # low-9 quotation mark
        result = identify_in_word_contractions(text, Locale(locale_id))
        assert result == "Paul{{typopo__apostrophe}}s Diner"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_pauls_diner_acute(self, locale_id):
        text = "Paul\u00b4s Diner"  # acute accent
        result = identify_in_word_contractions(text, Locale(locale_id))
        assert result == "Paul{{typopo__apostrophe}}s Diner"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_im_quadruple_quote(self, locale_id):
        text = "I''''m"
        result = identify_in_word_contractions(text, Locale(locale_id))
        assert result == "I{{typopo__apostrophe}}m"


class TestIdentifyContractedYearsUnit:
    """Unit tests for identify_contracted_years function."""

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_incheba_89(self, locale_id):
        text = "INCHEBA '89"
        result = identify_contracted_years(text, Locale(locale_id))
        assert result == "INCHEBA {{typopo__apostrophe}}89"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_in_70s(self, locale_id):
        text = "in '70s"
        result = identify_contracted_years(text, Locale(locale_id))
        assert result == "in {{typopo__apostrophe}}70s"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_q1_23(self, locale_id):
        text = "Q1 '23"
        result = identify_contracted_years(text, Locale(locale_id))
        assert result == "Q1 {{typopo__apostrophe}}23"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_false_positive_feet(self, locale_id):
        """12 '45" should NOT be matched as contracted year."""
        text = "12 '45\u2033"  # 12 '45″
        result = identify_contracted_years(text, Locale(locale_id))
        # Should remain unchanged - this is feet/inches, not a year
        assert result == text


class TestIdentifySinglePrimeAsFeetUnit:
    """Unit tests for identify_single_prime_as_feet function."""

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_12_feet_45_inches_with_space_before_quote(self, locale_id):
        text = "12 ' 45\u2033"  # 12 ' 45″
        result = identify_single_prime_as_feet(text, Locale(locale_id))
        assert result == "12 {{typopo__single-prime}} 45\u2033"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_12_feet_adjacent(self, locale_id):
        text = "12' 45\u2033"
        result = identify_single_prime_as_feet(text, Locale(locale_id))
        assert result == "12{{typopo__single-prime}} 45\u2033"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_12_feet_curly_quote_adjacent(self, locale_id):
        text = "12\u2019 45\u2033"  # 12' 45″ with curly quote
        result = identify_single_prime_as_feet(text, Locale(locale_id))
        assert result == "12{{typopo__single-prime}} 45\u2033"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_12_feet_left_quote_adjacent(self, locale_id):
        text = "12\u2018 45\u2033"  # 12' 45″ with left curly quote
        result = identify_single_prime_as_feet(text, Locale(locale_id))
        assert result == "12{{typopo__single-prime}} 45\u2033"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_12_feet_reversed_9_adjacent(self, locale_id):
        text = "12\u201b 45\u2033"  # 12‛ 45″
        result = identify_single_prime_as_feet(text, Locale(locale_id))
        assert result == "12{{typopo__single-prime}} 45\u2033"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_12_feet_prime_adjacent(self, locale_id):
        text = "12\u2032 45\u2033"  # 12′ 45″
        result = identify_single_prime_as_feet(text, Locale(locale_id))
        assert result == "12{{typopo__single-prime}} 45\u2033"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_12_feet_no_space(self, locale_id):
        text = "12'45\u2033"
        result = identify_single_prime_as_feet(text, Locale(locale_id))
        assert result == "12{{typopo__single-prime}}45\u2033"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_12_feet_space_before_no_space_after(self, locale_id):
        text = "12 '45\u2033"
        result = identify_single_prime_as_feet(text, Locale(locale_id))
        assert result == "12 {{typopo__single-prime}}45\u2033"


class TestIdentifyUnpairedLeftSingleQuoteUnit:
    """Unit tests for identify_unpaired_left_single_quote function."""

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_space_straight_quote(self, locale_id):
        text = '" \'word"'
        result = identify_unpaired_left_single_quote(text, Locale(locale_id))
        assert result == '" {{typopo__lsq--unpaired}}word"'

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_space_low9_quote(self, locale_id):
        text = '" \u201aword"'  # low-9 quotation mark
        result = identify_unpaired_left_single_quote(text, Locale(locale_id))
        assert result == '" {{typopo__lsq--unpaired}}word"'

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_space_right_single_quote(self, locale_id):
        text = " 'word"  # right single quotation mark (U+2019)
        result = identify_unpaired_left_single_quote(text, Locale(locale_id))
        assert result == " {{typopo__lsq--unpaired}}word"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_en_dash(self, locale_id):
        text = "\u2013'word"  # en dash
        result = identify_unpaired_left_single_quote(text, Locale(locale_id))
        assert result == "\u2013{{typopo__lsq--unpaired}}word"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_em_dash(self, locale_id):
        text = "\u2014'word"  # em dash
        result = identify_unpaired_left_single_quote(text, Locale(locale_id))
        assert result == "\u2014{{typopo__lsq--unpaired}}word"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_modifier_apostrophe(self, locale_id):
        text = " \u02bcword"  # modifier letter apostrophe
        result = identify_unpaired_left_single_quote(text, Locale(locale_id))
        assert result == " {{typopo__lsq--unpaired}}word"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_reversed_9(self, locale_id):
        text = " \u201bword"  # high-reversed-9 quotation mark
        result = identify_unpaired_left_single_quote(text, Locale(locale_id))
        assert result == " {{typopo__lsq--unpaired}}word"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_acute_accent(self, locale_id):
        text = " \u00b4word"  # acute accent
        result = identify_unpaired_left_single_quote(text, Locale(locale_id))
        assert result == " {{typopo__lsq--unpaired}}word"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_backtick(self, locale_id):
        text = " `word"
        result = identify_unpaired_left_single_quote(text, Locale(locale_id))
        assert result == " {{typopo__lsq--unpaired}}word"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_prime(self, locale_id):
        text = " \u2032word"  # prime
        result = identify_unpaired_left_single_quote(text, Locale(locale_id))
        assert result == " {{typopo__lsq--unpaired}}word"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_left_guillemet(self, locale_id):
        text = " \u2039word"  # single left-pointing angle quotation mark
        result = identify_unpaired_left_single_quote(text, Locale(locale_id))
        assert result == " {{typopo__lsq--unpaired}}word"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_right_guillemet(self, locale_id):
        text = " \u203aword"  # single right-pointing angle quotation mark
        result = identify_unpaired_left_single_quote(text, Locale(locale_id))
        assert result == " {{typopo__lsq--unpaired}}word"


class TestIdentifyUnpairedRightSingleQuoteUnit:
    """Unit tests for identify_unpaired_right_single_quote function."""

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_word_straight_quote_in_double_quotes(self, locale_id):
        text = '"word\'"'
        result = identify_unpaired_right_single_quote(text, Locale(locale_id))
        assert result == '"word{{typopo__rsq--unpaired}}"'

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_word_low9_quote(self, locale_id):
        text = '"word\u201a"'  # low-9 quotation mark
        result = identify_unpaired_right_single_quote(text, Locale(locale_id))
        assert result == '"word{{typopo__rsq--unpaired}}"'

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_word_straight_quote(self, locale_id):
        text = "word'"
        result = identify_unpaired_right_single_quote(text, Locale(locale_id))
        assert result == "word{{typopo__rsq--unpaired}}"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_word_modifier_apostrophe(self, locale_id):
        text = "word\u02bc"  # modifier letter apostrophe
        result = identify_unpaired_right_single_quote(text, Locale(locale_id))
        assert result == "word{{typopo__rsq--unpaired}}"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_word_reversed_9(self, locale_id):
        text = "word\u201b"  # high-reversed-9 quotation mark
        result = identify_unpaired_right_single_quote(text, Locale(locale_id))
        assert result == "word{{typopo__rsq--unpaired}}"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_word_acute_accent(self, locale_id):
        text = "word\u00b4"  # acute accent
        result = identify_unpaired_right_single_quote(text, Locale(locale_id))
        assert result == "word{{typopo__rsq--unpaired}}"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_word_backtick(self, locale_id):
        text = "word`"
        result = identify_unpaired_right_single_quote(text, Locale(locale_id))
        assert result == "word{{typopo__rsq--unpaired}}"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_word_prime(self, locale_id):
        text = "word\u2032"  # prime
        result = identify_unpaired_right_single_quote(text, Locale(locale_id))
        assert result == "word{{typopo__rsq--unpaired}}"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_word_left_guillemet(self, locale_id):
        text = "word\u2039"  # single left-pointing angle quotation mark
        result = identify_unpaired_right_single_quote(text, Locale(locale_id))
        assert result == "word{{typopo__rsq--unpaired}}"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_word_right_guillemet(self, locale_id):
        text = "word\u203a"  # single right-pointing angle quotation mark
        result = identify_unpaired_right_single_quote(text, Locale(locale_id))
        assert result == "word{{typopo__rsq--unpaired}}"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_word_period_quote(self, locale_id):
        text = "word.'"
        result = identify_unpaired_right_single_quote(text, Locale(locale_id))
        assert result == "word.{{typopo__rsq--unpaired}}"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_word_exclamation_quote(self, locale_id):
        text = "word!'"
        result = identify_unpaired_right_single_quote(text, Locale(locale_id))
        assert result == "word!{{typopo__rsq--unpaired}}"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_word_quote_colon(self, locale_id):
        text = "word':"
        result = identify_unpaired_right_single_quote(text, Locale(locale_id))
        assert result == "word{{typopo__rsq--unpaired}}:"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_word_quote_comma(self, locale_id):
        text = "word',"
        result = identify_unpaired_right_single_quote(text, Locale(locale_id))
        assert result == "word{{typopo__rsq--unpaired}},"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_word_quote_space(self, locale_id):
        text = "word' "
        result = identify_unpaired_right_single_quote(text, Locale(locale_id))
        assert result == "word{{typopo__rsq--unpaired}} "


class TestIdentifySingleQuotesWithinDoubleQuotesUnit:
    """Unit tests for identify_single_quotes_within_double_quotes function."""

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_single_word_in_double_quotes(self, locale_id):
        text = "\"What about 'word', is that good?\""
        result = identify_single_quotes_within_double_quotes(text, Locale(locale_id))
        assert "{{typopo__lsq}}" in result
        assert "{{typopo__rsq}}" in result

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_multiple_words_in_double_quotes(self, locale_id):
        text = "\"What about 'word word', is that good?\""
        result = identify_single_quotes_within_double_quotes(text, Locale(locale_id))
        assert "{{typopo__lsq}}" in result
        assert "{{typopo__rsq}}" in result

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_curly_double_quotes(self, locale_id):
        text = "\u201cWhat about 'word', is that good?\u201d"  # curly double quotes
        result = identify_single_quotes_within_double_quotes(text, Locale(locale_id))
        assert "{{typopo__lsq}}" in result
        assert "{{typopo__rsq}}" in result


class TestIdentifySingleQuotePairsUnit:
    """Unit tests for identify_single_quote_pairs function."""

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_unpaired_to_paired_single_word(self, locale_id):
        text = "{{typopo__lsq--unpaired}}word{{typopo__rsq--unpaired}}"
        result = identify_single_quote_pairs(text, Locale(locale_id))
        assert result == "{{typopo__lsq}}word{{typopo__rsq}}"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_unpaired_to_paired_multiple_words(self, locale_id):
        text = "{{typopo__lsq--unpaired}}word word{{typopo__rsq--unpaired}}"
        result = identify_single_quote_pairs(text, Locale(locale_id))
        assert result == "{{typopo__lsq}}word word{{typopo__rsq}}"


class TestIdentifySingleQuotePairAroundSingleWordUnit:
    """Unit tests for identify_single_quote_pair_around_single_word function."""

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_single_word(self, locale_id):
        text = "'word'"
        result = identify_single_quote_pair_around_single_word(text, Locale(locale_id))
        assert result == "{{typopo__lsq}}word{{typopo__rsq}}"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_two_single_words(self, locale_id):
        text = "'word' 'word'"
        result = identify_single_quote_pair_around_single_word(text, Locale(locale_id))
        assert result == "{{typopo__lsq}}word{{typopo__rsq}} {{typopo__lsq}}word{{typopo__rsq}}"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_single_letter(self, locale_id):
        text = "Press 'N' to get started"
        result = identify_single_quote_pair_around_single_word(text, Locale(locale_id))
        assert result == "Press {{typopo__lsq}}N{{typopo__rsq}} to get started"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_false_positive_dont_end(self, locale_id):
        """Don't treat apostrophe in don't as closing quote."""
        text = "... don't'"
        result = identify_single_quote_pair_around_single_word(text, Locale(locale_id))
        # The ' at the end is not word-bounded, so shouldn't create quote pair
        assert result == text

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_false_positive_dont_start(self, locale_id):
        """Don't treat apostrophe in don't as opening quote."""
        text = "'don't ..."
        result = identify_single_quote_pair_around_single_word(text, Locale(locale_id))
        # The ' at the start is not word-bounded, so shouldn't create quote pair
        assert result == text

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_false_positive_multiple_words(self, locale_id):
        """Multiple words should not be identified as single word quote pair."""
        text = "'word word'"
        result = identify_single_quote_pair_around_single_word(text, Locale(locale_id))
        # Multiple words - this function only handles single words
        assert result == text


class TestIdentifyResidualApostrophesUnit:
    """Unit tests for identify_residual_apostrophes function."""

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_straight_quote(self, locale_id):
        text = "Hers'"
        result = identify_residual_apostrophes(text, Locale(locale_id))
        assert result == "Hers{{typopo__apostrophe}}"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_curly_quote(self, locale_id):
        text = "Hers\u2019"  # right single quotation mark
        result = identify_residual_apostrophes(text, Locale(locale_id))
        assert result == "Hers{{typopo__apostrophe}}"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_modifier_apostrophe(self, locale_id):
        text = "word\u02bc"  # modifier letter apostrophe
        result = identify_residual_apostrophes(text, Locale(locale_id))
        assert result == "word{{typopo__apostrophe}}"


class TestReplaceSinglePrimeWithSingleQuoteUnit:
    """Unit tests for replace_single_prime_with_single_quote function."""

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_unpaired_left_and_prime(self, locale_id):
        text = "{{typopo__lsq--unpaired}}word{{typopo__single-prime}}"
        result = replace_single_prime_with_single_quote(text, Locale(locale_id))
        assert result == "{{typopo__lsq}}word{{typopo__rsq}}"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_prime_and_unpaired_right(self, locale_id):
        text = "{{typopo__single-prime}}word{{typopo__rsq--unpaired}}"
        result = replace_single_prime_with_single_quote(text, Locale(locale_id))
        assert result == "{{typopo__lsq}}word{{typopo__rsq}}"


class TestRemoveExtraSpaceAroundSinglePrimeUnit:
    """Unit tests for remove_extra_space_around_single_prime function."""

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_remove_space_before_prime(self, locale_id):
        text = f"12 {SINGLE_PRIME} 45\u2033"  # 12 ′ 45″
        result = remove_extra_space_around_single_prime(text, Locale(locale_id))
        assert result == f"12{SINGLE_PRIME} 45\u2033"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_remove_space_before_prime_no_trailing_space(self, locale_id):
        text = f"12 {SINGLE_PRIME}45\u2033"  # 12 ′45″
        result = remove_extra_space_around_single_prime(text, Locale(locale_id))
        assert result == f"12{SINGLE_PRIME}45\u2033"


class TestPlaceLocaleSingleQuotesUnit:
    """Unit tests for place_locale_single_quotes function."""

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_place_quote_pair(self, locale_id):
        q = get_quotes(locale_id)
        text = "{{typopo__lsq}}word{{typopo__rsq}}"
        result = place_locale_single_quotes(text, Locale(locale_id))
        assert result == f"{q['lsq']}word{q['rsq']}"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_place_apostrophe(self, locale_id):
        text = "{{typopo__apostrophe}}"
        result = place_locale_single_quotes(text, Locale(locale_id))
        assert result == APOSTROPHE

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_place_single_prime(self, locale_id):
        text = "{{typopo__single-prime}}"
        result = place_locale_single_quotes(text, Locale(locale_id))
        assert result == SINGLE_PRIME

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_place_unpaired_left_becomes_apostrophe(self, locale_id):
        text = "{{typopo__lsq--unpaired}}"
        result = place_locale_single_quotes(text, Locale(locale_id))
        assert result == APOSTROPHE

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_place_unpaired_right_becomes_apostrophe(self, locale_id):
        text = "{{typopo__rsq--unpaired}}"
        result = place_locale_single_quotes(text, Locale(locale_id))
        assert result == APOSTROPHE


class TestFixSingleQuotesPrimesAndApostrophes:
    """Integration tests for the main function."""

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_basic_contraction(self, locale_id):
        text = "don't"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"don{APOSTROPHE}t"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_quoted_word(self, locale_id):
        q = get_quotes(locale_id)
        text = "'word'"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"{q['lsq']}word{q['rsq']}"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_feet_and_inches(self, locale_id):
        text = "12' 45\u2033"  # 12' 45″
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"12{SINGLE_PRIME} 45\u2033"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_preserve_markdown_code(self, locale_id):
        text = "```\ncode\n```"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id, keep_markdown_code_blocks=True)
        assert result == text

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_inline_code(self, locale_id):
        text = "`code`"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id, keep_markdown_code_blocks=True)
        assert result == text

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_complex_text(self, locale_id):
        text = "I'm listening to rock 'n' roll in the '70s"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        expected = f"I{APOSTROPHE}m listening to rock{NBSP}{APOSTROPHE}n{APOSTROPHE}{NBSP}roll in the {APOSTROPHE}70s"
        assert result == expected


class TestSwapSingleQuotesAndTerminalPunctuationUnit:
    """Additional unit tests for swap_single_quotes_and_terminal_punctuation function."""

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_quoted_part_middle_of_paragraph_two_parts(self, locale_id):
        """Two quoted parts in middle of paragraph - move periods outside."""
        q = get_quotes(locale_id)
        text = f"a {q['lsq']}quoted part.{q['rsq']} A {q['lsq']}quoted part.{q['rsq']}"
        expected = f"a {q['lsq']}quoted part{q['rsq']}. A {q['lsq']}quoted part{q['rsq']}."
        result = swap_single_quotes_and_terminal_punctuation(text, Locale(locale_id))
        assert result == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_question_mark_no_swap_needed(self, locale_id):
        """Question mark outside stays outside when quote is a title."""
        q = get_quotes(locale_id)
        text = f"Is it {q['lsq']}Amores Perros{q['rsq']}?"
        result = swap_single_quotes_and_terminal_punctuation(text, Locale(locale_id))
        assert result == text

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_period_no_swap_needed(self, locale_id):
        """Period outside stays outside when quote is a title."""
        q = get_quotes(locale_id)
        text = f"Look for {q['lsq']}Anguanga{q['rsq']}."
        result = swap_single_quotes_and_terminal_punctuation(text, Locale(locale_id))
        assert result == text


class TestModuleIntegrationSingleQuotesWithinDoubleQuotes:
    """Integration tests for single quotes within double quotes (module level)."""

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_single_word_in_double_quotes(self, locale_id):
        """Single quoted word within double quotes."""
        q = get_quotes(locale_id)
        text = f"{q['ldq']}What about 'word', is that good?{q['rdq']}"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        expected = f"{q['ldq']}What about {q['lsq']}word{q['rsq']}, is that good?{q['rdq']}"
        assert result == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_two_single_words_in_double_quotes(self, locale_id):
        """Two single quoted words within double quotes."""
        q = get_quotes(locale_id)
        text = f"{q['ldq']}What about 'word' 'word', is that good?{q['rdq']}"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        expected = f"{q['ldq']}What about {q['lsq']}word{q['rsq']} {q['lsq']}word{q['rsq']}, is that good?{q['rdq']}"
        assert result == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_multiple_words_in_single_quotes_within_double_quotes(self, locale_id):
        """Multiple words in single quotes within double quotes."""
        q = get_quotes(locale_id)
        text = f"{q['ldq']}What about 'word word', is that good?{q['rdq']}"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        expected = f"{q['ldq']}What about {q['lsq']}word word{q['rsq']}, is that good?{q['rdq']}"
        assert result == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_double_quotes_with_single_quotes_and_within(self, locale_id):
        """Double quotes and single quotes within."""
        q = get_quotes(locale_id)
        text = f"{q['ldq']}double quotes 'and single quotes' within{q['rdq']}"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        expected = f"{q['ldq']}double quotes {q['lsq']}and single quotes{q['rsq']} within{q['rdq']}"
        assert result == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_single_quotes_with_mixed_punctuation(self, locale_id):
        """Single quotes with mixed punctuation including apostrophe contraction."""
        q = get_quotes(locale_id)
        text = f"Within double quotes {q['ldq']}there are single 'quotes with mix'd punctuation', you see{q['rdq']}."
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        expected = f"Within double quotes {q['ldq']}there are single {q['lsq']}quotes with mix{APOSTROPHE}d punctuation{q['rsq']}, you see{q['rdq']}."
        assert result == expected


class TestModuleIntegrationReplaceSinglePrimeWithSingleQuote:
    """Integration tests for replacing single prime with single quote (module level)."""

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_localhost_3000_in_quotes(self, locale_id):
        """'Localhost 3000' - prime after number becomes right quote."""
        q = get_quotes(locale_id)
        text = f"{q['ldq']}What about 'Localhost 3000', is that good?{q['rdq']}"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        expected = f"{q['ldq']}What about {q['lsq']}Localhost 3000{q['rsq']}, is that good?{q['rdq']}"
        assert result == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_30_bucks_in_quotes(self, locale_id):
        """30 'bucks' - number followed by quoted word."""
        q = get_quotes(locale_id)
        text = f"{q['ldq']}Here are 30 'bucks'{q['rdq']}"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        expected = f"{q['ldq']}Here are 30 {q['lsq']}bucks{q['rsq']}{q['rdq']}"
        assert result == expected


class TestModuleIntegrationComplexCases:
    """Integration tests for complex cases combining multiple transformations."""

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_complex_sentence_with_contractions_and_quotes(self, locale_id):
        """Complex sentence with contractions, 'n' contraction, and quoted words."""
        q = get_quotes(locale_id)
        text = f"Let's test this: {q['ldq']}however, 'quote this or nottin' rock 'n' roll this will be corrected for 69'ers,' he said{q['rdq']}"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        # Expected: Let's, nottin', rock 'n' roll, 69'ers all get apostrophes
        # 'quote this or nottin' rock 'n' roll this will be corrected for 69'ers,' becomes quoted
        assert f"Let{APOSTROPHE}s" in result
        assert f"nottin{APOSTROPHE}" in result
        assert f"{APOSTROPHE}n{APOSTROPHE}" in result
        assert f"69{APOSTROPHE}ers" in result

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_two_single_quote_pairs_and_name(self, locale_id):
        """Two names in single quotes: 'name' and 'other name'."""
        q = get_quotes(locale_id)
        text = f"{q['ldq']}What about 'name' and 'other name'?{q['rdq']}"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        expected = f"{q['ldq']}What about {q['lsq']}name{q['rsq']} and {q['lsq']}other name{q['rsq']}?{q['rdq']}"
        assert result == expected


class TestIdentifySinglePrimesModuleLevel:
    """Module-level tests for identifying single primes (feet/arcminutes)."""

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_12_space_quote_space_45_double_prime(self, locale_id):
        """12 ' 45″ with spaces around single quote."""
        text = "12 ' 45\u2033"  # 12 ' 45″
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"12{SINGLE_PRIME} 45\u2033"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_12_left_quote_space_45_double_prime(self, locale_id):
        """12 ' 45″ with left single quote."""
        text = "12 \u2018 45\u2033"  # 12 ' 45″
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"12{SINGLE_PRIME} 45\u2033"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_12_right_quote_space_45_double_prime(self, locale_id):
        """12 ' 45″ with right single quote."""
        text = "12 \u2019 45\u2033"  # 12 ' 45″
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"12{SINGLE_PRIME} 45\u2033"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_12_reversed9_space_45_double_prime(self, locale_id):
        """12 ‛ 45″ with high-reversed-9 quote."""
        text = "12 \u201b 45\u2033"  # 12 ‛ 45″
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"12{SINGLE_PRIME} 45\u2033"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_12_prime_space_45_double_prime(self, locale_id):
        """12 ′ 45″ with prime (already correct but extra space)."""
        text = "12 \u2032 45\u2033"  # 12 ′ 45″
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"12{SINGLE_PRIME} 45\u2033"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_12_reversed9_no_space_45_double_prime(self, locale_id):
        """12‛45″ with reversed-9 and no spaces."""
        text = "12 \u201b45\u2033"  # 12 ‛45″
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"12{SINGLE_PRIME}45\u2033"

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_12_straight_no_space_45_double_prime(self, locale_id):
        """12 '45″ with straight quote and no space after."""
        text = "12 '45\u2033"  # 12 '45″
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        assert result == f"12{SINGLE_PRIME}45\u2033"


class TestIdentifyUnpairedLeftSingleQuoteModuleLevel:
    """Module-level tests for identifying unpaired left single quotes."""

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_double_quote_space_single_quote_word(self, locale_id):
        """Inside double quotes: single quote before word becomes apostrophe."""
        q = get_quotes(locale_id)
        text = f"{q['ldq']}'word{q['rdq']}"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        expected = f"{q['ldq']}{APOSTROPHE}word{q['rdq']}"
        assert result == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_double_quote_en_dash_single_quote_word(self, locale_id):
        """Inside double quotes: en dash + single quote before word."""
        q = get_quotes(locale_id)
        text = f"{q['ldq']}\u2013'word{q['rdq']}"  # en dash
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        expected = f"{q['ldq']}\u2013{APOSTROPHE}word{q['rdq']}"
        assert result == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_double_quote_em_dash_single_quote_word(self, locale_id):
        """Inside double quotes: em dash + single quote before word."""
        q = get_quotes(locale_id)
        text = f"{q['ldq']}\u2014'word{q['rdq']}"  # em dash
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        expected = f"{q['ldq']}\u2014{APOSTROPHE}word{q['rdq']}"
        assert result == expected


class TestIdentifyUnpairedRightSingleQuoteModuleLevel:
    """Module-level tests for identifying unpaired right single quotes."""

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_word_single_quote_inside_double_quotes(self, locale_id):
        """Inside double quotes: word + single quote becomes apostrophe."""
        q = get_quotes(locale_id)
        text = f"{q['ldq']}word'{q['rdq']}"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        expected = f"{q['ldq']}word{APOSTROPHE}{q['rdq']}"
        assert result == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_word_low9_quote_inside_double_quotes(self, locale_id):
        """Inside double quotes: word + low-9 quote becomes apostrophe."""
        q = get_quotes(locale_id)
        text = f"{q['ldq']}word\u201a{q['rdq']}"  # low-9 quotation mark
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        expected = f"{q['ldq']}word{APOSTROPHE}{q['rdq']}"
        assert result == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_word_period_single_quote_inside_double_quotes(self, locale_id):
        """Inside double quotes: word + period + single quote."""
        q = get_quotes(locale_id)
        text = f"{q['ldq']}word.'{q['rdq']}"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        expected = f"{q['ldq']}word.{APOSTROPHE}{q['rdq']}"
        assert result == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_word_exclamation_single_quote_inside_double_quotes(self, locale_id):
        """Inside double quotes: word + exclamation + single quote."""
        q = get_quotes(locale_id)
        text = f"{q['ldq']}word!'{q['rdq']}"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        expected = f"{q['ldq']}word!{APOSTROPHE}{q['rdq']}"
        assert result == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_word_single_quote_colon_inside_double_quotes(self, locale_id):
        """Inside double quotes: word + single quote + colon."""
        q = get_quotes(locale_id)
        text = f"{q['ldq']}word':{q['rdq']}"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        expected = f"{q['ldq']}word{APOSTROPHE}:{q['rdq']}"
        assert result == expected

    @pytest.mark.parametrize("locale_id", ALL_LOCALES)
    def test_word_single_quote_comma_inside_double_quotes(self, locale_id):
        """Inside double quotes: word + single quote + comma."""
        q = get_quotes(locale_id)
        text = f"{q['ldq']}word',{q['rdq']}"
        result = fix_single_quotes_primes_and_apostrophes(text, locale_id)
        expected = f"{q['ldq']}word{APOSTROPHE},{q['rdq']}"
        assert result == expected
