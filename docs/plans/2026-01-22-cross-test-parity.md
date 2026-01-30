# Cross-Test Parity Fixes Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Fix Python behavior to match JS typopo for copyright spacing, ordinal dates, and quote punctuation.

**Architecture:** Locale-specific config fixes + regex pattern improvements for edge cases.

**Tech Stack:** Python, regex, pytest

---

## Summary of Failures

| Category | Failures | Root Cause |
|----------|----------|------------|
| Copyright spacing (cs) | 56 | Czech locale uses regular space, Python uses NBSP |
| Ordinal date | 19 | Version numbers (3.0.0) incorrectly treated as dates |
| Quote punctuation | 2000+ | Deferred - complex locale-specific rules |

---

### Task 1: Fix Czech Copyright Spacing

**Files:**
- Modify: `src/pytypopo/locale/base.py:106-107`
- Test: `tests/symbols/test_copyrights.py`

**Step 1: Write failing test**

Add to `tests/symbols/test_copyrights.py`:

```python
class TestCzechCopyrightSpacing:
    """Czech locale uses regular space (not NBSP) after copyright symbols."""

    def test_copyright_uses_regular_space_for_czech(self):
        """Czech: © should be followed by regular space, not NBSP."""
        from pytypopo import fix_typos
        from pytypopo.const import NBSP

        result = fix_typos('Company© 2017', 'cs')
        # Czech uses regular space, not NBSP
        assert result == 'Company © 2017'
        assert NBSP not in result

    def test_sound_recording_copyright_uses_regular_space_for_czech(self):
        """Czech: ℗ should be followed by regular space, not NBSP."""
        from pytypopo import fix_typos
        from pytypopo.const import NBSP

        result = fix_typos('Company℗ 2017', 'cs')
        # Czech uses regular space, not NBSP
        assert result == 'Company ℗ 2017'
        assert NBSP not in result
```

**Step 2: Run test to verify it fails**

```bash
uv run pytest tests/symbols/test_copyrights.py::TestCzechCopyrightSpacing -v
```

Expected: FAIL (currently outputs NBSP instead of space)

**Step 3: Fix locale config**

In `src/pytypopo/locale/base.py`, change cs locale config (around line 106):

```python
    "cs": {
        # ... other config ...
        "space_after_copyright": SPACE,  # Changed from NBSP
        "space_after_sound_recording_copyright": SPACE,  # Changed from NBSP
        # ... rest unchanged ...
    },
```

**Step 4: Run test to verify it passes**

```bash
uv run pytest tests/symbols/test_copyrights.py::TestCzechCopyrightSpacing -v
```

Expected: PASS

**Step 5: Run full copyright tests**

```bash
uv run pytest tests/symbols/test_copyrights.py -v
```

Expected: All tests pass

**Step 6: Commit**

```bash
git add src/pytypopo/locale/base.py tests/symbols/test_copyrights.py
git commit -m "fix(locale): use regular space for Czech copyright symbols"
```

---

### Task 2: Fix Ordinal Date Version Number False Positive

**Files:**
- Modify: `src/pytypopo/modules/whitespace/nbsp.py`
- Test: `tests/whitespace/test_nbsp.py`

**Step 1: Analyze current behavior**

Current behavior:
- `12.12.2017` → unchanged (WRONG - should add spaces)
- `3.0.0` → `3. 0. 0` (WRONG - should stay unchanged)

Expected behavior:
- `12.12.2017` → `12. 12. 2017` (valid date)
- `3.0.0` → `3.0.0` (version number, not a date)

**Step 2: Write failing tests**

Add to `tests/whitespace/test_nbsp.py`:

```python
class TestOrdinalDateVersionFalsePositive:
    """Version numbers should not be treated as ordinal dates."""

    @pytest.mark.parametrize('locale', ['cs', 'sk', 'de-de', 'en-us', 'rue'])
    def test_version_numbers_unchanged(self, locale):
        """Version numbers like 3.0.0 should not be modified."""
        from pytypopo import fix_typos

        # Version numbers - should NOT be changed
        assert fix_typos('3.0.0', locale) == '3.0.0'
        assert fix_typos('1.2.3', locale) == '1.2.3'
        assert fix_typos('10.0.1', locale) == '10.0.1'

    @pytest.mark.parametrize('locale', ['cs', 'sk', 'de-de'])
    def test_ordinal_dates_get_spaces(self, locale):
        """Valid ordinal dates should get proper spacing."""
        from pytypopo import fix_typos
        from pytypopo.const import NBSP

        # Valid dates - should add spacing
        result = fix_typos('12.12.2017', locale)
        # Should have spaces after day and month
        assert '12.' in result and '2017' in result
        # Verify spaces were added (either NBSP or regular)
        assert result != '12.12.2017'
```

**Step 3: Run test to verify it fails**

```bash
uv run pytest tests/whitespace/test_nbsp.py::TestOrdinalDateVersionFalsePositive -v
```

Expected: FAIL

**Step 4: Find and fix the ordinal date regex**

Locate the ordinal date function in `src/pytypopo/modules/whitespace/nbsp.py`:

```bash
grep -n "ordinal.*date\|date.*ordinal" src/pytypopo/modules/whitespace/nbsp.py
```

The fix needs to:
1. Only match dates with valid day (1-31) and month (1-12)
2. Year must be 4 digits (1000-2999 range)
3. Version numbers (any.any.any where any < 100) should be excluded

**Step 5: Implement the fix**

Update the ordinal date pattern to be more restrictive:

```python
def fix_ordinal_date_spacing(text, locale):
    """
    Add proper spacing to ordinal dates like 12.12.2017.

    Excludes version numbers like 3.0.0 or 1.2.3.
    Valid dates: day (1-31), month (1-12), year (1000-2999).
    """
    loc = _get_locale(locale)
    first_space = loc.ordinal_date_first_space
    second_space = loc.ordinal_date_second_space

    # Pattern: day.month.year where:
    # - day: 1-31 (with optional leading zero)
    # - month: 1-12 (with optional leading zero)
    # - year: 4 digits starting with 1 or 2
    pattern = re.compile(
        r'\b'
        r'([1-9]|0[1-9]|[12][0-9]|3[01])\.'  # day: 1-31
        r'([1-9]|0[1-9]|1[0-2])\.'           # month: 1-12
        r'([12][0-9]{3})'                     # year: 1000-2999
        r'\b'
    )

    return pattern.sub(rf'\1.{first_space}\2.{second_space}\3', text)
```

**Step 6: Run test to verify it passes**

```bash
uv run pytest tests/whitespace/test_nbsp.py::TestOrdinalDateVersionFalsePositive -v
```

Expected: PASS

**Step 7: Run full nbsp tests**

```bash
uv run pytest tests/whitespace/test_nbsp.py -v
```

Expected: All tests pass

**Step 8: Commit**

```bash
git add src/pytypopo/modules/whitespace/nbsp.py tests/whitespace/test_nbsp.py
git commit -m "fix(nbsp): exclude version numbers from ordinal date spacing"
```

---

### Task 3: Run Cross-Tests to Verify

**Step 1: Run cross-tests**

```bash
bash cross-test/run-cross-tests.sh 2>&1 | grep "Test Files"
```

Expected: Fewer failures (copyright and nbsp tests should pass now)

**Step 2: Count remaining failures**

```bash
bash cross-test/run-cross-tests.sh 2>&1 | grep "FAIL" | wc -l
```

Expected: ~2000 (quotes-related, deferred)

**Step 3: Commit all changes**

```bash
git add -A
git commit -m "fix: cross-test parity for copyright spacing and ordinal dates"
```

---

## Deferred: Quote Punctuation Placement

The 2000+ quote-related failures involve complex locale-specific punctuation placement rules:

1. **Period/punctuation inside vs outside quotes** - Varies by locale
2. **Nested quote handling** - Single quotes within double quotes
3. **Direct speech patterns** - Locale-specific intro markers

These require deeper analysis and are deferred to a separate plan.

---

## Verification Checklist

- [ ] Czech copyright uses regular space (not NBSP)
- [ ] Version numbers (3.0.0) unchanged
- [ ] Valid dates (12.12.2017) get proper spacing
- [ ] All existing Python tests still pass
- [ ] Cross-test copyright failures resolved
- [ ] Cross-test nbsp failures reduced
