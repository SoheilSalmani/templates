# Templates

Weft templates, one directory each. `base` is the root every repository starts from; the stack templates (`java`, `fastapi`, `dbt`, `airflow`, `scala`, `slides`) carry copies of its portable patches plus their own stack.

## Starting a project

`weft new` renders a template into a new directory, asking the template's questions on the way. Give it a directory of this checkout, or the repository on GitHub without cloning it:

```sh
weft new gh:SoheilSalmani/templates//slides my-talk
```

Each template's `AGENTS.md` lists its questions and patches. A deck from `slides` opens on a tour of what it can do: its `docs/how-to-write-a-talk.md` turns that into your talk, and its README is the reference for the syntax.

## The portable set

Every patch in `base/patches` except `base.json` is a portable patch: a root with `create_file` ops only, copied byte-for-byte into every other template. Identical bytes mean an identical patch id everywhere, so `weft update` moves every scaffolded project together. Edit the donor copy in `base` only, then re-copy:

```sh
scripts/sync-portable.sh                 # copy base's portable patches into every template, then weft check all
scripts/sync-portable.sh ~/path/to/skills   # first re-record the skills patches from a checkout of SoheilSalmani/skills
scripts/check-portable-drift.sh          # fail if any template's copy differs from base
scripts/check-templates.sh               # weft check every template under the shared answer combinations
```

CI (`.github/workflows/check.yml`) runs the last two, with `weft` built from source at the release its `WEFT_REF` names.
