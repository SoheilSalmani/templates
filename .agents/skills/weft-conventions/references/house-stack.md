# The house stack

What the house has already decided, read from the templates that exist. Surveyed 2026-09-25 across `~/Desktop/Projects/templates/{base,java,scala,dbt,fastapi,airflow}` and `~/Desktop/Projects/trendlift/weft-templates/web`. **Look at the templates directory before trusting this file**: a newer template outranks it, and the survey is the reading, not the rule. The rule is in `SKILL.md`: a tool is a decision the template makes; a question is for what varies between projects.

## Contents

- Every repository: the `base` template
- Per language
- Pinned, not asked
- Not yet decided
- Defects in the existing templates

## Every repository: the `base` template

`base` is the root every repository starts from and the donor of the portable patches every stack template carries (see `patch-format.md`). Its patches, and the decision each one embodies:

| Patch | Decided | Gate |
| --- | --- | --- |
| `editorconfig` | UTF-8, LF, final newline, four spaces; two for YAML, JSON, TOML; trailing whitespace kept in Markdown | |
| `gitattributes` | `* text=auto eol=lf`; a stack adds its own rules as a hunk (java: `*.bat` CRLF, `*.jar` binary) | |
| `mise` | `mise.toml` pins `node = "24"` for skill scripts and MCP servers; a stack pins its runtime with a `mise-<tool>` patch that hunks `[tools]` (`mise-java` → `java = "25"`, `mise-uv` → `uv = "0.12"`, `mise-astro`); `mise.local.toml` is the gitignored personal layer; hooks `verify-mise` and `mise-install` (`mise trust -q && mise install -y`, `glob:mise.toml`) | |
| `instructions` | `AGENTS.md` is the one instruction file; `CLAUDE.md` is `@AGENTS.md`. Codex and oh-my-pi read `AGENTS.md` and `.agents/skills` natively | |
| `skills` | the 14 house Agent Skills under `.agents/skills/`, canonical; `.claude/skills/` is a symlink farm rebuilt (and pruned) by the post hook `sync-claude-skills` with `glob:.agents/skills/**` | |
| `github` | 8 GitHub skills; they drive `gh`, no GitHub MCP server | `use_github` (True) |
| `linear`, `jira` | the tracker's skills | `use_linear` (True), `use_jira` (False) |
| `anki`, `obsidian` | personal skills; their MCP servers are per machine and stay in user-level config | `use_anki`, `use_obsidian` (False) |
| `mcp` | remote MCP servers as definition-only entries, identical in `.mcp.json` (Claude Code), `.codex/config.toml` (Codex, trusted projects) and `.omp/mcp.json` (oh-my-pi); `linear-server` at `https://mcp.linear.app/mcp`, `atlassian` at `https://mcp.atlassian.com/v2/mcp`; OAuth per user, nothing stored. The entries are hand-written `expr` lines on the two bools because one file cannot be shared by two sibling patches | `use_linear or use_jira` |
| `base` (not portable) | `README.md` with the `mise install` recipe and the `.gitignore` stanzas (OS, editors, `.env*`, `mise.local.toml`, `.claude/settings.local.json`); hooks `git-init` and `git-commit --after` every setup hook | |

Two rules follow from it:

- The trackers are **bools, not a choice**: choice values are abstracted wherever they appear and `linear` is all over the skill prose (`questions.md`).
- The portable copies are kept identical by `scripts/sync-portable.sh` and `scripts/check-portable-drift.sh` in the templates repository; CI runs the drift check and `weft check` on every template. Edit the donor in `base`, never a copy.

## Per language

| Stack | Decided | Asked with `use_*` | Evidence |
| --- | --- | --- | --- |
| Python | uv pinned by mise (`mise-uv`), Python pinned by `.python-version` (uv reads it natively), `pyproject.toml`; hooks `verify-uv`, `uv-sync` (`uv lock && uv sync`, `glob:pyproject.toml`) | Docker | `fastapi`, `dbt`, `web` (apps/api) |
| Node | pnpm (`packageManager` pinned), Turborepo, Prettier | shadcn/ui, Prisma, Better Auth, Resend, Fumadocs, Mastra, PostHog, Stripe, Typesense, Cloudinary | `web` |
| Java | JDK 25 by mise (`mise-java`), Gradle with the Kotlin DSL and a committed wrapper, Spotless + palantir-java-format, Error Prone, JUnit + AssertJ | Spring Boot, Testcontainers, GitHub Actions, Renovate | `java` |
| Scala | JDK 25 by mise (`mise-java`), scala-cli entry point, scalafmt with a pinned version, `verify-scala` and `verify-scalafmt` pre checks | sbt, ZIO | `scala` |
| dbt | uv-managed Python, snake_case `package_name` feeding both `dbt_project.yml` and `pyproject.toml`, `profile_name` defaulting to it, `.vscode/extensions.json` recommending the dbt extension, a `dbt-skills` patch with the four dbt skills; hooks `uv-sync`, `dbt-deps` (`uv run dbt deps`, `glob:packages.yml`) | | `dbt` |
| Airflow | Astro CLI project, Astro CLI pinned by mise (`mise-astro`), `verify-astro` | | `airflow` |

## Pinned, not asked

- Language and tool versions: `node`, `java`, `uv`, `astro` in `mise.toml`; `.python-version`; `packageManager`; the Gradle wrapper version; `scalafmt`; Spring Boot. Bump with `weft patch amend`; `weft update` moves every project. `java_version` was dropped from `java` on 2026-09-25. `scala` still asks `scala_version`, a 2.13-versus-3 axis rather than a plain version; do not add version questions elsewhere.
- Lockfiles: never in a patch. `uv.lock`, `pnpm-lock.yaml`, `gradle.lockfile` are produced by a `setup` hook with `inputs` on the manifest. List them in `.weftignore`.
- Formatter and linter configuration: shipped, not offered.
- Editor and git configuration, AGENTS.md, the skills, the MCP file set: shipped by the portable patches, never asked.

## Not yet decided

No template ships a LICENSE, pre-commit, ruff or mypy configuration, a justfile or Makefile, a devcontainer, or Renovate outside `java`. When a new template needs one of these, decide once, write it into the patch, and add the decision here. Do not turn the absence of a decision into a question.

## Defects in the existing templates

Steer away from these; they are not conventions:

- `java` is a six-deep chain (`base → gradle → gradle-wrapper → testing → formatter → linter`) because every patch was recorded on `latest`; only the `build.gradle.kts` edits needed the order.
- `scala`'s `zio` patch adds `MainApp.scala` without the `dev.zio` library dependency in `build.sbt`, so `sbt compile` fails under `use_zio=true`; the fix is one `weft patch amend zio` adding the hunk with a pinned ZIO version.
- `weft hook ls` prints `git-commit` before the setup hooks it lists in `--after`; `weft describe --json` and the actual run honour the order. Display only.
- `web-template` and `python-service` do not match their directory names.
