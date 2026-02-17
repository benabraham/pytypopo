---
name: release
description: Create a GitHub release with semantic versioning. Checks git status, analyzes code for breaking changes requiring user action, generates release notes, and publishes release. Use when user says "release", "create release", "publish", "new version", or "bump version".
---

# GitHub Release Skill

Create a new release for pytypopo with semantic versioning.

## Versioning Scheme

pytypopo uses a dual versioning scheme: `MAJOR.MINOR.PATCH+pyN`

- `MAJOR.MINOR.PATCH` tracks the upstream typopo JS library version
- `+pyN` is the Python port-specific revision (local build suffix)

**Version bump rules:**
1. **Upstream sync**: When porting a new upstream typopo version, change `MAJOR.MINOR.PATCH` to match upstream and reset `+pyN` to `+py0`
2. **Port-specific fix**: For Python-only fixes (no upstream change), increment only `+pyN` (e.g., `+py1` → `+py2`)
3. **Never** change `MAJOR.MINOR.PATCH` independently of upstream

**Version is stored in TWO places** (must stay in sync):
- `pyproject.toml` → `version = "X.Y.Z+pyN"`
- `src/pytypopo/__init__.py` → `__version__ = "X.Y.Z+pyN"`

**Tag format**: `vX.Y.Z+pyN` (e.g., `v3.0.0+py0`)

## Step 1: Pre-flight Checks

Run ALL checks silently, abort with clear message if any fail:

```bash
# Must be clean
git status --porcelain

# Must be on main
git branch --show-current

# Fetch and check sync status
git fetch origin
git rev-list HEAD..origin/main --count  # must be 0
git rev-list origin/main..HEAD --count  # if 0, warn "nothing to release"
```

Abort conditions:
- Uncommitted changes → "Commit or stash changes first"
- Not on main → "Switch to main branch first"
- Behind remote → "Pull from origin first"
- Nothing to release → "No new commits since last release"

## Step 2: Analyze Code for User-Facing Changes

### Get current version and diff
```bash
git tag --sort=-v:refname | head -1  # e.g., v2.9.1+py1
git diff <last-tag>..HEAD -- src/ tests/
git log <last-tag>..HEAD --oneline --no-merges
```

### Verify documentation is updated

Read ALL documentation files and verify changes are reflected:

**README.md** - User-facing documentation:

| Code Change | Must Be Documented |
|-------------|-------------------|
| New locale added | Listed in supported locales section |
| API parameter added/changed | Updated in usage/API section |
| New module/feature | Described in features section |
| Changed default behavior | Updated in relevant sections |
| New dependencies | Listed in requirements/installation |

**CLAUDE.md** - Developer documentation:

| Code Change | Must Be Documented |
|-------------|-------------------|
| New module/file | Listed in Architecture section |
| New locale | Listed in Supported Locales |
| API change | Updated in API section |
| New processing step | Listed in Module Processing Order |
| Version number | Updated at top |

**If documentation is missing, use AskUserQuestion:**

```
⚠ DOCUMENTATION INCOMPLETE

Missing from README.md:
  • New locale "xy" not documented
  • New API parameter not listed

Missing from CLAUDE.md:
  • New module not listed in Architecture
  • Version number stale
```

**Use AskUserQuestion tool:**
- Question: "Documentation is incomplete. How to proceed?"
- Header: "Docs"
- Options:
  - "Update docs now (Recommended)" - update all missing docs, commit with `docs: ...` message, then continue release
  - "Abort" - stop and let user handle manually

**If user selects "Update docs now":**
1. Update README.md with missing items
2. Update CLAUDE.md with missing items
3. Commit all doc changes: `git commit -am "docs: update for vX.Y.Z+pyN release"`
4. Continue to version question

### Breaking changes = user's code stops working

A breaking change is anything that **requires end users to take action** or their existing code stops working correctly.

| What Breaks | How to Detect in Diff | User Impact |
|-------------|----------------------|-------------|
| `fix_typos()` param renamed/removed | Parameter removed from function signature | User's function call errors |
| Locale code changed | Locale string changed (e.g., `en-us` → `en_us`) | User's locale param rejected |
| Module function removed | Public function deleted | User's direct import fails |
| Output behavior changed | Different typography rules applied | User's expected output changes silently |
| Python version dropped | `python_requires` changed | User's Python version unsupported |

**NOT breaking** (no user action needed):
- Adding new locales (old code still works)
- Adding new fix rules (more typos corrected)
- Internal refactoring (no API changes)
- Adding new optional parameters with defaults
- Bug fixes that correct wrong typography output

### New features = new capabilities users can opt into

| Feature Type | How to Detect |
|--------------|---------------|
| New locale | New file in `src/pytypopo/locale/` |
| New fix module | New file in `src/pytypopo/modules/` |
| New API parameter | New kwarg in `fix_typos()` |
| New typography rule | New regex/fix pattern in existing module |

### Identify contributors from merged PRs

Check if any commits since the last release came from merged pull requests:

```bash
# List merged PRs whose merge commit is in the release range
gh pr list --state merged --base main --json number,author,title \
  --jq '.[] | "\(.number)\t\(.author.login)\t\(.title)"'
```

Cross-reference with `git log vX.Y.Z+pyN..HEAD` to find PRs whose commits are in this release. Collect each external contributor's `@username` and PR number. The repo owner is not listed as a contributor.

**This information is required for Step 4** — contributors must always be thanked in the release notes.

### Determine version bump type

1. **Upstream sync**: `MAJOR.MINOR.PATCH` changes to match new upstream typopo version, `+pyN` resets to `+py0`
2. **Port fix**: Only `+pyN` increments (e.g., `3.0.0+py0` → `3.0.0+py1`)

## Step 3: Present Plan & First Question

Show analysis focused on user impact:

```
══════════════════════════════════════════════════════════════
                      RELEASE PLAN
══════════════════════════════════════════════════════════════

Current version: v2.9.1+py1
Commits since last release: 4

User impact analysis:

  Breaking (requires user action): none

  New features (opt-in):
    • New locale: "rue" - Rusyn language support

  Fixes/improvements:
    • Better handling of double quotes after numbers

Release type: Upstream sync (typopo 3.0.0)
Recommended: v3.0.0+py0
══════════════════════════════════════════════════════════════
```

For port-only releases:
```
Release type: Port fix
Recommended: v3.0.0+py1
```

If breaking changes found:
```
  ⚠ BREAKING (requires user action):
    • Parameter `keep_markdown_code_blocks` removed from fix_typos()
      → Users must remove this parameter from their calls
```

**Use AskUserQuestion tool:**
- Question: "Confirm version?"
- Header: "Version"
- Options (detected version first with "(Recommended)"):
  - Put detected version first with "(Recommended)"
  - Include alternative version numbers

## Step 4: Show Release Notes & Second Question

Generate release notes emphasizing user impact:

```
══════════════════════════════════════════════════════════════
                    RELEASE NOTES DRAFT
══════════════════════════════════════════════════════════════
Version: v3.0.0+py0

## What's Changed

### Upstream Sync: typopo 3.0.0

- **Breaking**: Removed `keep_markdown_code_blocks` parameter
- **Breaking**: Removed `remove_whitespaces_before_markdown_list` parameter
- Fixed double quotes false positive after numbers

### Python Port
- Reordered multiplication sign operations to match upstream

Thanks to @contributor for the contribution (#42)!

**Full Changelog**: https://github.com/benabraham/pytypopo/compare/v2.9.1+py1...v3.0.0+py0
══════════════════════════════════════════════════════════════
```

**Contributors section is mandatory** when the release includes commits from merged PRs. Always add a "Thanks to @user (#N)!" line for each external contributor identified in Step 2. For multiple contributors: "Thanks to @user1 (#1) and @user2 (#5)!". Omit the line only if all commits were authored by the repo owner.

For breaking changes, add migration guide:
```
### ⚠ Breaking Changes

**`keep_markdown_code_blocks` parameter removed**
- If you pass `keep_markdown_code_blocks=True` to `fix_typos()`, remove it
- Backtick characters are now treated as regular characters

**`remove_whitespaces_before_markdown_list` parameter removed**
- If you pass this parameter, remove it
- Whitespace before markdown lists is now always stripped
```

**Use AskUserQuestion tool:**
- Question: "Release notes look good?"
- Header: "Notes"
- Options:
  - "Publish as shown (Recommended)"
  - "Edit notes" - wait for user's modified version

## Step 4.5: Bump Version

Before creating the tag, update the version in both locations:

```bash
# Check current versions are in sync
grep '^version = ' pyproject.toml
grep '^__version__ = ' src/pytypopo/__init__.py

# Update pyproject.toml
sed -i 's/^version = ".*"/version = "3.0.0+py0"/' pyproject.toml

# Update __init__.py
sed -i 's/^__version__ = ".*"/__version__ = "3.0.0+py0"/' src/pytypopo/__init__.py

# Verify both match
grep '^version = ' pyproject.toml
grep '^__version__ = ' src/pytypopo/__init__.py

# Commit the version bump
git commit -am "chore: bump version to 3.0.0+py0"
```

**Important:** This commit becomes the tagged release commit. Both version locations must match the tag being created.

## Step 5: Execute Release

Only after both confirmations:

```bash
# Create annotated tag
git tag -a v3.0.0+py0 -m "v3.0.0+py0"

# Push commit + tag
git push origin main v3.0.0+py0

# Create GitHub release
gh release create v3.0.0+py0 --title "v3.0.0+py0" --notes "$(cat <<'EOF'
## What's Changed
...
EOF
)"
```

## Step 6: Confirm Success

```
✓ Tag v3.0.0+py0 created and pushed
✓ GitHub release published

View release: https://github.com/benabraham/pytypopo/releases/tag/v3.0.0+py0
```

## Error Recovery

- Tag creation fails → show error, no cleanup needed
- Push fails → `git tag -d vX.Y.Z+pyN` to remove local tag, show error
- gh release fails → tag already pushed, provide URL: https://github.com/benabraham/pytypopo/releases/new?tag=vX.Y.Z+pyN
