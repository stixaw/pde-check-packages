#!/usr/bin/env python3
"""
Usage: ./check-pde-package.py <package-name>
Example: ./check-pde-package.py axios

Lists the version of a given npm package across all non-archived chghealthcare repos owned by
@chghealthcare/pde. Candidates are name-matched (pde-*/chg-work*/chg-ws*/chg-travel*,
case-insensitive) to keep the API-call count reasonable, then each candidate's ownership is
verified against its CODEOWNERS file for @chghealthcare/pde -- that's the actual source of
truth, since naming doesn't line up cleanly.
Checks both dependencies and devDependencies.
"""

import base64
import json
import subprocess
import sys

TEAM = "@chghealthcare/pde"
CODEOWNERS_PATHS = (".github/CODEOWNERS", "CODEOWNERS", "docs/CODEOWNERS")


def gh_api_content(path: str) -> str | None:
    """Fetch a repo file's contents via `gh api` and base64-decode it, or None if unavailable."""
    result = subprocess.run(
        ["gh", "api", path, "--jq", ".content"],
        capture_output=True, text=True,
    )
    if result.returncode != 0 or not result.stdout.strip():
        return None
    try:
        return base64.b64decode(result.stdout.strip()).decode("utf-8", errors="replace")
    except (ValueError, UnicodeDecodeError):
        return None


def is_owned(repo: str) -> bool:
    for path in CODEOWNERS_PATHS:
        content = gh_api_content(f"repos/chghealthcare/{repo}/contents/{path}")
        if content is not None:
            return TEAM.lower() in content.lower()
    return False


def list_candidate_repos() -> list[str]:
    result = subprocess.run(
        [
            "gh", "repo", "list", "chghealthcare",
            "--json", "name", "--limit", "1000", "--no-archived",
            "--jq", '.[] | select(.name | test("^(pde-|chg-work|chg-ws|chg-travel)"; "i")) | .name',
        ],
        capture_output=True, text=True, check=True,
    )
    return [line for line in result.stdout.splitlines() if line]


def package_version(repo: str, package: str) -> str | None:
    content = gh_api_content(f"repos/chghealthcare/{repo}/contents/package.json")
    if content is None:
        return None
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return None
    return data.get("dependencies", {}).get(package) or data.get("devDependencies", {}).get(package)


def main() -> int:
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <package-name>")
        print(f"Example: {sys.argv[0]} axios")
        return 1

    package = sys.argv[1]

    for repo in list_candidate_repos():
        if not is_owned(repo):
            continue
        version = package_version(repo, package)
        if version:
            print(f"{repo}: {version}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
