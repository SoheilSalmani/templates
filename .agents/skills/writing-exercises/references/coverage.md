# What is already covered

Read this before writing a set, and before adding to one. A concept the learner already holds, on a card or in an exercise they did, gets no new exercise.

## Contents

- The Anki collection
- Existing exercise sets
- Deciding
- Reporting

## The Anki collection

Reach the collection through the anki MCP server when the session has it: `findNotes` with an Anki search, then `notesInfo` on the ids. Without the server, AnkiConnect answers the same actions on `localhost:8765`. Both read; neither writes:

```bash
curl -s localhost:8765 -d '{"action": "findNotes", "version": 6, "params": {"query": "\"Tool:Rust\" macro"}}'
curl -s localhost:8765 -d '{"action": "notesInfo", "version": 6, "params": {"notes": [1712345678901]}}'
```

With neither reachable, say that the collection was not checked, and carry on.

Search each subject twice:

- **By its context field**, to see everything carded about it: `"Tool:Rust"` matches the field exactly, case aside, and `"Topic:Rust*"` matches topics that start with the name. Collections name these fields differently; `notesInfo` on one match shows the field names.
- **By each concept's own words within the subject**: `"Tool:Rust" lifetime`, `"Tool:Rust" trait`.

Read the fronts that match. A count says nothing about which facts are carded.

A concept is covered by cards when its facts are: what it is, its rules, its syntax, its defaults. Cards never cover the doing. A card that recalls how to write a doc comment is enough for doc comments; a card that defines a trait object does not show that the learner can design one.

Some collections also schedule exercise reviews, with a note type that holds a set and a range of its items, such as `Repository` and `Range` fields. Search it for the set's name, as in `"Repository:rust-activities"`, to see which items already come back on Anki's schedule. A note that points at an outside practice activity, such as an interactive game for the subject, counts as an existing exercise.

## Existing exercise sets

The learner's sets live in two places. The current ones are folders of one activities repository, each with its `README.md` on `master` and a branch of answers named after the folder. Older ones are repositories named `*-activities`, usually side by side in one folder. Search the READMEs of both for the concept's words, in the subject's own set and in sets for neighbouring tools:

```bash
git -C activities grep -n -i -E 'lifetime|borrow' master -- '*/README.md'
grep -n -i -E 'lifetime|borrow' */README.md
```

An item whose number has an `Exercise N` commit was done, on the activity's branch or in the older repository:

```bash
git -C activities log --oneline --grep='^Exercise 7$' rust --
git -C rust-activities log --oneline --grep='^Exercise 7$'
```

An item without one is still waiting for the learner. Read the item before counting it: a `TODO` or a one-word note covers nothing.

## Deciding

| The concept is | and | then |
| --- | --- | --- |
| theory: a definition, a rule, a default, a name, a syntax form, a trade-off stated in a sentence | carded | skip it |
| theory | not carded | flashcards: list it for `anki-flashcards`, which drafts the cards and asks before adding them |
| practice: writing code with it, operating the tool, finding a bug, choosing under real constraints | practised by an exercise the learner did | skip it, or bring it back unannounced inside a later task |
| practice | written up but not done | point the learner at that item instead of writing it again |
| practice | not practised anywhere | write an exercise |
| not needed by the target, or barely used by the codebase | | skip it |

When a concept is both, split it: its facts go on cards, and the doing gets an exercise only if a real task needs it.

## Reporting

The reply says, for every concept considered, which way it went and why, in one line each: "exercise 4", "skipped: 12 cards under `Tool:Rust`", "flashcards: not carded", "skipped: `rust-activities` item 7, done". It names any store that could not be checked. After writing the set, where the learner schedules exercise reviews in Anki, it proposes one review note for each part of the set, and adds them only once the learner approves, as `anki-flashcards` does for any card. In a README whose numbering restarts under each section, a bare range is ambiguous, so the note names the section as well.
