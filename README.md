# pytypopo

[![CI](https://github.com/benabraham/pytypopo/actions/workflows/ci.yml/badge.svg)](https://github.com/benabraham/pytypopo/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Python port of [typopo](https://github.com/surfinzap/typopo/)** — a multilingual typography fixer by Braňo Šandala.

## About

This library is a complete Python port of the JavaScript [typopo](https://github.com/surfinzap/typopo/) library. It automatically fixes common typography issues in text, with support for multiple languages and their specific typographic conventions.

The original typopo is a battle-tested tool used for fixing typography in various content management systems and text editors. This Python port brings the same functionality to Python developers, following the original's behavior as closely as possible.

### Why a port?

- Use typopo's easily in Python projects with zero runtime dependencies (pure Python + regex)
- Same reliable fixes as the original JavaScript version
- Wanted to try how Claude Code would handle such task.

### Future

I use this in a serious Python project but I'm really not sure if I will keep maintaing this.

## Installation

Not on pypi yet (may change in future).

```bash
# Install from GitHub
pip install git+https://github.com/benabraham/pytypopo.git

# Or with uv
uv add git+https://github.com/benabraham/pytypopo.git
```

## Usage

```python
from pytypopo import fix_typos

# Basic usage (defaults to English)
text = fix_typos('Hello "world"...')
# → Hello "world"…

# With locale
text = fix_typos('Ahoj "svete"...', locale='cs')
# → Ahoj „svete"…

# German
text = fix_typos('Er sagte "Hallo"', locale='de-de')
# → Er sagte „Hallo"

# With options
text = fix_typos(
    text,
    locale='en-us',
    remove_lines=True,           # Remove excessive empty lines
    keep_markdown_code_blocks=True  # Protect code blocks from changes
)
```

## API

```python
def fix_typos(
    text: str,
    locale: str = 'en-us',
    *,
    remove_lines: bool = True,
    keep_markdown_code_blocks: bool = True
) -> str:
    """
    Fix typography issues in text.

    Args:
        text: Input text to fix
        locale: Language locale (en-us, de-de, cs, sk, rue)
        remove_lines: Remove excessive empty lines
        keep_markdown_code_blocks: Protect markdown code blocks from changes

    Returns:
        Text with typography fixes applied
    """
```

## Development

```bash
# Clone and setup
git clone https://github.com/benabraham/pytypopo.git
cd pytypopo
uv sync --dev
uv run pre-commit install  # Setup git hooks

# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/pytypopo

# Lint
uv run ruff check src tests
uv run ruff format src tests
```

## Contributing

PRs are welcome. If you're thinking about contributing something more than a simple fix please [open an issue](https://github.com/benabraham/pytypopo/issues) first.

## Versioning

This project tracks the upstream library's version using semantic versioning and appends a Python-specific local build suffix.

The format is: `MAJOR.MINOR.PATCH+pyN`

Where:

- `2.8.2` matches the upstream version for compatibility reference
- `+py1` is the local Python port patch/revision number
- The local suffix never implies changes to the upstream version itself

## Differences from original

This port aims to match the original typopo behavior exactly. Minor differences may exist in edge cases. If you find any discrepancies, please [open an issue](https://github.com/benabraham/pytypopo/issues).
