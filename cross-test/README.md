# pytypopo Cross-Test Suite

Runs the upstream [typopo](https://github.com/surfinzap/typopo/) JavaScript test suite against the pytypopo Python port to verify parity.

## How It Works

```
┌────────────────┐     HTTP POST     ┌───────────────┐
│ Vitest (JS)    │ ────────────────▶ │ Python Bridge │
│ upstream tests │ ◀──────────────── │ (http server) │
└────────────────┘   JSON response   └───────────────┘
                                          pytypopo
```

1. **Python Bridge** (`python_bridge.py`) - HTTP server that exposes pytypopo functions
2. **JS Adapter** (`js-adapter/`) - Modified test utilities that redirect function calls to Python
3. **Upstream Tests** (`typopo/`) - Clone of the original typopo repo with all tests

## Quick Start

```bash
# Run all cross-tests
./run-cross-tests.sh

# Or manually:
uv run python python_bridge.py 9876 &
cd js-adapter && npm test
```

## Test Results

- **Passed tests** = Python produces same output as JS ✅
- **Failed tests** = Parity issues to investigate ⚠️
- **Skipped tests** = Helper functions not exposed in Python ⏭️

## Updating Upstream

To pull latest upstream tests:

```bash
cd typopo
git pull origin main
```

## Adding Missing Functions

If tests fail with "Unknown function", add the function to `python_bridge.py`:

```python
FUNCTION_MAP = {
    # ...existing functions...
    'newFunction': (new_function, True, False),  # (func, needs_locale, needs_config)
}
```

## Known Differences

Some intentional differences between Python and JS:
- (Document any known/accepted differences here)
