---
name: pde-check-packages
description: Check which version of an npm package is installed across GitHub repos owned by the @chghealthcare/pde team, by scanning package.json dependencies/devDependencies of name-matched repos (pde-*, chg-work*, chg-ws*, chg-travel*) and verifying ownership via each repo's CODEOWNERS file. Use when the user asks what version of a package the PDE team's repos are on, wants to find outdated or inconsistent package versions across those repos, asks "which repos use package X," or wants to audit a dependency before a bump/migration.
---

# Check PDE package versions across repos

Lists the installed version of a given npm package across all non-archived `chghealthcare`
repos actually owned by `@chghealthcare/pde`. Candidates are first name-matched
(`pde-*`/`chg-work*`/`chg-ws*`/`chg-travel*`, case-insensitive) to keep the API-call count
reasonable, then each candidate's ownership is verified against its CODEOWNERS file for
`@chghealthcare/pde` — that's the actual source of truth, since naming doesn't line up cleanly
with ownership. Checks both `dependencies` and `devDependencies`.

## Prerequisites

Requires `gh` (GitHub CLI) authenticated with access to the `chghealthcare` org, and `jq` if
using the shell variant. Check once, up front:

```bash
gh auth status
```

If that fails, stop and tell the user — don't attempt `gh auth login` yourself, it's an
interactive flow that needs the user's own action.

## Running it

Two equivalent implementations ship with this skill — same logic, same output format
(`repo: version`, one per line, only for repos where the package is found). Prefer the Python
version by default (more robust JSON handling); fall back to the shell version if Python isn't
available.

```bash
python3 check-pde-package.py <package-name>
# or
./check-pde-package.sh <package-name>
```

Example:

```bash
python3 check-pde-package.py axios
```

A run with no matches prints nothing — that means no CODEOWNERS-verified `@chghealthcare/pde`
repo has that package as a direct or dev dependency, not that the check failed. Report absence
of output as "not found in any PDE-owned repo," not as an error.

## Adapting for a different team/org

Both scripts hardcode `chghealthcare` as the org and `@chghealthcare/pde` as the CODEOWNERS
team, and the `pde-|chg-work|chg-ws|chg-travel` name-match regex used to shortlist candidate
repos. To point this at a different org/team, change those constants in both files
(`TEAM`/org variables near the top) — the CODEOWNERS-verification approach itself isn't
org-specific.
