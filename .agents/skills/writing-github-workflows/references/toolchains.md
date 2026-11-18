# Toolchains in GitHub workflows

Releases checked 2026-10-23. Before pinning, check for a newer one with `gh api repos/<owner>/<repo>/releases/latest --jq .tag_name`, then find the commit it points at with `gh api repos/<owner>/<repo>/commits/<tag> --jq .sha`.

## Contents

- Choosing the setup step
- Python with uv
- Node with pnpm
- Java with Gradle
- mise
- Caches
- Releases on 2026-10-23

## Choosing the setup step

1. **The repository pins its tools in `mise.toml`**: one `jdx/mise-action` step installs all of them, and `mise run <task>` is the entry point when the project has tasks. Don't add a language's setup action beside it.
2. **Otherwise one setup action per language**, reading the project's own version file, never a version typed into the workflow.
3. **No setup step for a tool another step provides** (Python under uv, Node under `pnpm/setup`), and no action for something the runner already has: zizmor's `superfluous-actions` audit flags such actions, `softprops/action-gh-release` where `gh release create` does the job.

## Python with uv

```yaml
      - uses: astral-sh/setup-uv@07a047e608db84b3d8c06cd9a7c7dcc9c355c18e # v10.3.2
      - name: Run tests
        run: uv run pytest
```

- uv installs the Python that `.python-version` or `requires-python` pins. `actions/setup-python` beside it saves about a second on GitHub-hosted runners and adds a second pin.
- setup-uv installs the uv version that `required-version` in `pyproject.toml` or `uv.toml` asks for, else the newest; `version: latest` changes nothing. It has published no major tags since v8.0.0, so pin the exact release.
- `UV_LOCKED: 1` in the workflow's `env` makes every `uv run` fail on a stale `uv.lock`, which keeps each command the one developers type; `--locked` does the same for one command. `--frozen` skips the check and hides a forgotten `uv lock`.
- `uv run --only-group <group>` installs that dependency group without the project, for a job that needs the dev tools only.
- Don't set `activate-environment`; setup-uv's documentation recommends `uv run` instead.
- setup-uv's cache is on by default on GitHub-hosted runners, and off on self-hosted runners and for tag pushes, releases, `pull_request_target` and `workflow_run`.

## Node with pnpm

With pnpm 11 or later, `pnpm/setup` is the whole setup: it installs the pnpm that `packageManager` names, the runtime that `devEngines.runtime` or `.nvmrc` names, and then runs `pnpm install`.

```yaml
      - uses: pnpm/setup@a0881977cd8ea73b1ed212236c99ca10dcc80cf4 # v3.1.1
        with:
          cache: true
          require-lockfile: true
      - name: Run tests
        run: pnpm test
```

With pnpm 10 or earlier, `pnpm/action-setup` (which reads `packageManager`) comes before `actions/setup-node` with `node-version-file` and `cache: pnpm`, then a `pnpm install --frozen-lockfile` step.

## Java with Gradle

```yaml
      - uses: actions/setup-java@b843ebf9b913146b38da2eaa7aeddf76074ae1ad # v6.1.0
        with:
          distribution: temurin
          java-version-file: .java-version
      - uses: gradle/actions/setup-gradle@3f5f9adaf7d9fecd50b5935e54106014257a94e6 # v6.4.0
      - name: Build
        run: ./gradlew build
```

`setup-gradle` caches Gradle's state, so the job needs no `actions/cache`. When `mise.toml` pins the JDK, `jdx/mise-action` replaces `setup-java`.

## mise

```yaml
      - uses: jdx/mise-action@8418fedb1110381a0d3ba51a7a415d7c1b884550 # v5.2.2
      - name: Run tests
        run: mise run test
```

- It installs every tool `mise.toml` pins, `--locked` against `mise.lock` when there is one, and caches them by default. `install_args: node` limits a job to the tools it needs.
- mise can pin uv and Python as well, so a uv project whose tools live in `mise.toml` needs no setup-uv.
- A release job sets `cache: false`, because mise trusts a restored tool cache as it is.

## Caches

- Use the setup action's own cache: setup-uv's `enable-cache`, `pnpm/setup`'s `cache`, setup-node's `cache`, setup-java's `cache` or `setup-gradle`, mise-action's `cache`.
- Write an `actions/cache` step only for what no setup action caches, keyed on the lockfile: `key: <tool>-${{ runner.os }}-${{ hashFiles('<lockfile>') }}`.
- Release and publish jobs restore no cache, because a cache saved by one run is restored by others: `cache-mode: none` on the job, or the setup action's cache turned off.

## Releases on 2026-10-23

| Action | Release | Commit |
| --- | --- | --- |
| `actions/checkout` | v7.0.1 | `3d3c42e5aac5ba805825da76410c181273ba90b1` |
| `actions/setup-python` | v7.1.0 | `6d4fd22b20465ccc0f7354476588e8df7c9ca0e0` |
| `actions/setup-node` | v7.1.0 | `949feb2413d6458794dcd2491c4babbbce0c15c1` |
| `actions/setup-java` | v6.1.0 | `b843ebf9b913146b38da2eaa7aeddf76074ae1ad` |
| `actions/cache` | v6.1.0 | `55cc8345863c7cc4c66a329aec7e433d2d1c52a9` |
| `actions/upload-artifact` | v7.0.2 | `cf430e030ddbb5b0abf93d22962f4752f3646cd9` |
| `astral-sh/setup-uv` | v10.3.2 | `07a047e608db84b3d8c06cd9a7c7dcc9c355c18e` |
| `jdx/mise-action` | v5.2.2 | `8418fedb1110381a0d3ba51a7a415d7c1b884550` |
| `pnpm/setup` | v3.1.1 | `a0881977cd8ea73b1ed212236c99ca10dcc80cf4` |
| `pnpm/action-setup` | v6.1.0 | `ea17c68df8912ef543352723c149a84f56e3d413` |
| `gradle/actions` | v6.4.0 | `3f5f9adaf7d9fecd50b5935e54106014257a94e6` |
