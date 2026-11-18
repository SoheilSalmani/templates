# Security in GitHub workflows

Checked 2026-11-18. These facts move with GitHub's releases; recheck them before relying on them.

## Contents

- Pinning actions
- Keeping pins current
- Permissions
- Untrusted input
- Privileged triggers
- Secrets, OIDC and environments
- Caches
- Runners
- Linters

## Pinning actions

A tag can move. In March 2025 an attacker repointed the tags of `tj-actions/changed-files` at a commit that printed secrets into build logs, and through `reviewdog/action-setup@v1`, called by other actions, the same campaign reached workflows whatever their own pins said. Pin every action to something that cannot move.

| Mechanism | In the YAML | Covers | State on 2026-11-18 |
| --- | --- | --- | --- |
| [Workflow lockfile](https://docs.github.com/en/actions/concepts/security/workflow-dependency-lockfiles), `.github/workflows/actions.lock` | exact tags: `actions/checkout@v7.0.1` | each action and the actions it calls; not reusable workflows from other repositories, nor container images | [generally available since 2026-10-28](https://github.blog/changelog/2026-10-28-github-actions-workflow-lockfiles-are-generally-available/) on github.com plans, not on GitHub Enterprise Server; `gh actions-lock` is still pre-1.0; zizmor reads it [experimentally since 1.32.0](https://docs.zizmor.sh/usage/); check whether your OpenSSF Scorecard release recognises it |
| SHA pin | `actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1` | the action named, not what it calls | what zizmor, Scorecard and [GitHub's SHA-pinning policy](https://github.blog/changelog/2025-08-15-github-actions-policy-now-supports-blocking-and-sha-pinning-actions/) check |

Use the one the repository uses. For a repository with neither, the lockfile is the readable choice and also locks the actions an action calls; SHA pins remain the choice on GitHub Enterprise Server, or where a linter or policy the repository relies on does not read the lockfile yet.

Never pin a branch (`@main`) or a floating major tag (`@v7`). An action without a major tag, such as `astral-sh/setup-uv` since v8.0.0, is a reminder that the tag was never a pin.

Resolve a pin:

```sh
gh api repos/actions/checkout/releases/latest --jq .tag_name   # the newest release
gh api repos/actions/checkout/commits/v7.0.1 --jq .sha         # the commit it points at
```

The comment carries the full version, `# v7.0.1`, never `# v7`: zizmor's `ref-version-mismatch` audit compares the two, and Dependabot rewrites the comment with the SHA.

With a lockfile:

```sh
gh extension install github/gh-actions-lock
gh actions-lock            # write or fix the lockfile, narrowing @v7 to the exact tag
gh actions-lock --verify   # check without writing, as in CI
```

Rerun `gh actions-lock` after every change to a `uses:`. A same-repository `./` action that calls remote actions has to become `$/` first, which `--migrate-local-actions` does.

## Keeping pins current

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: github-actions
    directory: /
    schedule:
      interval: weekly
    cooldown:
      default-days: 7
```

Dependabot moves the SHA and its comment together, and regenerates a lockfile entry in the same pull request. It waits three days after a release by default; zizmor's `dependabot-cooldown` audit asks for seven. It raises no security alerts for SHA-pinned actions, so zizmor's online `known-vulnerable-actions` audit is what catches a vulnerable pin. Renovate pins and updates SHAs with the `helpers:pinGitHubActionDigests` preset.

## Permissions

- `permissions: contents: read` at the top of the workflow. Every scope a `permissions` block does not list is `none`.
- A job's `permissions` replaces the workflow's, so a job that needs more lists its whole set, `contents: read` included.
- The usual grants, each on the one job that needs it: `id-token: write` for OIDC, such as trusted publishing or a cloud login; `packages: write` to push to GHCR; `contents: write` to push tags or create releases; `pull-requests: write` to comment; `pages: write` with `id-token: write` to deploy Pages; `security-events: write` to upload SARIF.
- `persist-credentials: false` on `actions/checkout` unless a later step pushes with git. Since checkout v6 the persisted token sits outside the workspace, but every later step in the job can still read it.

## Untrusted input

A contributor controls the pull request's title, body and branch name (`github.head_ref`), commit messages, issue, comment and review bodies, and most of `github.event`. `${{ }}` is expanded into the script before the shell sees it, so any of these inside `run:` is code injection. Pass them through `env:` and quote the variable; `${{ env.NAME }}` inside `run:` is templated too, so write `"$NAME"`.

Before:

```yaml
      - name: Deploy the preview
        run: ./scripts/deploy-preview.sh "${{ github.head_ref }}"
```

After:

```yaml
      - name: Deploy the preview
        env:
          BRANCH: ${{ github.head_ref }}
        run: ./scripts/deploy-preview.sh "$BRANCH"
```

Variables the runner sets, such as `GITHUB_REF_NAME` and `GITHUB_SHA`, are already in the environment; read them as `"$GITHUB_REF_NAME"` instead of through `${{ github.ref_name }}`.

## Privileged triggers

- `pull_request` from a fork runs with a read-only token and no secrets. It is the trigger for checks.
- `pull_request_target`, `workflow_run` and `issue_comment` run in the base repository with its secrets and, often, write access. Code from the pull request is data there: never built, installed or run. Since v7, `actions/checkout` refuses a fork's code under `pull_request_target` or `workflow_run` unless given `allow-unsafe-pr-checkout: true`; needing that input is the sign to stop.
- For privilege separation, the unprivileged `pull_request` workflow uploads its results and a `workflow_run` workflow reads them as data.
- Public repositories have a default policy that blocks `pull_request_target`. It runs in evaluate mode now; GitHub's page on securely using `pull_request_target` gives 2026-12-02 as the date it is enforced.

## Secrets, OIDC and environments

- Give a secret to the step that needs it, through that step's `env:`, never to the whole workflow.
- Prefer OIDC to stored keys: PyPI trusted publishing (`uv publish` uses it on GitHub Actions with no token, once the PyPI project trusts the workflow), and cloud logins that assume a role.
- Put deployment secrets in an `environment:` with required reviewers; the job cannot read them until someone approves.
- Never `secrets: inherit`, `toJSON(secrets)`, or one secret holding a JSON document.

## Caches

- A cache saved by one run is restored by others, so a release or publish job restores none: `cache-mode: none` on the job, or the setup action's cache turned off. setup-uv already leaves its cache off for tag pushes and releases.
- Since September 2026 `cache-mode` (`read`, `write`, `write-only`, `none`) sets cache access per workflow or job, and low-trust triggers such as `pull_request_target` get `read` by default.

## Runners

- A self-hosted runner never serves a public repository: a fork's pull request would run on it.
- Prefer ephemeral self-hosted runners, such as Actions Runner Controller or just-in-time runners; a persistent one keeps whatever the last job left.
- `$/` references need runner 2.336.0 or later. Runners run every JavaScript action on Node 24 since 2026-09-23, so an action release that still declares `node20`, such as setup-uv v4, is due for an upgrade.

## Linters

- **actionlint** types expressions, checks ids, runner labels and action inputs, and runs shellcheck on `run:` blocks when shellcheck is on the `PATH`. Its input checks for popular actions only work on `@vN` references, so SHA-pinned steps lose them. 1.7.12, still the latest release on 2026-11-18, rejects `$/` references.
- **zizmor** audits security. At the default persona it wants every action hash-pinned (since 1.20), `persist-credentials: false`, no `${{ }}` from untrusted contexts in scripts, least-privilege permissions, no cache in release workflows and trusted publishing where a registry offers it. `--persona=pedantic` also asks for a `name` on every job and for `concurrency` limits; this skill leaves job names off on purpose, so pedantic's `anonymous-definition` findings are expected.
- In CI, `zizmorcore/zizmor-action` runs zizmor; actionlint has a Docker image and pre-commit hooks. Pin both like any other action.
