# The weft command sheet

Copied from `weft <command> --help` on `weft 0.1.0`, 2026-09-25, with the slot, `weft commit` and `weft patch resync` changes of a weft built from source on 2026-09-29 (`weft patch resync --yes` does not exist on 0.1.0). The docs under `docs/content/docs/weft/reference/cli.mdx` lag the binary in places (they omit `--title`, spell the tag flag `--tags a,b`, and still mention `weft record`), so when this sheet and the binary disagree, run `--help` and believe the binary. `weft --version` first: a newer binary may have moved flags, and a build from source still reports `0.1.0`.

## Contents

- Template
- Sessions
- Staging and committing
- Patches after the fact
- Hooks
- Presets
- Validation and description
- Consuming a template
- Composition and hub
- Errors you will meet

## Template

```text
weft init [DIR] [--name NAME]          # weft.toml + empty patches/ + a default .weftignore (node_modules/)
```

The generated `weft.toml` carries `description = "TODO: what this template scaffolds."`. Replace it; `weft describe` and the studio show it first.

## Sessions

```text
weft session new NAME [--template DIR] [--base latest|PATCH] [--preset P]... [--answer K=V]...
                      [--answers-file F] [--path DIR] [--foreach INCLUDE=KEY] [--exec [CMD]]
                      [--force] [--non-interactive] [--no-wizard]
weft session adopt PATH -n NAME [--template DIR] [--base REF] [--preset P]... [--answer K=V]...
                      [--answers-file F] [--scope GLOB]... [--force] [--non-interactive]
weft session list | ls
weft session path [NAME]
weft session move NAME DEST
weft session scope [--add GLOB]... [--rm GLOB]
weft session refresh [--answer K=V]... [--preset P]... [--answers-file F] [--answers-json J]
weft session end [NAME] [--discard]
```

- `--base latest` (default) stacks on everything active. `--base PATCH` renders that patch and its ancestors only, so the new patch is independent of everything later.
- `--exec CMD` runs the command in the rendered worktree; its output is the patch and the command is stored so `weft patch resync` can re-run it. `${answer}` and `${expr}` interpolate declared answers. Pass `--exec` with no value to write the command in `$EDITOR`. What the command prints to stdout comes out before the worktree path (verified 2026-09-28 with the shadcn CLI), so `cd $(…)` breaks; `cd` into `.weft-sessions/NAME/worktree` instead.
- `adopt` on a directory `weft new` made needs no arguments beyond `-n`; it reads `.weft/state.toml`. On any other directory pass `--template`, the answers, and `--scope`, or every file reads as new.
- `end` refuses a worktree with uncommitted changes unless `--discard`. A worktree weft created is deleted; an adopted one is only unlinked.
- Inside a worktree no `--template` or `--session` is needed: weft walks up to `.weft/worktree.toml`. From the template root, `-s NAME` when more than one session exists.

## Staging and committing

```text
weft add [PATTERNS]... [-A|--all] [-p|--patch]
weft reset [PATTERNS]...                                   # no --patch variant exists
weft status
weft diff [--abstracted] [--json] [--staged|--cached]
weft commit --name NAME [--title TEXT] [--describe TEXT] [--tag T]... [--when EXPR]
            [--yes] [--keep-literal ANSWER@PATH:LINE[:NTH]]... [--stack|--sibling]
            [--depends-on A,B | --after NAME] [--no-tui]
```

- Paths and globs are relative to where you stand. `weft add .` stages the subtree, `-A` the whole worktree.
- `-p` prompts `y n a d s q ?` per hunk; `s` splits a hunk that has internal context. A new file is one hunk and cannot be split, so trim a new file in the worktree before staging it.
- `commit` takes the staged set, or the whole worktree when nothing is staged. `--name` is the file stem; without it and without a TTY the patch is auto-named `patch-NNN`.
- `--tag` is repeatable on `commit`; `--tags a,b` in the docs is wrong.
- `--yes` accepts every abstraction candidate. `--keep-literal` keeps one occurrence literal and implies `--yes` for the rest; the keys come from `weft diff --json` (`occurrences[].id/path/line/nth`).
- `--depends-on` names must be in the session's base, and the patch must still apply with only their closure present. `--after NAME` is sugar for one parent. A slot filler passes `--depends-on <owner>`.
- Commit context never comes from lines an `expr` rendered or from slot content; a change with only such lines around it is refused unless it appends at the end of the file.
- Lines added inside a slot are recorded as a `fill_slot` keyed by the patch name, and `weft diff` prints ``note: line 3 fill slot `servers` under key `lightdash` `` under the file, using the session's name as the key. The block must sit where its key sorts, with the separator ending every contribution but the last; commit refuses it otherwise and prints the layout it expects.
- In a `weft patch amend` session, `--title`, `--describe` and `--tag` apply as `weft patch set` would, in the same save as the ops. `--when`, `--depends-on`/`--after` and a `--name` other than the patch's are refused before anything is written; edit those in the JSON.
- `commit` ends the session, and a worktree weft created is deleted with it, so nothing later in the same shell command can run in it.

## Patches after the fact

```text
weft patch ls [--template DIR]
weft patch set NAME [--title TEXT] [--describe TEXT] [--tag T]... [--clear-tags] [--no-tui]
weft patch amend NAME [--answer K=V]... [--preset P]... [--answers-file F] [--force]
weft patch squash NAME NAME... --into NAME [--title TEXT]
weft patch resync [NAMES]... [--all] [--answer K=V]... [--keep-literal SPEC]... [--dry-run] [--yes] [--json]
weft patch set-command NAME [COMMAND] [--resync]
weft patch detach NAME
```

- `set` never changes an id. An empty string clears a field.
- `amend` opens a session named after the patch (one per patch at a time) and prints its worktree path; `weft commit --yes` inside it rewrites the patch in place. The id changes and dependents replay. A dependent whose anchors no longer match is not named, the amend is written anyway, and `weft patch amend` on that dependent then fails to render (verified 2026-09-29). So before an amend that touches lines a dependent anchors on, move the dependent's JSON out and keep its title, description, `depends_on` and `when`; after the amend, re-record it in `weft session new NAME` with `weft commit --name NAME --depends-on … --when … --title … --describe …`. A slot filler keeps its key.
- `squash` members must be convex in the graph, share a gate, and be neither generator nor foreach patches.
- `resync` refuses while any session is open. `amend` refuses a generator patch until `detach`. Both refuse a patch that declares a slot (`resync` skips it with an issue): edit its JSON, then `weft check`.
- `resync --answer` is stored in the generator metadata even when the output is up to date (``note: `base`: stored the --answer override(s) in its generator metadata (ops unchanged)``). `--keep-literal` re-derives the ops even when the output is unchanged, so it repairs an occurrence an earlier resync abstracted (`gen: rewritten (1 op(s))`); when the ops come out the same it only stores the specs. Questions added since recording take their defaults, as on `weft update`. When the regenerated ops reference an answer the previous version did not, the patch is skipped with the occurrence keys (`docs_url@README.md:1:1`) until `--yes` accepts them or `--keep-literal` keeps them literal.
- Rename: `mv patches/old.json patches/new.json`, then edit every `"old"` in `depends_on` arrays. Delete: `rm`. Both followed by `weft check`.

## Hooks

```text
weft hook add PATCH --id ID --phase pre|post --effect check|setup|deploy --label TEXT --action CMD
              [--description TEXT] [--when EXPR] [--after HOOK_ID]... [--input glob:P|answer:ID|hook:ID]... [--no-tui]
weft hook rm PATCH ID
weft hook ls                                               # every hook, in execution order
```

`--input` is post-only. Bad `--after` or `--input` references are rejected and the patch file is rolled back. Pass `--no-tui` in scripts, or a missing flag opens a form.

## Presets

```text
weft presets list
weft presets show NAME
weft presets save NAME [TEMPLATE] [--answer K=V]... [--fix K=CHOICE]... [--block K=CHOICE]... [--non-interactive]
weft presets rm NAME
```

`save` writes `presets/NAME.toml` and appends a `[[preset]]` entry to `weft.toml`. A preset locks what it answers; secrets cannot be preset.

## Validation and description

```text
weft check [TEMPLATE] [--answer K=V]... [--preset P]... [--answers-file F] [--json] [--frozen]
weft graph [TEMPLATE] [--answer K=V]... [--preset P]... [--json] [--diff PATCH]
weft describe [TEMPLATE] [--json | --agents-md [PATH]]
weft schema [--out DIR]                                    # weft-patch.schema.json, weft-manifest.schema.json
```

- `check` without answers validates the manifest, expressions, graph and slot declarations only, unless every question has a default, in which case it renders under the defaults. With answers it renders every patch on top of its own dependencies, then the whole graph, then every independent pair for commutation, under those answers. A patch that fails on its own dependencies is reported once (``patch `mine` does not apply under these answers: …``) and left out of the rest. Pairs whose only shared files both merely fill are counted, not rendered: `commutation ok for 2 independent pair(s); 1 more only fill the same slots, which commutes by construction`. `--json` returns `{ok, issues, notes}`.
- `describe --json` returns `template`, `questions`, `presets`, `patches` (with `title`, `description`, `when`, `depends_on`, op summaries), `hooks` in execution order, `includes`, `usage`. Its `usage.author` lines still say `weft record`; ignore them.
- `describe --agents-md` writes `<template>/AGENTS.md`; `-` writes to stdout.

## Consuming a template

```text
weft new [TEMPLATE] [DEST] [--preset P]... [--answer K=V]... [--answers-file F] [--answers-json J|@file|-]
         [--instance INCLUDE=KEY]... [--skip-tasks] [--non-interactive] [--frozen]
weft update [DEST] [--dry-run] [--template DIR] [--skip-tasks] [--non-interactive] [--frozen]
weft instance add INCLUDE KEY [--answer ID=V]... | list | remove INCLUDE KEY
```

`DEST` must be empty or absent; two templates cannot be scaffolded into one directory. `--skip-tasks` renders without running hooks.

`update` merges each file three ways: the template's last render, the project's copy and the new render. A file the project deleted stays deleted when the new render changes it (`chapters/tour.mdx: kept it deleted: you deleted it, and the new render changes it`). A file the project rewrote, such as starter content replaced by the user's own, takes every template change to it as a conflict, and the post hooks wait until it is resolved. So starter content a user is meant to replace goes in files of its own, which they delete, never in the file they write in (verified 2026-09-30 on `slides`).

## Composition and hub

```text
weft lock [TEMPLATE] [--upgrade] [--registry URL]
weft hub publish OWNER/NAME --version X.Y.Z [--template DIR] [--registry URL] [--token T]
weft hub search TEXT | info OWNER/NAME
```

## Errors you will meet

| Message | Cause | Do |
| --- | --- | --- |
| `this patch is gated off under the session answers, so the session cannot continue on top of it` | `--when` false under the session's answers, with changes left | record with answers that make the gate true, or give the patch its own session |
| `this patch does not apply with only `a` in the base` | `--depends-on` too narrow | declare the patch it anchors on too |
| `replaying the recorded patch does not reproduce the worktree` | ambiguous hunk context | add a distinguishing line, or commit the file whole |
| `a dependent patch no longer applies after the amend` | the amend changed lines a dependent's hunks anchor on; the amend is already written | restore the patch file from git, set the dependent aside, amend again, then re-record the dependent under its old name |
| `--sibling` on an adopted session (refused with an error) | adopted worktrees always stack | use `--depends-on base` on later commits to keep them independent |
| `destination … is not empty` | `weft new` into a used directory | pick an empty directory; adopt the existing one instead |
| `base state hash changed since the session started` / `pinned base patch … no longer exists` | the template moved under an open session | copy the worktree files out, `weft session end NAME --discard`, start again |
| ``the change at line 2 sits between lines that read differently under other answers or with other patches active (`expr` segment …)`` | the only lines around the change were rendered by an `expr` or are slot content | make the change next to a literal line, or turn the list into a slot |
| ``with this patch's lines under key `lightdash`, slot `servers` renders as: …`` | the new block in a slot is out of key order, or a separator is missing or extra | move the block where its key sorts; every contribution but the last ends with the separator |
| ``the worktree changed slot `servers` in a way no single contribution explains`` | two blocks in one slot, or an edit to another patch's contribution | one block per patch; change another patch's lines by amending that patch |
| ``patches `linear` and `twin` both fill slot `servers` of `.mcp.json` under key `linear` `` | two fills with one key in one slot | rename one key in its JSON |
| ``patch `mcp` declares slot(s) `servers` in `.mcp.json`, which a recording cannot reproduce`` | `weft patch amend` on a slot owner | edit `patches/mcp.json` by hand, then `weft check` |
| `` `.mcp.json` does not exist on top of its dependencies; depend on the patch that creates it`` | a filler without `depends_on` on the owner | add the owner to `depends_on` |
