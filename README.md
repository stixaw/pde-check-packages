# pde-check-packages

Find which version of an npm package is installed across the GitHub repos owned by the
`@chghealthcare/pde` team.

It scans `dependencies` and `devDependencies` in each repo's `package.json`. Ownership is
verified through the repo's `CODEOWNERS` file, so only repos the PDE team actually owns are
reported.

## Prerequisites

- [`gh`](https://cli.github.com/) (GitHub CLI), authenticated with access to the `chghealthcare` org
- `jq` (only for the shell version)
- `python3` (only for the Python version)

```bash
gh auth status   # should show you're logged in
```

If not, run `gh auth login` yourself first.

## Usage

```bash
python3 check-pde-package.py <package-name>
# or
./check-pde-package.sh <package-name>
```

Both do the same thing and print the same format. Python is preferred.

### Example

```bash
$ python3 check-pde-package.py axios
pde-example-service: ^1.6.2
chg-work-example: ^1.7.0
```

Output is one `repo: version` line per repo where the package is found. **No output means the
package isn't a direct or dev dependency of any PDE-owned repo**, not that the check failed.

## How it works

1. Lists non-archived repos in the `chghealthcare` org.
2. Shortlists candidates by name (`pde-*`, `chg-work*`, `chg-ws*`, `chg-travel*`,
   case-insensitive) to keep API calls down.
3. Keeps only candidates whose `CODEOWNERS` references `@chghealthcare/pde`.
4. Reads `package.json` in each and reports the version of the requested package.

## Using it as a Claude Code skill

`SKILL.md` makes this usable as a Claude Code skill. Once installed, ask things like
"what version of axios are the PDE repos on?" and Claude will run the script for you.

## Adapting for another team or org

The org, the CODEOWNERS team, and the name-match regex are hardcoded near the top of both
scripts. Change them in both files.
