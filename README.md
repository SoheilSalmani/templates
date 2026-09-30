# Templates

Weft templates, one directory each. `base` is the root every repository starts from; the stack templates (`java`, `fastapi`, `dbt`, `airflow`, `scala`, `slides`) extend it and add their own stack.

The templates need a `weft` built from source at the `WEFT_REF` of `.github/workflows/check.yml` or later. The 0.1.0 release ignores the `[refine]` tables and rejects the hooks' `before` field.

## Starting a project

`weft new` renders a template into a new directory, asking the template's questions on the way. Give it a directory of this checkout, or the repository on GitHub without cloning it:

```sh
weft new gh:SoheilSalmani/templates//slides my-talk
```

Each template's `AGENTS.md` lists its questions and patches. A deck from `slides` opens on a tour of what it can do: its `docs/how-to-write-a-talk.md` turns that into your talk, and its README is the reference for the syntax.

For a client's repository, answer no to the `commit_*` questions: the skills, MCP configuration, `mise.toml` and agent instructions are still rendered and kept current by `weft update`, but the committed `.gitignore` keeps them, `paseo.json` and `.weft/` out of git, and every new git worktree, Paseo's included, gets a copy from your main checkout.

## The base template

Every stack template declares `extends = "../base"`, so base's questions, patches and hooks are part of it under their own names and ids: one change to base reaches every template and, through `weft update`, every scaffolded project. Change shared scaffolding in `base` only; `weft patch amend` refuses an inherited patch in a stack.

All the Agent Skills live in base. The ones for one stack are behind the `stack_skills` question: `dbt-skills` behind `dbt`, `writing-slides` behind `slides`. A stack narrows base's questions with `[refine.<id>]` tables in its `weft.toml`: dbt offers and selects its skills, slides fixes its own (its features extend `writing-slides`), and the other stacks offer none. The same tables reword a question for the stack, such as `project_name`'s description.

A stack's first patch, named after the template, builds on base's root: it adds the stack's ignores to the top of base's `.gitignore`, replaces base's README where the stack has its own, and orders its setup hooks `before` base's `git-commit`, so the first commit includes what they produce.

```sh
scripts/sync-skills.sh ~/path/to/skills   # re-record base's skills patches from a checkout of SoheilSalmani/skills, then check every template
scripts/check-templates.sh                # weft check every template under base's answer combinations, then prove the commit_* answers on a real render
```

CI (`.github/workflows/check.yml`) runs `check-templates.sh`, with `weft` built from source at the release or commit its `WEFT_REF` names.
