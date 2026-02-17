# CLAUDE.md - pytypopo

Python port of [typopo](https://github.com/surfinzap/typopo/) - a multilingual typography fixer.

## Project Overview

**Version:** 3.0.0
**Status:** Complete - full port of typopo with 12,525 tests passing on Python 3.10-3.14.

**Original JS library:** https://github.com/surfinzap/typopo/

## Architecture

```
src/pytypopo/
├── __init__.py          # Main API: fix_typos()
├── const.py             # Character sets, regex patterns
├── locale/
│   ├── __init__.py
│   ├── base.py          # Locale class
│   ├── en_us.py, de_de.py, cs.py, sk.py, rue.py
├── modules/
│   ├── punctuation/     # period, ellipsis, dash, quotes
│   ├── symbols/         # copyright, exponents, marks, etc.
│   ├── whitespace/      # lines, nbsp, spaces
│   └── words/           # abbreviations, case, pub_id
└── utils/
    └── regex_overlap.py
```

## Commands

```bash
# Setup pre-commit hooks (one-time after clone)
uv run pre-commit install

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src/pytypopo

# Run tests on specific Python version
uv sync --python 3.14 --all-extras && uv run --python 3.14 pytest

# Run tests on all supported versions
for v in 3.10 3.11 3.12 3.13 3.14; do
  uv sync --python $v --all-extras -q
  uv run --python $v pytest -q
done

# Lint
uv run ruff check src tests
uv run ruff format src tests
```

## Development

### Prerequisites

| Tool | Required For | Install |
|------|--------------|---------|
| uv | All development | https://docs.astral.sh/uv/ |
| Node.js + npm | Cross-testing | https://nodejs.org/ |
| jq | Cross-test `--json` flag | `brew install jq` / `apt install jq` |

## API

```python
from pytypopo import fix_typos

result = fix_typos(
    text,
    locale="en-us",           # en-us, de-de, cs, sk, rue
    remove_lines=True,        # remove empty lines
)
```

## Supported Locales

| Locale | Language |
|--------|----------|
| en-us  | English (US) - default |
| de-de  | German |
| cs     | Czech |
| sk     | Slovak |
| rue    | Rusyn |

## Module Processing Order

Pipeline order matters (prevents re-matching corrected patterns):

1. Exception extraction (URLs, emails, code blocks)
2. Whitespace fixes (spaces, lines)
3. Punctuation fixes (periods, ellipsis, dashes, quotes)
4. Symbol fixes (©, ™, ×, etc.)
5. Word fixes (abbreviations, case)
6. Non-breaking space rules
7. Exception reinsertion

## Key Implementation Notes

- Runtime dependency: `regex` library (for Unicode category support like `\p{L}`)
- Dev dependencies: pytest, ruff, coverage
- Locale-aware: all functions receive locale parameter
- False positive prevention is critical

## Style Guide

- No type hints (per project conventions)
- Pythonic patterns, f-strings
- No semicolons, single quotes in tests
- 4-space indent, 120-char max line
- Use guard clauses, pure functions where practical

## Cross-Testing (brotest)

Verifies Python port matches JS behavior:

```bash
# Run full cross-test suite
./cross-test/run-cross-tests.sh

# Show only failures
./cross-test/show-failures.sh

# Test specific module
./cross-test/show-failures.sh dash

# JSON output (requires jq)
./cross-test/show-failures.sh --json
```

See `cross-test/README.md` for architecture details.

Use the **brotest** agent to fix parity failures:
- Compares JS vs Python locale configs
- Identifies mismatches in dash types, quote chars, spacing
- Reference: `cross-test/typopo/src/` (JS) vs `src/pytypopo/` (Python)

## Versioning

This project tracks the upstream library's version using semantic versioning and appends a Python-specific local build suffix.

The format is: `MAJOR.MINOR.PATCH+pyN`

Example: `3.0.0+py1`

Where:

- `3.0.0` matches the upstream version for compatibility reference
- `+py1` is the local Python port patch/revision number

### Rules

- Upstream updates change `MAJOR.MINOR.PATCH`
- Port-specific fixes increment only the local suffix (e.g., `+py2`, `+py3`, …)
- The local suffix never implies changes to the upstream version itself

### Rationale

This pattern preserves the ability to see upstream compatibility at a glance while remaining compliant with SemVer and PEP 440. Tools such as `pip`, `setuptools`, `wheel`, and `twine` correctly parse and sort versions like `3.0.0+pyN`.
