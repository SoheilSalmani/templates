# Names in GitHub workflows

## Contents

- Where each name appears
- The grammar, with its reasons
- Verbs
- Rewrites
- Matrices and reusable workflows
- Required checks and other readers of a name

## Where each name appears

| Name | Shown in | Breaks when changed |
| --- | --- | --- |
| File path | the workflow's identity: badge URLs, `gh workflow run <file>`, and the Actions sidebar when `name` is missing | badges, scripts and documents that link it |
| Workflow `name` | the Actions sidebar, the first half of each check in a pull request, the badge's text | `workflow_run` triggers, whose `workflows:` list selects workflows by name; `gh run list --workflow <name>` in scripts |
| `run-name` | each run in the list of runs; by default the commit message or pull request title | nothing |
| Job id, or job `name` when set | the check's name on pull requests and commits, with matrix values appended; what branch rules require | required checks; `needs:` and `needs.<id>` read the id |
| Step `name` | the job's log; a step without one shows `Run` and its command's first line, or `Run owner/repo@<ref>`, which is a 40-character SHA once pinned | nothing |
| Step `id` | expressions such as `steps.<id>.outputs.<name>` | every expression that reads it |

A pull request lists each check as `<workflow name> / <job name> (<event>)`, such as `CI / test (pull_request)`. A required check matches the job's name with its matrix suffix and ignores the workflow's name, so two workflows with a job called `test` make one ambiguous check: keep job names unique across every workflow in the repository.

An id starts with a letter or `_` and holds letters, digits, `-` and `_`. Hyphens work in expressions, as in `needs.check-format.result`. An expression that names a missing id evaluates to an empty string without an error, which is one more reason to add ids only where something reads them.

## The grammar, with its reasons

- **Workflows are nouns**, because the sidebar lists what the repository has: `CI`, `Release`, `Deployment`, `Nightly`. `CI` is the usual name for the workflow that checks pull requests; nine of fifteen widely used repositories sampled in October 2026 use exactly that.
- **Files mirror the name** in kebab-case with `.yml`, so the file behind a sidebar entry is predictable: `CI` is `ci.yml`, `Docs site` is `docs-site.yml`. A workflow that only other workflows call takes a `reusable-` prefix, `reusable-build.yml`, so nobody looks for its trigger. Renaming a file breaks badges and `gh workflow run` calls, and renaming a workflow's `name` silently stops every `workflow_run` trigger that names it, so neither is a style fix: find the readers first.
- **Jobs are verbs**, because a check reads as what CI did: `CI / lint`, `CI / test`, `CI / check-format`, `Deployment / deploy-production`. Name the activity, never the tool: `typecheck`, not `mypy`; `check-format`, not `sqlfmt`. Tools are replaced more often than the checks they run, and a rule requires the check's name.
- **Steps are imperative sentences**, verb first and in sentence case, because the log reads as a list of instructions carried out: `Install dependencies`, `Check SQL formatting`, `Publish to PyPI`. Thirteen of the fifteen repositories put the verb first.
- **Ids are nouns for what they hold**: `version`, `pnpm-store`, `wheel-path`.

## Verbs

| Verb | For | Example |
| --- | --- | --- |
| `Set up` | a toolchain; usually unnamed, since the action says it | `Set up Python` |
| `Install` | the project's dependencies | `Install dependencies` |
| `Check` | a read-only check that fails instead of fixing | `Check SQL formatting`, `Check types`, `Check links` |
| `Lint` | a linter | `Lint Python` |
| `Run` | tests or benchmarks | `Run unit tests` |
| `Build` | an artefact | `Build the image`, `Build docs` |
| `Publish` | to a registry | `Publish to PyPI` |
| `Deploy` | to an environment | `Deploy to staging` |
| `Upload`, `Download` | artifacts | `Upload test reports` |
| `Log in to` | a registry or cloud | `Log in to GHCR` |

`Set up` and `Log in` are verbs; `setup` and `login` are nouns. Never `Ensure`, `Verify that`, `Make sure`, `Handle` or `Process`: they say that something happens, not what.

## Rewrites

| Before | After | Why |
| --- | --- | --- |
| `sql-format.yml` named `SQL Format`, one job, triggered like the pull request workflow and owned by the same people | a `check-format` job in the existing pull request workflow | a check on the same trigger and owner is a job, not a workflow; a workflow another team owns, or one with its own path filters, may stay separate |
| job `sqlfmt` with `name: sqlfmt` | job `check-format`, no `name` | named for its check; the `name` repeated the id |
| `name: Checkout code` on `actions/checkout` | no name | the action says it, and "checkout" is the noun |
| `name: Setup Node.js` on `actions/setup-node` | no name; `Set up Node.js` where the repository names every step | as above |
| `name: Install the dev tools` running `uv sync` | gone | `uv run` installs what it runs |
| `name: Check that the sqlfmt hook pins the locked versions` | gone | the duplication it guarded was removed |
| `name: Check that semi-structured keys are quoted` | `Check semi-structured keys are quoted` | "that" adds nothing |
| `name: Build & Package Binaries` | `Build binaries` | one verb, sentence case |
| `name: Get Package Version` | `id: version` and `name: Read the package version` | sentence case; the id is the noun later steps read |
| `- run: npm test` | `name: Run unit tests` above `run: npm test` | every `run:` step gets a name |
| job `build_and_test` | jobs `build` and `test`, or one job named for the check a reader cares about | "and" in a name means two things |

## Matrices and reusable workflows

- GitHub appends a matrix job's values to its name, as in `test (3.12, ubuntu-latest)`. Leave `name` off unless the wording matters. A `name` that contains any matrix expression gets nothing appended, so it must use every matrix variable, or two jobs end up with the same name.
- Changing a matrix value, or the order of its keys, changes the check names, and with them the required checks.
- A job that calls a reusable workflow shows as `<calling job> / <called job>`. Name the calling job for what it does, as you would any job.

## Required checks and other readers of a name

List what the rules require before renaming any job:

```sh
gh api repos/{owner}/{repo}/rules/branches/{branch} \
  --jq '.[] | select(.type == "required_status_checks") | .parameters.required_status_checks[].context'
```

Older branch protection, outside rulesets, shows its checks to administrators at `gh api repos/{owner}/{repo}/branches/{branch}/protection/required_status_checks --jq '.contexts'`.

- Rename a required job only in the same change as the rule, and say so to whoever administers it.
- A workflow skipped by a `paths` or `branches` filter leaves its checks pending; a job skipped by `if:` reports success. So decide inside the workflow, with job-level `if:`.
- Where jobs depend on one another or vary by matrix, require one final job instead of each of them, so the others can change freely. `astral-sh/uv` requires only such a job.

```yaml
  gate:
    if: always()
    needs: [lint, test, check-format]
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - name: Fail when a check failed
        if: contains(needs.*.result, 'failure') || contains(needs.*.result, 'cancelled')
        run: exit 1
```

- A repository with a merge queue also triggers its required workflows on `merge_group`, or the queue waits forever.

Before renaming a workflow, find the workflows that trigger on it; `workflow_run` only reads workflows in the same repository:

```sh
grep -rn -A4 'workflow_run' .github/workflows   # each workflows: [ ... ] entry is a workflow name
```

Renaming `Build` to `CI` while a deploy workflow still says `workflows: [Build]` raises no error anywhere: the deploy simply never runs again. Change both in one commit, or keep the old name.
