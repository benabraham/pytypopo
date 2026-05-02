---
name: sync-with-upstream
description: Sync pytypopo with the upstream typopo JS library. Detects upstream changes since last sync, identifies what needs porting (source, tests, docs), runs cross-tests for parity gaps, and updates version references. Use when user says "sync upstream", "update from upstream", "pull upstream changes", "port new typopo version", or "sync with typopo".
---

# Upstream Sync Skill

Sync pytypopo with the upstream [typopo](https://github.com/surfinzap/typopo/) JS library.

## Mental Model

- **Upstream repo**: `cross-test/typopo/` (git clone of `surfinzap/typopo`, used as authoritative reference)
- **Sync marker**: Latest pytypopo tag `vX.Y.Z+pyN` means upstream `X.Y.Z` was the last sync target
- **Goal of a sync**: Make the Python port match upstream `X.Y.Z` (latest tag) at parity, then bump pytypopo to `vX.Y.Z+py0` for release

This skill stops *before* running `/release`. It prepares the codebase; the release skill publishes it.

## Step 1: Pre-flight Checks

Run silently. Abort with clear message on any failure.

```bash
# Working tree must be clean
git status --porcelain

# Must be on main
git branch --show-current

# Must be in sync with origin
git fetch origin
git rev-list HEAD..origin/main --count  # must be 0
```

Abort conditions:
- Uncommitted changes → "Commit or stash changes first"
- Not on main → "Switch to main branch first"
- Behind remote → "Pull from origin first"

## Step 2: Detect Last Synced Upstream Version

```bash
# Latest pytypopo tag, e.g. "v3.0.0+py0"
LAST_TAG=$(git tag --sort=-v:refname | head -1)

# Extract upstream version: v3.0.0+py0 → 3.0.0
LAST_UPSTREAM=$(echo "$LAST_TAG" | sed -E 's/^v?([0-9]+\.[0-9]+\.[0-9]+).*/\1/')
echo "Last synced upstream version: $LAST_UPSTREAM"
```

## Step 3: Fetch Upstream & Determine Target Version

```bash
cd cross-test/typopo
git fetch --tags origin
git checkout main
git pull origin main

# Latest upstream tag (semver-sorted)
LATEST_UPSTREAM=$(git tag --sort=-v:refname | head -1)
echo "Latest upstream version: $LATEST_UPSTREAM"
cd ../..
```

If `LATEST_UPSTREAM == LAST_UPSTREAM`, check whether upstream main is ahead of the tag (untagged commits):

```bash
cd cross-test/typopo
git rev-list "$LATEST_UPSTREAM..origin/main" --count
cd ../..
```

- If 0 → "Already up to date with upstream $LATEST_UPSTREAM. Nothing to sync." Abort.
- If >0 → "Upstream has untagged commits past $LATEST_UPSTREAM. Wait for upstream release, or sync to HEAD anyway?" Use AskUserQuestion.

## Step 4: Analyze What Changed Upstream

Show the user a focused summary of what's changed between `LAST_UPSTREAM` and `LATEST_UPSTREAM`.

```bash
cd cross-test/typopo

# Commits since last sync
git log --oneline --no-merges "$LAST_UPSTREAM".."$LATEST_UPSTREAM"

# Files changed by category
git diff --stat "$LAST_UPSTREAM".."$LATEST_UPSTREAM" -- src/
git diff --stat "$LAST_UPSTREAM".."$LATEST_UPSTREAM" -- tests/
git diff --name-only "$LAST_UPSTREAM".."$LATEST_UPSTREAM" -- '*.md' 'package.json'

cd ../..
```

Categorize the diff for the user:

```
══════════════════════════════════════════════════════════════
                  UPSTREAM SYNC ANALYSIS
══════════════════════════════════════════════════════════════

Last synced: 2.9.1
Target:      3.0.0
Commits:     12

Source changes (src/):
  • src/modules/punctuation/dash.js          (24 +/-)
  • src/modules/symbols/copyrights.js        (new file)
  • src/locale/sk.js                         (8 +/-)

Test changes (tests/):
  • tests/punctuation/dash.test.js           (+15 cases)
  • tests/symbols/copyrights.test.js         (new file)

Docs/meta:
  • README.md, CHANGELOG.md, package.json

Likely Python work:
  • Update src/pytypopo/modules/punctuation/dash.py
  • Port new src/pytypopo/modules/symbols/copyrights.py
  • Update src/pytypopo/locale/sk.py
  • Mirror new test cases in tests/
══════════════════════════════════════════════════════════════
```

## Step 5: Confirm Sync Plan

**Use AskUserQuestion:**
- Question: "Proceed with sync to $LATEST_UPSTREAM?"
- Header: "Sync"
- Options:
  - "Proceed (Recommended)" — continue to Step 6
  - "Show full diff first" — output `git diff "$LAST_UPSTREAM".."$LATEST_UPSTREAM" -- src/`, then re-ask
  - "Abort" — stop

## Step 6: Run Cross-Tests Against Updated Upstream

The upstream repo is now at the new version, so cross-tests will reveal exactly what parity gaps exist.

```bash
# Start Python bridge (background)
uv run python cross-test/python_bridge.py 9876 &
BRIDGE_PID=$!

# Wait briefly for bridge to start
sleep 1

# Run cross-tests, capture summary
cd cross-test/js-adapter
PYTHON_BRIDGE_URL=http://127.0.0.1:9876 npx vitest run 2>&1 | tail -30
cd ../..

# Stop bridge
kill $BRIDGE_PID 2>/dev/null
```

Show the user:
- Number of failing tests
- Which test files have failures (groups by module)

## Step 7: Fix Parity Gaps with brotest Agent

If there are failures, delegate to the **brotest** agent. It is purpose-built for this:

> Use the Agent tool with `subagent_type: "general-purpose"` and a prompt that references `.claude/agents/brotest.md`. The brotest agent's workflow already covers: starting the bridge, isolating failures, comparing JS vs Python config, fixing source, and verifying with both cross-tests AND `uv run pytest`.

Brief the agent with:
- Last synced version → target version
- List of upstream files changed (from Step 4)
- Specific failing test files (from Step 6)
- Mandate: cross-tests must pass AND `uv run pytest` must pass

Do not duplicate the agent's work yourself — let it run, then verify the result.

## Step 8: Mirror New Upstream Tests

The brotest agent fixes Python *source* to match JS behavior, but new upstream test cases must also be mirrored into `tests/` so the Python suite covers them.

For each new/modified upstream test file, check the corresponding Python test file:

| Upstream | Python |
|----------|--------|
| `cross-test/typopo/tests/punctuation/dash.test.js` | `tests/punctuation/test_dash.py` |
| `cross-test/typopo/tests/symbols/copyrights.test.js` | `tests/symbols/test_copyrights.py` |

Add new test cases to mirror upstream coverage. Use existing Python test style (single quotes, no semicolons in JS sense, pytest patterns).

Run after each mirror:
```bash
uv run pytest tests/<module>/test_<file>.py
```

## Step 9: Update Version References

Bump version to `LATEST_UPSTREAM+py0`:

```bash
NEW_VERSION="${LATEST_UPSTREAM}+py0"

# pyproject.toml
sed -i "s/^version = \".*\"/version = \"${NEW_VERSION}\"/" pyproject.toml

# src/pytypopo/__init__.py
sed -i "s/^__version__ = \".*\"/__version__ = \"${NEW_VERSION}\"/" src/pytypopo/__init__.py

# Verify
grep '^version = ' pyproject.toml
grep '^__version__ = ' src/pytypopo/__init__.py
```

## Step 10: Update Documentation

Read each doc file and update where upstream changes affect it:

**CLAUDE.md** — check and update if needed:
- `**Version:**` line at top
- Test count in `**Status:**` line (run `uv run pytest --collect-only -q | tail -1` for actual count)
- New modules in Architecture tree
- New locales in Supported Locales table
- New API parameters in API section
- Any new processing step in Module Processing Order

**README.md** — check and update if needed:
- Supported locales section
- API/usage examples (if `fix_typos()` signature changed)
- Features section (if new modules)
- Installation/dependencies (if `pyproject.toml` deps changed)

**CHANGELOG.md** — only if the project maintains one (check `ls CHANGELOG*`). If absent, skip — release notes via `/release` cover this.

If unsure whether a doc change is needed, **use AskUserQuestion**:
- Question: "Found upstream change X. Update doc Y?"
- Header: "Docs"
- Options: "Update", "Skip (irrelevant)", "Show me the change"

## Step 11: Final Verification

All of these must pass before declaring sync complete:

```bash
# Python tests pass
uv run pytest

# Cross-tests pass (or are at the same/lower failure count as before)
uv run python cross-test/python_bridge.py 9876 &
BRIDGE_PID=$!
sleep 1
cd cross-test/js-adapter
PYTHON_BRIDGE_URL=http://127.0.0.1:9876 npx vitest run 2>&1 | tail -5
cd ../..
kill $BRIDGE_PID 2>/dev/null

# Linting clean
uv run ruff check src tests
uv run ruff format --check src tests
```

## Step 12: Commit Sync Work

Stage and commit in logical chunks. Suggested commit messages:

```bash
# Source/test parity changes
git add src/ tests/
git commit -m "feat: update to typopo ${LATEST_UPSTREAM} parity"

# Version bump (separate commit so it tags cleanly via /release)
git add pyproject.toml src/pytypopo/__init__.py
git commit -m "chore: bump version to ${NEW_VERSION}"

# Docs (if updated)
git add CLAUDE.md README.md
git commit -m "docs: update for ${NEW_VERSION}"

# Updated upstream pin (if cross-test/typopo submodule/clone tracks a specific commit)
# Note: cross-test/typopo is a regular clone, not a submodule, so its state isn't tracked
# in the parent repo. Skip.
```

## Step 13: Hand Off to Release Skill

```
══════════════════════════════════════════════════════════════
                    SYNC COMPLETE
══════════════════════════════════════════════════════════════

✓ Synced upstream:    ${LAST_UPSTREAM} → ${LATEST_UPSTREAM}
✓ Python tests:       passing
✓ Cross-tests:        passing
✓ Version bumped:     ${NEW_VERSION}
✓ Docs updated:       CLAUDE.md, README.md

Next step: run /release to publish ${NEW_VERSION}
══════════════════════════════════════════════════════════════
```

Do not run `/release` automatically — the user invokes it explicitly.

## Error Recovery

- **Cross-test failures the agent can't fix** → present them to the user, ask whether to skip and accept partial parity (rare; usually a real upstream behavior we need to port)
- **Python tests fail after parity fixes** → the JS behavior is authoritative; update Python test expectations (this is documented in `.claude/agents/brotest.md` step 8)
- **Upstream `cross-test/typopo` has uncommitted changes** → ask the user before discarding; they may have local debugging edits
- **Version already matches latest upstream** → suggest a port-fix release via `/release` instead (increments `+pyN`)

## Key References

- `.claude/agents/brotest.md` — parity-fixing agent workflow
- `.claude/skills/release/SKILL.md` — publishes the synced version
- `cross-test/README.md` — cross-test architecture
- `CLAUDE.md` § Versioning — `MAJOR.MINOR.PATCH+pyN` rules
