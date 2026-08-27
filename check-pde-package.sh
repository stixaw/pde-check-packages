#!/usr/bin/env bash
# Usage: ./scripts/check-pde-package.sh <package-name>
# Example: ./scripts/check-pde-package.sh axios
#
# Lists the version of a given npm package across all non-archived chghealthcare repos owned by
# @chghealthcare/pde. Candidates are name-matched (pde-*/chg-work*/chg-ws*/chg-travel*,
# case-insensitive) to keep the API-call count reasonable, then each candidate's ownership is
# verified against its CODEOWNERS file for @chghealthcare/pde — that's the actual source of
# truth, since naming doesn't line up cleanly.
# Checks both dependencies and devDependencies.

set -euo pipefail

if [ $# -eq 0 ]; then
  echo "Usage: $0 <package-name>"
  echo "Example: $0 axios"
  exit 1
fi

PACKAGE="$1"
TEAM="@chghealthcare/pde"

# Verify ownership via CODEOWNERS — check the standard locations for $TEAM.
is_owned() {
  local repo="$1" path content
  for path in ".github/CODEOWNERS" "CODEOWNERS" "docs/CODEOWNERS"; do
    content="$(gh api "repos/chghealthcare/$repo/contents/$path" --jq '.content' 2>/dev/null | base64 -d 2>/dev/null || true)"
    if [ -n "$content" ]; then
      echo "$content" | grep -qi -F "$TEAM" && return 0
      return 1
    fi
  done
  return 1
}

gh repo list chghealthcare --json name --limit 1000 --no-archived \
  --jq '.[] | select(.name | test("^(pde-|chg-work|chg-ws|chg-travel)"; "i")) | .name' \
  | while read -r repo; do
      is_owned "$repo" || continue
      result=$(gh api "repos/chghealthcare/$repo/contents/package.json" \
        --jq '.content' 2>/dev/null \
        | base64 -d 2>/dev/null \
        | jq -r --arg pkg "$PACKAGE" '.dependencies[$pkg] // .devDependencies[$pkg] // empty' 2>/dev/null)
      if [ -n "$result" ]; then
        echo "$repo: $result"
      fi
    done || true

# The while loop's exit status is that of its last command (often a failed
# match test). With `set -e`/pipefail that would abort the script with a
# spurious non-zero code, so neutralize the pipeline's status above.
