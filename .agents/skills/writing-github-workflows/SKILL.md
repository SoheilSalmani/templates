---
name: writing-github-workflows
description: Writes, reviews and simplifies GitHub Actions workflows so each reads at a glance, with a workflow per trigger, a job per check, one command per step, one naming grammar, and no comment doing a name's job. Covers names, triggers, permissions, action pins and lockfiles, timeouts, concurrency, toolchain setup and caches, required checks, and linting with actionlint and zizmor. Use when creating, editing or reviewing anything under .github/workflows, adding CI, a release or a deployment on GitHub, when a workflow grows inline scripts, drift checks or explanatory comments, or when a required check never reports. Not for GitLab CI or other CI systems, nor for the code of a JavaScript or Docker action.
---

# Writing GitHub workflows

A workflow is read far more often than it is written: by whoever reviews the change, by the developer whose check went red, and by branch protection, which treats job names as an API. Write it as an index of what CI does, not as a program. Every line is a trigger, a privilege, a toolchain, or a command a developer also runs on their own machine. **Logic lives in the project; the workflow wires it to GitHub.**

## Before you write

- **Read what exists**: every file in `.github/workflows/`, the project's entry points (Makefile, mise tasks, `package.json` scripts, justfile, nox or tox sessions, `.pre-commit-config.yaml`) and its pins (`mise.toml`, `.python-version`, `uv.lock`, `packageManager`). A step calls one of those entry points and never re-implements one.
- **Keep the repository's conventions**: how it pins actions (`.github/workflows/actions.lock`, SHA pins, Dependabot or Renovate), `.yml` or `.yaml`, and how it names steps.
- **Find what reads a name before changing it.** A job's `name`, or its id when it has none, is the name a branch rule requires; a workflow's `name` is what another workflow's `workflow_run` trigger selects. `references/naming.md` has the commands that find both.
- **Size the job.** A workflow with one check usually needs four steps, not a framework. A matrix, a composite action or a reusable workflow earns its place with its second or third caller.

## When rules collide

1. **Behaviour, release policy and trust boundaries are preserved.** Simplifying may move a check to where it belongs, never drop the invariant it enforces. Removing an invariant, or changing which file is authoritative, is a decision for the user: name it and ask, never fold it into a cleanup.
2. **Security beats readability.** Immutable pins, least privilege, untrusted input kept out of scripts and the choice of trigger are never traded for a shorter file. Win readability back through structure: fewer actions, a lockfile instead of SHA pins, a task instead of a script.
3. **A name something reads beats the naming grammar.** Rename a required job, or a workflow another one triggers on, only in the same change as whatever reads the name.
4. **The repository's conventions beat this skill's style defaults**, such as case, the file extension and which steps get names. Consistency inside one repository is worth more than agreement with a guide. Rule 2 is not style.
5. **Plain beats DRY.** Two short, similar jobs beat a YAML anchor, a one-entry matrix or a reusable workflow with one caller.

The rest of this skill sets defaults. Depart from one where a concrete responsibility needs it, such as a separate owner, a deliberate install boundary or a failure nobody yet understands, and say which responsibility it is.

## The shape

| Unit | Is | Split when | Never split to |
| --- | --- | --- | --- |
| Workflow | a trigger with a purpose: checks on pull requests, a release, a deployment, a schedule | the trigger, the audience or the owner differs | group by tool: a new check on the same trigger and owner is a job in the existing workflow |
| Job | a check someone reads, or work that needs its own runner, permissions, secrets or environment | it must run in parallel, report separately or hold other privileges | label phases: every job pays for a runner, a checkout and a toolchain |
| Step | one command whose failure means one thing | the failures mean different things to the reader | show progress: group long output with `::group::` |

A check job is usually three to five steps: check out, set up the toolchain, install when the run command does not, run the check. The count is a prompt to inspect, not a target: past six, write down what each step buys and cut the ones that buy nothing.

## Names

Workflows are nouns, jobs are verbs, steps are sentences. One grammar lets a reader predict a name before seeing it.

| Thing | Pattern | Examples | Not |
| --- | --- | --- | --- |
| File | the workflow's name in kebab-case, `.yml` | `ci.yml`, `release.yml`, `docs-site.yml` | `Run_Tests.yaml`, `workflow2.yml` |
| Workflow `name` | short noun phrase, sentence case, no emoji | `CI`, `Release`, `Deployment`, `Docs site`, `Nightly` | `Run CI`, `ESLint Check Workflow`, `🚀 Deploy` |
| Job id | kebab-case verb, with an object when siblings need one: what the job does, never the tool that does it | `lint`, `test`, `build`, `check-format`, `deploy-staging` | `eslint`, `pytest`, `job1`, `Build_Docs` |
| Job `name` | omitted, so the id is the check's name; set only to word a matrix or keep a name a rule already requires | `Test (${{ matrix.python }})` | `name: lint` repeating the id |
| Step `name` | imperative in sentence case: a verb, then what the step proves or produces; no full stop | `Check formatting`, `Install dependencies`, `Run unit tests`, `Publish to PyPI` | `Run prettier --check .`, `Formatting`, `Checkout code`, `Setup Node` |
| Step `id` | only when something reads it: a kebab-case noun for its output | `version`, `pnpm-store` | an id on every step |

- **Name every `run:` step. Name a `uses:` step only when the action's name hides what it does here**: `actions/checkout` and `setup-*` steps go unnamed; an `actions/upload-artifact` step is `Upload test reports`.
- **One verb per meaning**: `Check` for a read-only check that fails instead of fixing, `Lint`, `Run` for tests, `Set up` for a toolchain (two words; "setup" is the noun), `Install` for dependencies, `Build`, `Publish` to a registry, `Deploy` to an environment, `Upload` and `Download` for artifacts. Never `Ensure`, `Verify that` or `Make sure`.
- **Name the outcome, not the mechanism.** The command already shows the mechanism, so a name that repeats it says nothing.
- **A job is named for its check, not its tool**, so the check, and the rule that requires it, survive a change of tool.

Read `references/naming.md` for where each name appears, rewrites of names that went wrong, matrices, reusable workflows, and keeping required checks intact.

## Steps

- **A step runs one command a developer could paste into a terminal**, usually one line calling the project's entry point: `uv run pytest`, `pnpm test`, `mise run lint`, `make check`, `./gradlew build`. When CI needs a command no developer runs, decide which side should change.
- **No programs in YAML.** By default a `run:` block holds a few plain commands in sequence: no loops, no heredoc in another language, no `python -c`, no parsing another command's output. Logic like that becomes a task in the project's runner or a script file that also runs locally, called in one line, or it is designed away. Moving it only pays when the logic has a life outside CI: a script used once, just to make the YAML shorter, hides the complexity without removing it.
- **Delete a drift check by deleting the drift, but only when it guards a duplication.** A step that checks two copies of the same fact agree, such as a version pinned in two files or a list kept twice, goes once one copy is the source and the other is derived or deleted. When a generated copy must stay, check it with its own generator, `<regenerate> && git diff --exit-code`. A check that enforces policy, such as a release tag matching the committed version, is not a drift check: keep its invariant, and move it into a one-line command or a task. Never parse YAML or TOML in a step.
- **Configuration belongs to the tool, not the command line.** Paths, excludes, line length and dialect go in the tool's own configuration where it has a key for them, so CI and a developer run the same command. No input or flag that restates a default or does nothing in CI, such as setup-uv's `version: latest`, or a flag that hides progress output a tool already hides without a terminal.
- **No version numbers in the workflow**, except in a matrix that tests several. The project pins its tools and languages (`mise.toml`, `.python-version`, `uv.lock`, `required-version`, `packageManager`) and the setup step reads the pins.
- **One setup step per toolchain, and none for a tool another one provides.** `jdx/mise-action` installs everything `mise.toml` pins. `actions/setup-node` reads `.nvmrc` through `node-version-file`. `astral-sh/setup-uv` is enough for a uv project, because uv installs the Python the project pins; `actions/setup-python` beside it is a second source of truth. Use the setup action's own cache before writing an `actions/cache` step.
- **Don't install what the run command installs.** `uv run` syncs the environment it needs, so a `uv sync` step followed by `uv run --no-sync` is usually two steps doing one job. Keep a separate install step where it is a deliberate boundary, such as installing once for steps that do not go through uv, or keeping install failures apart from check failures.
- **When order matters, the order is visible.** Put steps in the order the reader should fix them, so the names explain it. When the order protects something beyond CI, it belongs where developers get it too, such as hook order in `.pre-commit-config.yaml` or a make prerequisite.
- **No routine diagnostic steps**: printing versions, `ls`, `env`, "check that X is installed", `set -x`, `sleep`. A setup action fails loudly, and the log already shows versions. A step that captures state for a failure nobody yet understands may stay, under `if: failure()` and with a name that says what it captures, until the failure is understood.
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
    timeout-minutes: 90 # the nightly suite replays a full day of traffic
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
uvx zizmor@1.32.0 .github/workflows                          # security audits at the default persona
```

- Use the repository's own pins of these tools when it has them, and check for newer releases before pinning new ones.
- actionlint 1.7.12 rejects `$/` references; ignore that one error until a release accepts them.
- A self-hosted runner's label needs `.github/actionlint.yaml` with `self-hosted-runner: {labels: [<label>]}`.
- Run each step's command from a clean checkout where you can. A workflow that lints clean but whose command fails is not done.

## Reviewing a workflow

1. Read it top to bottom and write down, for each step, what it proves or produces and which invariant, if any, it enforces. A step with nothing to write down goes; an invariant stays, wherever it ends up.
2. Report findings ranked: unsafe or broken first (floating pins, untrusted input in scripts, privileged triggers, write permissions at the top, actions on a removed runtime), then structure, then names and comments.
3. Give each finding its line, the problem, the fix, and where a removed responsibility now lives, such as "the version check is gone because the pre-commit hook now runs the linter version the lockfile pins".
4. Show the whole rewritten file, then the changes outside it that the rewrite depends on.
5. A workflow that already meets the bar gets "no changes needed". Never invent findings to fill a review.

## Before you finish

- Every step sets up a toolchain or runs one command a developer can run; any inline logic, kept guard or diagnostic step left in has a stated responsibility.
- Every invariant the old workflow enforced is still enforced somewhere, or the user chose to drop it.
- No comment says what a step does.
- Names follow the grammar, or the repository's own grammar throughout, and nothing that reads a job or workflow name (a branch rule, a `workflow_run` trigger) was broken by a rename.
- Every action is pinned to a SHA or a locked exact tag, `permissions` is explicit, untrusted input reaches scripts only through `env:`, and every job has `timeout-minutes`.
- No tool or language version appears in the YAML outside a matrix.
- actionlint and zizmor ran on the changed files, and their findings are fixed or reported.

## Sources

Checked 2026-11-18. GitHub changes Actions every month; recheck versions and compatibility facts before relying on them. The volatile ones, releases and their SHAs included, are kept in `references/toolchains.md` and `references/security.md`.

- GitHub Docs: [workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax), [events that trigger workflows](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows) (`workflow_run` selects workflows by name), [secure use](https://docs.github.com/en/actions/reference/security/secure-use), [workflow dependency lockfiles](https://docs.github.com/en/actions/concepts/security/workflow-dependency-lockfiles), [troubleshooting required status checks](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks), [reusing workflow configurations](https://docs.github.com/en/actions/concepts/workflows-and-actions/reusing-workflow-configurations).
- GitHub changelog: [SHA-pinning policy](https://github.blog/changelog/2025-08-15-github-actions-policy-now-supports-blocking-and-sha-pinning-actions/) (2025-08-15), [YAML anchors](https://github.blog/changelog/2025-09-18-actions-yaml-anchors-and-non-public-workflow-templates/) (2025-09-18), [self-repository references](https://github.blog/changelog/2026-07-30-reference-same-repository-actions-with-self-repository-syntax/) (2026-07-30), [Node 20 removed](https://github.blog/changelog/2026-09-23-node-20-is-no-longer-available-in-github-actions/) (2026-09-23), [workflow lockfiles generally available](https://github.blog/changelog/2026-10-28-github-actions-workflow-lockfiles-are-generally-available/) (2026-10-28).
- [zizmor audits](https://docs.zizmor.sh/audits/); [actionlint checks](https://github.com/rhysd/actionlint/blob/main/docs/checks.md); [OpenSSF Scorecard checks](https://github.com/ossf/scorecard/blob/main/docs/checks.md).
- [uv's GitHub Actions guide](https://docs.astral.sh/uv/guides/integration/github/) and the [`astral-sh/setup-uv` v8.0.0 release notes](https://github.com/astral-sh/setup-uv/releases/tag/v8.0.0); [`actions/setup-node`](https://github.com/actions/setup-node); [pre-commit's `unsupported` language](https://pre-commit.com/#unsupported) and [repository-local hooks](https://pre-commit.com/#repository-local-hooks).
- [`bitwarden/workflow-linter`](https://github.com/bitwarden/workflow-linter); the CI workflows of fifteen widely used repositories, among them `astral-sh/uv`, `python/cpython`, `cli/cli`, `pypa/pip` and `pallets/flask`; [Pact's CI guide for contributors](https://docs.pact.io/contributing/ci); Ian Duncan, ["GitHub Actions Is Slowly Killing Your Engineering Team"](https://iankduncan.com/engineering/2026-02-05-github-actions-killing-your-team) (2026-02-05).
