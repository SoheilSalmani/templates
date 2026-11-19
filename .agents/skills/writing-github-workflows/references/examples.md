# Workflows before and after

The SHAs below are the commits of the releases in their comments on 2026-11-18. Resolve current ones before copying: `gh api repos/<owner>/<repo>/commits/<tag> --jq .sha`.

## Contents

- A pull request workflow from scratch
- A check that grew a program
- A release that checks the tag against the version
- A deployment whose logic belonged to its task

## A pull request workflow from scratch

A Node project with ESLint, Prettier and a test script, and its Node version in `.nvmrc`. `push` to `main` is there because a cache saved on `main` is the one pull requests restore.

```yaml
name: CI

on:
  pull_request:
  push:
    branches: [main]

permissions:
  contents: read

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  lint:
    name: Lint
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
        with:
          persist-credentials: false
      - uses: actions/setup-node@949feb2413d6458794dcd2491c4babbbce0c15c1 # v7.1.0
        with:
          node-version-file: .nvmrc
          cache: npm
      - name: Install dependencies
        run: npm ci
      - name: Check formatting
        run: npm run format:check
      - name: Lint JavaScript
        run: npm run lint

  test:
    name: Test
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
        with:
          persist-credentials: false
      - uses: actions/setup-node@949feb2413d6458794dcd2491c4babbbce0c15c1 # v7.1.0
        with:
          node-version-file: .nvmrc
          cache: npm
      - name: Install dependencies
        run: npm ci
      - name: Run tests
        run: npm test
```

No Node version appears: setup-node reads `.nvmrc`. The install step is right here, because unlike `uv run`, `npm test` installs nothing; each check is a script from `package.json`, so CI and a developer run the same command.

## A check that grew a program

A Python project that lints with ruff, both from its dev dependencies and from a pre-commit hook. Before: seven steps, a Python program in a heredoc, and two comments explaining the YAML.

```yaml
---
name: Lint

# Lint runs apart from ci.yml, whose test job needs the database
# secret, so pull requests from forks still get a lint result.
on:
  pull_request:
    branches:
      - main

permissions:
  contents: read

jobs:
  ruff:
    name: ruff
    runs-on: ["ubuntu-latest"]
    timeout-minutes: 10

    steps:
      - name: Checkout code
        uses: actions/checkout@v7

      - name: Set up Python
        uses: actions/setup-python@v7
        with:
          python-version: '3.12'

      - name: Install uv
        uses: astral-sh/setup-uv@v4
        with:
          version: "latest"

      - name: Install the dev tools
        run: uv sync --frozen --only-group dev

      - name: Check that the ruff hook pins the locked version
        run: |
          uv run --no-sync python - <<'EOF'
          import importlib.metadata
          import sys

          import yaml

          with open(".pre-commit-config.yaml") as f:
              repos = yaml.safe_load(f)["repos"]
          hook = next(r for r in repos if r["repo"] == "https://github.com/astral-sh/ruff-pre-commit")
          locked = "v" + importlib.metadata.version("ruff")
          if hook["rev"] != locked:
              sys.exit(f"The ruff hook pins {hook['rev']} but uv.lock has {locked}. Bump both together.")
          EOF

      # Formatting first: a lint finding on unformatted code may vanish once it is formatted.
      - name: Check formatting
        run: uv run --no-sync ruff format --check

      - name: Lint
        run: uv run --no-sync ruff check
```

After: one job in `ci.yml`, which already runs on the same trigger. Secrets are given per job, so a `lint` job that is given no database secret runs for forks as it did before, and the header comment has nothing left to explain.

```yaml
  lint:
    name: Lint
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
        with:
          persist-credentials: false
      - uses: astral-sh/setup-uv@68559e99cc807c1eb7e9238fd43a15bba460eec2 # v10.3.3
      - name: Check formatting
        run: uv run --locked --only-group dev ruff format --check
      - name: Lint Python
        run: uv run --locked --only-group dev ruff check
```

The version check guarded a duplication: the pre-commit hook installed its own ruff, pinned by `rev`, while CI ran the one in `uv.lock`, and two ruff versions can disagree about the same file. With one pin there is nothing to compare, so the hooks run the locked ruff:

```yaml
# .pre-commit-config.yaml, before
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.17.5
    hooks:
      - id: ruff-format
      - id: ruff-check

# after
  - repo: local
    hooks:
      - id: ruff-format
        name: ruff format
        entry: uv run --only-group dev ruff format --force-exclude
        language: unsupported
        types_or: [python, pyi, jupyter]
        require_serial: true
      - id: ruff-check
        name: ruff check
        entry: uv run --only-group dev ruff check --force-exclude
        language: unsupported
        types_or: [python, pyi, jupyter]
        require_serial: true
```

`language: unsupported` is pre-commit 4.4.0's name for `system`; on an older pre-commit, write `system`. The other single source works as well: drop ruff from the dev dependencies, keep the remote hook, and have CI run `pre-commit run --all-files`. Either one removes the check; keeping both pins and the check does not.

What else moved:

- The job became `lint`, named `Lint`: named for its check, not its tool. A branch rule that required `ruff` now needs `Lint`; change the rule in the same change, or keep `ruff` as the name.
- `actions/setup-python` and its `3.12` went: uv installs the Python the project pins, and `3.12` was a second pin.
- `setup-uv@v4` declares Node 20, which runners stopped shipping on 2026-09-23, and setup-uv has published no major tags since v8.0.0, so the exact release is pinned. `version: "latest"` was the default.
- `uv sync` and every `--no-sync` went: `uv run --only-group dev` installs exactly that group. `--locked` replaced `--frozen`, so a stale `uv.lock` now fails instead of passing unnoticed.
- The comment on order went: the steps keep that order, formatting before lint, and the hooks' order in `.pre-commit-config.yaml` gives developers the same one.
- `runs-on` became a label instead of a one-item list.

## A release that checks the tag against the version

Before: a script compares the tag with `pyproject.toml`, interpolates the tag into the shell, and publishes with a long-lived token.

```yaml
      - name: Check the tag matches the version
        run: |
          VERSION=$(python -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])")
          if [ "v$VERSION" != "${{ github.ref_name }}" ]; then
            echo "::error::Tag ${{ github.ref_name }} does not match version $VERSION"
            exit 1
          fi
      - name: Build
        run: python -m build
      - name: Publish
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_TOKEN }}
        run: twine upload dist/*
```

After: the same rule in one line, without `${{ }}` in the script, and PyPI's trusted publishing instead of the token. The check is not a drift check: it enforces a release policy, that the version committed in `pyproject.toml` is the one published, so it stays.

```yaml
name: Release

on:
  push:
    tags: ["v*"]

permissions:
  contents: read

jobs:
  publish-pypi:
    name: Publish to PyPI
    runs-on: ubuntu-latest
    timeout-minutes: 10
    environment: pypi
    permissions:
      contents: read
      id-token: write
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
        with:
          persist-credentials: false
      - uses: astral-sh/setup-uv@68559e99cc807c1eb7e9238fd43a15bba460eec2 # v10.3.3
      - name: Check the tag matches the committed version
        run: test "v$(uv version --short)" = "$GITHUB_REF_NAME"
      - name: Build the package
        run: uv build
      - name: Publish to PyPI
        run: uv publish
```

`GITHUB_REF_NAME` is an environment variable the runner sets, so the tag never passes through `${{ }}` into the script, and `uv version --short` reads the version without creating an environment. `uv publish` uses trusted publishing on GitHub Actions once the PyPI project trusts this workflow and environment. setup-uv leaves its cache off for tag pushes, so a poisoned cache cannot reach the release.

Making the tag the only place the version is written, with `uv version --frozen "${GITHUB_REF_NAME#v}"` before `uv build`, would remove the comparison too, but it is a different release policy: a mismatched tag would publish whatever version it names instead of failing. Offer it as that choice and let the user make it; it is never a readability fix.

## A deployment whose logic belonged to its task

A service deployed to Kubernetes with Helm, whose tools and `deploy` task are defined in `mise.toml`. Before: a comment explains a default, and each deploy step scripts around the task it calls.

```yaml
# One deploy at a time, and never one cancelled halfway.
concurrency:
  group: deploy
  cancel-in-progress: false

jobs:
  staging:
    name: Staging
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - uses: actions/checkout@v7
      - uses: jdx/mise-action@v5
      - name: Deploy
        env:
          KUBECONFIG_CONTENT: ${{ secrets.KUBECONFIG }}
          HELM_VALUES: ${{ secrets.HELM_VALUES }}
        run: |
          printf '%s\n' "$KUBECONFIG_CONTENT" > "$RUNNER_TEMP/kubeconfig"
          export KUBECONFIG="$RUNNER_TEMP/kubeconfig"
          # Without HELM_VALUES, the release keeps the values already on the cluster.
          if [ -n "$HELM_VALUES" ]; then
            printf '%s\n' "$HELM_VALUES" > "$RUNNER_TEMP/values.yaml"
            export VALUES_FILE="$RUNNER_TEMP/values.yaml"
          fi
          mise run deploy staging
```

After: the deploy task reads `KUBECONFIG_CONTENT` and `HELM_VALUES` itself, so the same task works from a laptop and from CI, and the branch on `HELM_VALUES` lives once in code that can be read and run on its own, instead of in every deploy job.

```yaml
concurrency: deploy

jobs:
  deploy-staging:
    name: Deploy to staging
    runs-on: ubuntu-latest
    timeout-minutes: 15
    environment: staging
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
        with:
          persist-credentials: false
      - uses: jdx/mise-action@236a21c3b91f5db6d4e174b348674a0f0caac06d # v5.2.9
      - name: Deploy to staging
        env:
          KUBECONFIG_CONTENT: ${{ secrets.KUBECONFIG }}
          HELM_VALUES: ${{ secrets.HELM_VALUES }}
        run: mise run deploy staging
```

The move pays because the logic has a life outside this step: the production job and anyone deploying by hand need it too. Logic only this one step needs, moved into a script just to shorten the YAML, would not.
