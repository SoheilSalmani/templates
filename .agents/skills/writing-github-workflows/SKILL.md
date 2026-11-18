---
name: writing-github-workflows
description: Writes, reviews and simplifies GitHub Actions workflows so each reads at a glance, with a workflow per trigger, a job per check, one command per step, one naming grammar, and no comment doing a name's job. Covers names, triggers, permissions, action pins and lockfiles, timeouts, concurrency, toolchain setup and caches, required checks, and linting with actionlint and zizmor. Use when creating, editing or reviewing anything under .github/workflows, adding CI, a release or a deployment on GitHub, when a workflow grows inline scripts, drift checks or explanatory comments, or when a required check never reports. Not for GitLab CI or other CI systems, nor for the code of a JavaScript or Docker action.
---

# Writing GitHub workflows

A workflow is read far more often than it is written: by whoever reviews the change, by the developer whose check went red, and by branch protection, which treats job names as an API. Write it as an index of what CI does, not as a program. Every line is a trigger, a privilege, a toolchain, or a command a developer also runs on their own machine. **Logic lives in the project; the workflow wires it to GitHub.**

## Before you write

- **Read what exists**: every file in `.github/workflows/`, the project's entry points (Makefile, mise tasks, `package.json` scripts, justfile, nox or tox sessions, `.pre-commit-config.yaml`) and its pins (`mise.toml`, `.python-version`, `uv.lock`, `packageManager`). A step calls one of those entry points and never re-implements one.
- **Keep the repository's conventions**: how it pins actions (`.github/workflows/actions.lock`, SHA pins, Dependabot or Renovate), `.yml` or `.yaml`, and how it names steps.
- **Find the required checks before renaming a job.** A job's `name`, or its id when it has none, is the name a branch rule requires; `references/naming.md` has the command that lists them.
- **Size the job.** A workflow with one check needs four steps, not a framework. A matrix, a composite action or a reusable workflow earns its place with its second or third caller.

## When rules collide

1. **Security beats readability.** Immutable pins, least privilege, untrusted input kept out of scripts and the choice of trigger are never traded for a shorter file. Win readability back through structure: fewer actions, a lockfile instead of SHA pins, a task instead of a script.
2. **A required check's name beats the naming grammar.** Rename a required job only in the same change as the rule that requires it.
3. **The repository's conventions beat this skill's style defaults**, such as case, the file extension and which steps get names. Consistency inside one repository is worth more than agreement with a guide. Rule 1 is not style.
4. **Plain beats DRY.** Two short, similar jobs beat a YAML anchor, a one-entry matrix or a reusable workflow with one caller.

## The shape

| Unit | Is | Split when | Never split to |
| --- | --- | --- | --- |
| Workflow | a trigger with a purpose: checks on pull requests, a release, a deployment, a schedule | the trigger or the audience differs | group by tool: a new pull request check is a job in the existing workflow |
| Job | a check someone reads, or work that needs its own runner, permissions, secrets or environment | it must run in parallel, report separately or hold other privileges | label phases: every job pays for a runner, a checkout and a toolchain |
| Step | one command whose failure means one thing | the failures mean different things to the reader | show progress: group long output with `::group::` |

A check job is three to five steps: check out, set up the toolchain, install when the run command does not, run the check. Past six, write down what each step buys and cut the ones that buy nothing.

## Names

Workflows are nouns, jobs are verbs, steps are sentences. One grammar lets a reader predict a name before seeing it.

| Thing | Pattern | Examples | Not |
| --- | --- | --- | --- |
| File | the workflow's name in kebab-case, `.yml` | `ci.yml`, `release.yml`, `docs-site.yml` | `SQL_Format.yaml`, `workflow2.yml` |
| Workflow `name` | short noun phrase, sentence case, no emoji | `CI`, `Release`, `Deployment`, `Docs site`, `Nightly` | `Run CI`, `SQL Format Check Workflow`, `🚀 Deploy` |
| Job id | kebab-case verb, with an object when siblings need one: what the job does, never the tool that does it | `lint`, `test`, `build`, `check-format`, `deploy-staging` | `sqlfmt`, `ruff`, `job1`, `Build_Docs` |
| Job `name` | omitted, so the id is the check's name; set only to word a matrix or keep a name a rule already requires | `Test (${{ matrix.python }})` | `name: sqlfmt` repeating the id |
| Step `name` | imperative in sentence case: a verb, then what the step proves or produces; no full stop | `Check SQL formatting`, `Install dependencies`, `Run unit tests`, `Publish to PyPI` | `Run sqlfmt --diff`, `SQL formatting`, `Checkout code`, `Setup Node` |
| Step `id` | only when something reads it: a kebab-case noun for its output | `version`, `pnpm-store` | an id on every step |

- **Name every `run:` step. Name a `uses:` step only when the action's name hides what it does here**: `actions/checkout` and `setup-*` steps go unnamed; an `actions/upload-artifact` step is `Upload test reports`.
- **One verb per meaning**: `Check` for a read-only check that fails instead of fixing, `Lint`, `Run` for tests, `Set up` for a toolchain (two words; "setup" is the noun), `Install` for dependencies, `Build`, `Publish` to a registry, `Deploy` to an environment, `Upload` and `Download` for artifacts. Never `Ensure`, `Verify that` or `Make sure`.
- **Name the outcome, not the mechanism.** The command already shows the mechanism, so a name that repeats it says nothing.
- **A job is named for its check, not its tool**, so the check, and the rule that requires it, survive a change of tool.

Read `references/naming.md` for where each name appears, rewrites of names that went wrong, matrices, reusable workflows, and keeping required checks intact.

## Steps

- **A step runs one command a developer could paste into a terminal**, usually one line calling the project's entry point: `uv run pytest`, `pnpm test`, `mise run lint`, `make check`, `./gradlew build`. When CI needs a command no developer runs, decide which side should change.
- **No programs in YAML.** A `run:` block holds at most a few plain commands in sequence: no conditionals or loops, no heredoc in another language, no `python -c`, no parsing another command's output. Logic like that becomes a task in the project's runner or a script file that also runs locally, called in one line, or it is designed away.
- **Delete a drift check by deleting the drift.** A step that checks two files agree, such as a version pinned in two places or a list kept twice, guards a duplication. Make one file the source and derive or delete the other. When a generated copy must stay, check it with its own generator, `<regenerate> && git diff --exit-code`. Never parse YAML or TOML in a step.
- **Configuration belongs to the tool, not the command line.** Paths, excludes, line length and dialect go in the tool's own configuration where it has a key for them, so CI and a developer run the same command. No input or flag that restates a default or does nothing in CI, such as setup-uv's `version: latest` or sqlfmt's `--no-progressbar`, which it already applies without a terminal.
- **No version numbers in the workflow**, except in a matrix that tests several. The project pins its tools and languages (`mise.toml`, `.python-version`, `uv.lock`, `required-version`, `packageManager`) and the setup step reads the pins.
- **One setup step per toolchain, and none for a tool another one provides.** `jdx/mise-action` installs everything `mise.toml` pins. `astral-sh/setup-uv` is enough for a uv project, because uv installs the Python the project pins; `actions/setup-python` beside it is a second source of truth. Use the setup action's own cache before writing an `actions/cache` step.
- **Don't install what the run command installs.** `uv run` syncs the environment it needs, so a `uv sync` step followed by `uv run --no-sync` is two steps doing one job.
- **When order matters, the order is visible.** Put steps in the order the reader should fix them, so the names explain it. When the order protects something beyond CI, it belongs where developers get it too, such as hook order in `.pre-commit-config.yaml` or a make prerequisite.
- **No diagnostic steps**: printing versions, `ls`, `env`, "check that X is installed", `set -x`, `sleep`. A setup action fails loudly, and the log already shows versions.
- **Let the tool explain its failure.** Prefer the tool's own diff, annotations or problem matcher (`--diff`, `--show-diff-on-failure`, the matchers `setup-*` actions register) to a script that prints advice.

Read `references/examples.md` for whole workflows before and after, including one that went from seven steps and an embedded Python program to four steps.

## Comments

**A comment that explains what a step does means the step is misnamed or does too much: rename or restructure it, then delete the comment.** No header narrating the workflow and no history ("added because…"): the name and trigger say what the workflow is, and the commit says why it changed.

Two kinds stay, one line each:

- the exact version after a SHA pin: `uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1`;
- the reason a line must stay as it is, where a careful reader would otherwise change it and no name can carry the reason.

Before:

```yaml
# One deploy at a time, and never one cancelled halfway.
concurrency:
  group: deploy
  cancel-in-progress: false
```

After, because a group given as a string lets one run at a time and `cancel-in-progress` is false by default:

```yaml
concurrency: deploy
```

A comment that stays:

```yaml
    runs-on: ubuntu-latest # pnpm check drives Chrome, which the arm images lack
```

## Triggers, permissions and pins

- **Checks run on `pull_request`.** Add `push` to the default branch only when something needs that run, such as a status badge, caches that pull requests restore, or a deployment. Add `workflow_dispatch` to anything a person may need to rerun.
- **Never let a filter skip a required workflow.** A workflow skipped by `paths` or `branches` leaves its checks pending, and the pull request cannot merge. Skip inside it with a job-level `if:`, which reports success.
- **`pull_request_target`, `workflow_run` and `issue_comment` run with secrets and write access.** Use one only for a stated reason, and never run the pull request's code under it.
- **`permissions: contents: read` at the top of every workflow.** A job that needs more lists its whole set, because a job's `permissions` replaces the workflow's.
- **Pin every action to something immutable**, through the repository's mechanism: exact tags such as `@v7.0.1` recorded in `.github/workflows/actions.lock`, or a full commit SHA with its version as a comment. A floating tag such as `@v7` is not a pin, and some actions no longer publish one: `astral-sh/setup-uv` has had none since v8.0.0. Pins nobody updates go stale, so where neither Dependabot nor Renovate watches the actions, say so and offer the configuration in `references/security.md`; don't add it unasked.
- **`persist-credentials: false` on every checkout** unless a later step pushes with git.
- **Untrusted input reaches a script only through `env:`**, quoted: `env: TITLE: ${{ github.event.pull_request.title }}` with `run: echo "$TITLE"`. Never put `${{ }}` inside `run:` for anything a contributor controls.
- **`timeout-minutes` on every job**, a few times its usual duration. The default is six hours.
- **Pull request workflows cancel superseded runs**: `group: ${{ github.workflow }}-${{ github.ref }}` with `cancel-in-progress: true`. A deployment never cancels one in progress: `concurrency: deploy`.
- `runs-on` takes a label, not a one-item list.

Read `references/security.md` when choosing or changing a pinning mechanism, granting a write permission, handling secrets, OIDC or environments, or using a privileged trigger, a cache in a release, or a self-hosted runner. Read `references/toolchains.md` when setting up Python, Node, Java or mise, or caching dependencies.

## Reuse

- A **matrix** for variations of one job.
- A **composite action** in the repository for a run of steps repeated in three or more jobs, referenced as `uses: $/.github/actions/<name>`, which needs no checkout and needs runners at 2.336.0 or later.
- A **reusable workflow** for whole jobs shared between workflows.
- **Avoid YAML anchors.** GitHub has accepted them since September 2025, but without merge keys they save little, and the reader has to jump around the file to read one job.
- Repeat two or three lines before abstracting them.

## Verify

These are commands for you to run, not lines for a workflow or for a page written for people:

```sh
mise x actionlint@1.7.12 shellcheck@0.11.0 -- actionlint   # syntax, expressions, runner labels, shellcheck on run: blocks
uvx zizmor@1.31.1 .github/workflows                          # security audits at the default persona
```

- Use the repository's own pins of these tools when it has them, and check for newer releases before pinning new ones.
- actionlint 1.7.12 rejects `$/` references; ignore that one error until a release accepts them.
- A self-hosted runner's label needs `.github/actionlint.yaml` with `self-hosted-runner: {labels: [<label>]}`.
- Run each step's command from a clean checkout where you can. A workflow that lints clean but whose command fails is not done.

## Reviewing a workflow

1. Read it top to bottom and write down, for each step, what it proves or produces. A step with nothing to write down goes.
2. Report findings ranked: unsafe or broken first (floating pins, untrusted input in scripts, privileged triggers, write permissions at the top, actions on a removed runtime), then structure, then names and comments.
3. Give each finding its line, the problem, the fix, and where a removed responsibility now lives, such as "the version check is gone because the hook now runs the locked sqlfmt".
4. Show the whole rewritten file, then the changes outside it that the rewrite depends on.
5. A workflow that already meets the bar gets "no changes needed". Never invent findings to fill a review.

## Before you finish

- Every step sets up a toolchain or runs one command a developer can run; no inline program, drift check or diagnostic step is left.
- No comment says what a step does.
- Names follow the grammar, or the repository's own grammar throughout, and no required check was renamed by accident.
- Every action is pinned to a SHA or a locked exact tag, `permissions` is explicit, untrusted input reaches scripts only through `env:`, and every job has `timeout-minutes`.
- No tool or language version appears in the YAML outside a matrix.
- actionlint and zizmor ran on the changed files, and their findings are fixed or reported.

## Sources

Checked 2026-10-23. GitHub changes Actions every month; recheck versions, and anything in preview, before relying on them.

- GitHub Docs: workflow syntax, the secure use reference, workflow dependency lockfiles, troubleshooting required status checks, reusing workflow configurations. GitHub changelog: 2025-08-15 (SHA-pinning policy), 2025-09-18 (YAML anchors), 2026-07-30 (self-repository references), 2026-09-23 (Node 20 removed), 2026-10-14 (workflow lockfiles, public preview).
- zizmor 1.31.1 audit documentation; actionlint 1.7.12 checks documentation; OpenSSF Scorecard checks.
- uv's GitHub Actions guide and the `astral-sh/setup-uv` v8.0.0 release notes; the pre-commit 4.4.0 changelog (`language: unsupported`); the sqlfmt configuration reference.
- Bitwarden's workflow conventions and `bitwarden/workflow-linter`; the CI workflows of fifteen widely used repositories, among them `astral-sh/uv`, `python/cpython`, `cli/cli`, `pypa/pip` and `dbt-labs/dbt-core`; Pact's CI guide for contributors; Ian Duncan, "GitHub Actions Is Slowly Killing Your Engineering Team" (2026-02-05).
