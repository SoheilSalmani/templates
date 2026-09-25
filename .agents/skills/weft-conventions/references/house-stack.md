# The house stack

What the house has already decided, read from the templates that exist. Surveyed 2026-09-25 across `~/Desktop/Projects/templates/{skills,java,scala,dbt,fastapi,airflow}` and `~/Desktop/Projects/trendlift/weft-templates/web`. **Look at the templates directory before trusting this file**: a newer template outranks it, and the survey is the reading, not the rule. The rule is in `SKILL.md`: a tool is a decision the template makes; a question is for what varies between projects.

## Contents

- Per language
- Shared scaffolding
- Pinned, not asked
- Not yet decided
- Defects in the existing templates

## Per language

| Stack | Decided | Asked with `use_*` | Evidence |
| --- | --- | --- | --- |
| Python | uv, `.python-version` pinned, `pyproject.toml` | Docker | `fastapi`, `dbt`, `airflow`, `web` (apps/api), every docs tutorial |
| Node | pnpm (`packageManager` pinned), Turborepo, Prettier | shadcn/ui, Prisma, Better Auth, Resend, Fumadocs, Mastra, PostHog, Stripe, Typesense, Cloudinary | `web` |
| Java | Gradle with the Kotlin DSL and a committed wrapper, Spotless + palantir-java-format, Error Prone, JUnit + AssertJ | Spring Boot, Testcontainers, GitHub Actions, Renovate | `java` |
| Scala | scala-cli entry point, scalafmt with a pinned version, `verify-scala` and `verify-scalafmt` pre checks | sbt, ZIO | `scala` |
| dbt | uv-managed Python, `mise.toml` for `[env]` with `mise.local.toml` gitignored, `.vscode/extensions.json` recommending the dbt extension | Snowflake connection | `dbt` |
| Airflow | Astro CLI project (`astro dev init` recorded) | | `airflow` |
| Agent skills | `.agents/skills/` canonical, `.claude/skills/` symlink farm rebuilt by a post hook `sync-claude-skills` with `glob:.agents/skills/**` inputs | one `use_<tool>` per external tool (GitHub, Jira, Linear, Anki, Obsidian) | `skills` |

## Shared scaffolding

Root-level things that every template wants and that travel best as portable patches (see `patch-format.md`): the agent skills patch, `.editorconfig` (only `java` has one today), `.gitignore` stanzas in the `# <What> (<Tool>)` style the older templates use, a CI workflow under `.github/workflows/`, Renovate config. `git init` plus an initial commit as post hooks with no `inputs` (`web` does this: `git-init`, then `pnpm-install`, `format`, `git-commit` chained with `--after`).

## Pinned, not asked

- Language and tool versions: `requires-python`, `.python-version`, `packageManager`, the Gradle wrapper version, `scalafmt` version, Spring Boot version. Bump with `weft patch amend`; `weft update` moves every project. The existing `java` and `scala` templates still ask `java_version` and `scala_version`; do not copy that into new templates.
- Lockfiles: never in a patch. `uv.lock`, `pnpm-lock.yaml`, `gradle.lockfile` are produced by a `setup` hook with `inputs` on the manifest (`uv lock && uv sync` with `glob:pyproject.toml`; `pnpm install` with `glob:**/package.json`). List them in `.weftignore`.
- Formatter and linter configuration: shipped, not offered.

## Not yet decided

No template ships a LICENSE, pre-commit, ruff or mypy configuration, a justfile or Makefile, or a devcontainer. When a new template needs one of these, decide once, write it into the patch, and add the decision here. Do not turn the absence of a decision into a question.

## Defects in the existing templates

Steer away from these; they are not conventions:

- `fastapi` and `airflow` recorded their generator without a name, so `name = "worktree"` is in the patch and `project_name` is never used.
- `scala`, `dbt`, `cube` and `pysvc` still carry `description = "TODO: what this template scaffolds."`.
- `skills/base.json` ships six `__pycache__/*.pyc` blobs; its `.weftignore` only lists `node_modules/`.
- `uv.lock` is committed in `fastapi` and ignored in `dbt` and `airflow`; `.python-version` is 3.13 in two templates and 3.12 in a third.
- `java` is a six-deep chain (`base → gradle → gradle-wrapper → testing → formatter → linter`) because every patch was recorded on `latest`; only the `build.gradle.kts` edits needed the order.
- `web-template` and `python-service` do not match their directory names.
