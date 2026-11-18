# Workflows before and after

The SHAs below are the commits of the releases in their comments on 2026-10-23. Resolve current ones before copying: `gh api repos/<owner>/<repo>/commits/<tag> --jq .sha`.

## Contents

- A pull request workflow from scratch
- A check that grew a program
- A release that compared the tag with the version
- A deployment whose logic belonged to its task

## A pull request workflow from scratch

A uv project with ruff and pytest. `push` to `main` is there because setup-uv's cache, saved on `main`, is what pull requests restore. `UV_LOCKED` makes every `uv run` fail on a stale `uv.lock`, so the commands stay the ones developers type.

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

env:
  UV_LOCKED: 1

jobs:
  lint:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
        with:
          persist-credentials: false
      - uses: astral-sh/setup-uv@07a047e608db84b3d8c06cd9a7c7dcc9c355c18e # v10.3.2
      - name: Check formatting
        run: uv run ruff format --check
      - name: Lint Python
        run: uv run ruff check

  test:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
        with:
          persist-credentials: false
      - uses: astral-sh/setup-uv@07a047e608db84b3d8c06cd9a7c7dcc9c355c18e # v10.3.2
      - name: Run tests
        run: uv run pytest
```

No Python version appears: uv installs the one `.python-version` pins. No `uv sync` step: `uv run` installs what it runs.

## A check that grew a program

Before: seven steps, a Python program in a heredoc, and two comments explaining the YAML.

```yaml
---
name: SQL Format

# sqlfmt needs no Snowflake login, so this check runs apart from the
# pre-commit job in pr-checks.yml, which needs one for SQLFluff.
on:
  pull_request:
    branches:
      - main
      - develop

permissions:
  contents: read

jobs:
  sqlfmt:
    name: sqlfmt
    runs-on: ["atmos-aws-arc-runner-set"]
    timeout-minutes: 10

    steps:
      - name: Checkout code
        uses: actions/checkout@v7

      - name: Set up Python
        uses: actions/setup-python@v7
        with:
          python-version: '3.11'

      - name: Install uv
        uses: astral-sh/setup-uv@v4
        with:
          version: "latest"

      - name: Install the dev tools
        run: uv sync --frozen --only-group dev

      - name: Check that the sqlfmt hook pins the locked versions
        run: |
          uv run --no-sync python - <<'EOF'
          import importlib.metadata
          import sys

          import yaml

          with open(".pre-commit-config.yaml") as f:
              repos = yaml.safe_load(f)["repos"]
          hook = next(r for r in repos if r["repo"] == "https://github.com/tconbeer/sqlfmt")
          rev = "v" + importlib.metadata.version("shandy-sqlfmt")
          black = "black==" + importlib.metadata.version("black")
          if hook["rev"] != rev or black not in hook["hooks"][0].get("additional_dependencies", []):
              sys.exit(
                  f"The sqlfmt hook in .pre-commit-config.yaml must pin rev {rev} and {black}, as uv.lock does. "
                  "Bump both together, then run `make fmt` and commit the result."
              )
          EOF

      # Before sqlfmt: its diff would show a bare camelCase key lowercased, and
      # applying that diff makes the column NULL.
      - name: Check that semi-structured keys are quoted
        run: uv run --no-sync pre-commit run quote-json-keys --all-files

      - name: Check SQL formatting
        run: uv run --no-sync sqlfmt --diff --no-progressbar models tests snapshots analyses
```

After: one job in the pull request workflow, `pr-checks.yml`, which already runs on the same trigger. The job is given no Snowflake secret, so nothing needs a separate workflow, and the header comment has nothing left to explain.

```yaml
  check-format:
    runs-on: atmos-aws-arc-runner-set
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
        with:
          persist-credentials: false
      - uses: astral-sh/setup-uv@07a047e608db84b3d8c06cd9a7c7dcc9c355c18e # v10.3.2
      - name: Check semi-structured keys are quoted
        run: uv run --locked --only-group dev pre-commit run quote-json-keys --all-files
      - name: Check SQL formatting
        run: uv run --locked --only-group dev sqlfmt --diff models tests snapshots analyses
```

The version check guarded a duplication: the pre-commit hook installed its own sqlfmt and black, pinned in `.pre-commit-config.yaml`, while CI and `make fmt` ran the ones in `uv.lock`, and different versions format differently. With one pin there is nothing to compare, so the hook runs the locked tools:

```yaml
# .pre-commit-config.yaml, before
  - repo: https://github.com/tconbeer/sqlfmt
    rev: v0.32.0
    hooks:
      - id: sqlfmt
        additional_dependencies: ["shandy-sqlfmt[jinjafmt]", "black==26.10.1"]

# after
  - repo: local
    hooks:
      - id: sqlfmt
        name: sqlfmt
        entry: uv run --only-group dev sqlfmt
        language: unsupported
        types_or: [sql, jinja]
        require_serial: true
```

`language: unsupported` is pre-commit 4.4.0's name for `system`; on an older pre-commit, write `system`.

What else moved:

- `name: sqlfmt` went: the id is the check's name. If a branch rule required `sqlfmt`, change the rule in the same change.
- `actions/setup-python` and its `3.11` went: uv installs the Python the project pins, and `3.11` was a second pin.
- `setup-uv@v4` declares Node 20, which runners stopped shipping on 2026-09-23, and setup-uv has published no major tags since v8.0.0, so the exact release is pinned. `version: "latest"` was the default; pin uv itself with `required-version` in `pyproject.toml` if it matters.
- `uv sync` and every `--no-sync` went: `uv run --only-group dev` installs exactly that group. `--locked` replaced `--frozen`, so a stale `uv.lock` now fails instead of passing unnoticed.
- The comment on order went: the steps keep that order, correctness before style, and the hooks' order in `.pre-commit-config.yaml` gives developers the same one.
- `--no-progressbar` went: sqlfmt turns its bar off without a terminal.

## A release that compared the tag with the version

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

After: the tag is the only place the version is written, so there is nothing to compare, and PyPI's trusted publishing replaces the token.

```yaml
name: Release

on:
  push:
    tags: ["v*"]

permissions:
  contents: read

jobs:
  publish:
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
      - uses: astral-sh/setup-uv@07a047e608db84b3d8c06cd9a7c7dcc9c355c18e # v10.3.2
      - name: Set the version from the tag
        run: uv version --frozen "${GITHUB_REF_NAME#v}"
      - name: Build the package
        run: uv build
      - name: Publish to PyPI
        run: uv publish
```

`GITHUB_REF_NAME` is an environment variable the runner sets, so the tag never passes through `${{ }}` into the script. `uv publish` uses trusted publishing on GitHub Actions once the PyPI project trusts this workflow and environment. setup-uv leaves its cache off for tag pushes, so a poisoned cache cannot reach the release.

## A deployment whose logic belonged to its task

Before: comments explain a default, and the deploy step scripts around the task it calls.

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
          CUBE_ENV: ${{ secrets.CUBE_ENV }}
        run: |
          printf '%s\n' "$KUBECONFIG_CONTENT" > "$RUNNER_TEMP/kubeconfig"
          export KUBECONFIG="$RUNNER_TEMP/kubeconfig"
          # Without CUBE_ENV, the Secret is managed outside this repository.
          if [ -n "$CUBE_ENV" ]; then
            printf '%s\n' "$CUBE_ENV" > "$RUNNER_TEMP/cube.env"
            export CUBE_ENV_FILE="$RUNNER_TEMP/cube.env"
          fi
          mise run deploy staging
```

After: the deploy task reads `KUBECONFIG_CONTENT` and `CUBE_ENV` itself, so the same task works from a laptop and from CI, and its branch on `CUBE_ENV` lives in code that can be read and run on its own.

```yaml
concurrency: deploy

jobs:
  deploy-staging:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    environment: staging
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
        with:
          persist-credentials: false
      - uses: jdx/mise-action@8418fedb1110381a0d3ba51a7a415d7c1b884550 # v5.2.2
      - name: Deploy to staging
        env:
          KUBECONFIG_CONTENT: ${{ secrets.KUBECONFIG }}
          CUBE_ENV: ${{ secrets.CUBE_ENV }}
        run: mise run deploy staging
```
