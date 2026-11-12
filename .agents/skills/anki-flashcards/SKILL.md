---
name: anki-flashcards
description: Author Anki flashcards that are atomic, accurate, readable, and easy to recall, then add them to the user's collection over AnkiConnect. Use when asked to make flashcards, Anki cards, or study cards from any source (a web page, a Confluence or Notion page, a PDF, a repository or source code, API docs, a paper, or the current conversation), and also when asked to review, critique, or fix existing cards, or to organize the cards waiting in the Inbox deck. Encodes the SuperMemo twenty rules, Andy Matuschak's prompt attributes, and this collection's own note-type and formatting conventions.
allowed-tools: Read, Grep, Glob, WebFetch, Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/anki_cards.py:*), mcp__anki__listDecks, mcp__anki__modelNames, mcp__anki__modelFieldNames, mcp__anki__findNotes, mcp__anki__notesInfo, mcp__anki__getTags
---

# Authoring Anki flashcards

A card is a tool for one retrieval. If it asks for two things, it teaches neither. Everything below
follows from that.

Four targets, in priority order when they conflict: accurate, atomic, easy to recall, readable.
Accuracy wins over everything. A card that is memorable and wrong is worse than no card.

## Non-negotiable

Never write to the collection before showing the drafted cards and getting explicit approval.
Bad cards are expensive: they cost review time for months and are tedious to find and repair.
The approval table is the whole safety mechanism. Do not skip it, and do not treat "make me some
cards" as advance approval of specific cards.

Never invent facts to fill a card. If the source does not state it, the card does not exist.
When the source is thin or self-contradictory, say so and card only what it actually supports.

## Workflow

1. Read the source in full before writing anything. If you do not understand it, stop and say so
   rather than carding it. Memorising something you do not understand produces unusable knowledge
   (SuperMemo rules 1 and 2).
2. Run `python3 scripts/anki_cards.py check` from this skill's directory. If Anki is down,
   offer to launch it with `open -a Anki`, then wait for AnkiConnect on port 8765.
3. Write a fact inventory: one line per candidate fact, in plain text, before any card formatting.
   Then cut. Most sources deserve 5 to 15 cards, not one per sentence. Cutting is the main quality
   lever you have, so say out loud what you dropped and why. From code or API docs, mark each fact
   with what the user will do with it: type it, read it, or decide with it (see Code below).
4. Pick the deck, the note type, and the `Topic` or `Tool` value. Run
   `anki_cards.py inspect "<deck>"` to see what the deck already uses and to get real field names.
   Never guess field names. See `references/note-types.md`. When the user asks for the Inbox or says
   the cards are not urgent, or when no current deck fits, the deck is `Inbox` (see "The Inbox"
   below). Never add to a deck whose name starts with `_Legacy`.
5. Draft to a JSON file in the scratchpad directory, one object per note. Shape:
   `{"deckName": ..., "modelName": ..., "notes": [{"fields": {...}, "tags": [...]}]}`
6. Self-audit against the checklist below, then run
   `anki_cards.py lint <draft.json>`. Fix every violation and re-lint until clean. The linter is
   mechanical, so it catches slips but cannot judge whether a card is worth having. That is your job.
7. Show the cards as a table, get approval, then add with `mcp__anki__addNotes`, one call per
   deck-and-model pair, at most 100 notes per call. Report what was created and what you left out.

## Rules

Atomicity and content:

- One card, one retrieval. A Front containing "and", "or", a slash, or two question marks is two cards.
- Prefer a question-and-answer card. Reach for cloze when the fact reads naturally as a sentence,
  when you want both directions of an acronym or pairing, for a closed list, or to blank the line
  that matters in a code snippet.
- Never ask for a set ("what are the five pillars"). Convert it into one cloze card per member, or
  drop it. Listing members in a different order each review actively damages recall (SuperMemo 9).
- A procedure is an enumeration. Card what carries knowledge: the step people get wrong, the
  condition that gates the next step, and why a step exists. Skip steps anyone doing the task would
  infer. Asking for the whole sequence is an optional extra: one card for three steps or fewer
  where each leads to the next, or, when a longer outline itself must be known, a cloze with one
  index per step (SuperMemo 10).
- No yes-or-no and no true-or-false Fronts. A coin flip is not retrieval. Rephrase as an open question.
- No card whose answer is inferable from its own Front. If reading the question hands you the answer,
  the card trains nothing.
- Ask "why" and "how" as well as "what". An explanation card holds better than a bare label, and
  gives the fact something to hang on.
- Date-stamp volatile facts inside the card text: figures, versions, org charts, prices, headcounts.
  Write "as of March 2026" in the card, not just in a tag.
- Skip facts that are trivially derivable, that you would look up rather than recall, or that only
  matter once.

Code, from source files, API docs, or a codebase the user works in:

- Card the use. A fact the user will type (a call, a command, a flag, a config key) gets a
  production card: the Front states the goal with the names and values it needs, and the Back is
  the code. Code they will read goes on the Front, asking what it returns, what it is for, or which
  line is wrong. What they will decide with (why it is built this way, what must hold, what breaks)
  gets a prose card with a one-reason answer. Neither kind trains the other, so mix them within a
  topic rather than doing one first.
- Size a code answer by what it holds. One line is the best-kept card. Up to six lines is fine when
  they belong together, such as an idiom. Past six a review takes about twice as long, so only a
  pattern the user writes again and again goes further, up to twelve lines, as a skeleton: the
  Front names the pattern and its setting, the Back holds only the lines that make the pattern and
  then a `Check:` line naming the parts to grade, and the card sits on top of cards for its key line
  and for when to use it. Inside a longer snippet, blank the line that matters as a code cloze.
- Never "Write an example of X": any correct example is right, so the Back cannot grade it. Name the
  task so that one answer is right.
- Card a call only when recalling it beats looking it up. Not what the editor completes, such as a
  full import path.
- From a codebase, card what the code does not say: why it is written this way, what must hold,
  where things live at module level, the path a request or a record takes, and the gotchas. Never a
  verbatim implementation. The code is always there to re-read, and it changes under the card.
- A whole function, program, or algorithm problem is an exercise, not a Back. Anki can still
  schedule it: offer a card that points to the exercise, written in an editor and checked against
  tests, in a deck of its own, or the `Coding Exercises` note type if the user keeps an exercise
  repository.

Phrasing:

- The Front never carries the `Topic` or `Tool` value as a label prefix. The note type renders it
  above the question already, so `"Acme R&D: which committee ..."` is redundant. Naming the subject
  inside the question is fine when it reads better, as in "What does `--frozen` do in `uv run`?".
- Shortest wording that stays unambiguous. Cut "What is the ...?" to the noun phrase when it reads
  cleanly, and cut preamble that the Topic line already supplies.
- One unambiguous answer. If two answers are defensible, the Front is underspecified: add the
  qualifier that picks one.
- Watch interference between sibling cards. When a source gives you six parallel items, near-identical
  Fronts will blur together under review. Differentiate by the distinguishing content, or card only
  the items that carry weight.
- Match the source language. A French source gets French cards.

Formatting, in full in `references/house-style.md`:

- Back is normally one short sentence ending in a period. A code Back is the code alone, with no
  period: `<code>` for one line, `<pre><code>` for more, and a pattern skeleton ends with its
  `Check:` line.
- `<code>` for identifiers, flags, paths, and commands. `<i>` for a term being defined.
- No bold, no emoji, no em dash, no curly quotes, no bold-header bullet lists. Sources full of
  emoji headings and bold (Confluence and Notion especially) must be stripped, not mirrored.
- Steps on a Back: two are one sentence joined with "then", such as `Add the package to
  <code>packages.yml</code>, then run <code>dbt deps</code>.` Three are an `<ol>`, one short item
  per step, each opening with its verb. Four or more are more than one card.
- `<ol>` also lays out a procedure inside a cloze Text, one cloze index per `<li>`, never running
  across two items. Numbers assert order and count, so never use `<ol>` for a set, criteria, or
  conditions.
- `<ul><li>` only for a closed list of two or three items that belongs on one card.
- Escape `<`, `>` and `&` inside code, or `List<String>` loses its `<String>`. In a cloze, a `::`
  inside a deletion starts a hint, and a `}` just before the closing braces ends the deletion early.
  Break both with `<!-- -->`: `fmt:<!-- -->:Display`, `{}<!-- -->}}`.
- Tags: lowercase kebab-case, sparse, thematic, plus exactly one source tag such as
  `confluence-acme-rd` or `supermemo-20-rules`.

## Self-audit before showing cards

Walk the drafted set once and ask:

1. The sigh test. Reading this Front cold, would you groan? A groan means it is too broad, too
   ambiguous, or not worth remembering. Fix it or cut it.
2. Does any Front ask for two things?
3. Could any two cards in this batch be confused for each other?
4. Is every answer traceable to the source, with no inference of your own presented as fact?
5. Does any Front repeat its own Topic or Tool value?
6. Is any Back longer than it needs to be?
7. For each procedure, does the step that is easiest to get wrong have a card of its own?
8. Does every fact the user will type have a card that makes them produce it? Is every Back over
   six lines of code a pattern skeleton with its `Check:` line?
9. Would you want this card in six months?

## Reviewing existing cards

When asked to critique or repair cards, fetch them with `mcp__anki__findNotes` and
`mcp__anki__notesInfo`, run the same audit, and report findings per note id with a concrete
rewrite for each. Apply changes with `mcp__anki__updateNoteFields` only after approval. Rewording a
field, such as making a list's items parallel, keeps the card's review history. Splitting a
bundled card means creating new notes and deleting the old one, which loses its review history, so
call that out and let the user decide. A long code Back usually becomes a production card for the
call that matters plus a code cloze for its context, a pattern skeleton when the shape is what the
user needs, or an exercise for a whole program (worked examples 10 and 11).

## The Inbox

`Inbox` is a top-level deck where cards wait to be filed. The user does not study it, so filing is
what puts its cards into review.

A card sent to the Inbox gets everything but its deck: note type, `Topic` or `Tool`, tags. The
context field is what the card shows, and the deck never appears in review. A card from client work
also gets a `client-<name>` tag such as `client-acme`, because the client is the one thing a
deck said that the card does not. New cards go to `Inbox` itself, never to an `Inbox::<client>`
subdeck. The subdecks that exist empty out as their notes are filed.

When asked to organize or file the Inbox:

1. Run `anki_cards.py inbox`. It groups the waiting notes by context value and shows where cards
   with that value already live, which cards were studied and are overdue, the client tag each
   subdeck still needs, and lint findings.
2. Propose one row per note: target deck, tags to add, and any fix the audit or the linter found.
   Decks are broad categories the user studies separately, so most notes go to an existing deck.
   When nothing fits, propose one new broad deck under a placeholder name and ask the user to name
   it. Never rebuild the nested tree under `_Legacy`. Report a missing source tag rather than
   guessing one. The source is usually out of reach by now, so audit the form, and flag a doubtful
   fact instead of rewriting it. Fixes follow "Reviewing existing cards" above.
3. Lead with what is decaying. Studied cards keep falling due in the Inbox, and a card that has
   waited more than two weeks is losing the context it was written in.
4. After approval, apply fixes and new notes first, then add tags with `mcp__anki__addTags`, then
   move every card of each note with `mcp__anki__changeDeck`. Read the card ids after the fixes,
   because a new cloze index makes a new card. A move keeps the card's schedule and review history.
   Hand the user anything these tools cannot do, such as changing a note type, and name any emptied
   subdeck for them to delete.

## Reference files

Load these as needed rather than up front:

- `references/note-types.md`. Every note type in this collection with its exact fields, how its
  template renders, usage counts, and which to pick. Also the two API traps that break batches.
  Read this before choosing a note type.
- `references/house-style.md`. Formatting, HTML, tags, language, and the prose rules for card text.
  Read this before drafting.
- `references/principles.md`. The research canon with attribution. Read this when a judgement call
  is genuinely unclear, for example how to handle an open-ended list, which parts of a procedure to
  card, which facts from code deserve a code card, or whether two cards on one fact is redundancy or
  waste.
- `references/worked-examples.md`. Before-and-after rewrites of real bad cards. Read this if the
  rules above feel abstract, or to calibrate how short a good Back is.
