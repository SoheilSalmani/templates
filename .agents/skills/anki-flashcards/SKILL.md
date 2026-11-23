---
name: anki-flashcards
description: Author Anki flashcards that are atomic, accurate, readable, and easy to recall, then add them to the user's collection over AnkiConnect. Use when asked to make flashcards, Anki cards, or study cards from any source (a web page, a Confluence or Notion page, a PDF, a repository or source code, API docs, a paper, or the current conversation), and also when asked to review, critique, or fix existing cards, to find the cards worth fixing from their review history or run those checks on a schedule, to go through the repair queue, to organize the Inbox and its project decks, or to set up the note types the skill uses. Encodes the SuperMemo twenty rules, Andy Matuschak's prompt attributes, and the skill's own note types and formatting conventions.
allowed-tools: Read, Grep, Glob, WebFetch, Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/anki_cards.py:*), mcp__anki__listDecks, mcp__anki__modelNames, mcp__anki__modelFieldNames, mcp__anki__findNotes, mcp__anki__notesInfo, mcp__anki__getTags, mcp__anki__createModel
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
   offer to launch it with `open -a Anki`, then wait for AnkiConnect on port 8765. The check also
   reports whether the skill's four note types are there. A missing one is created only after the
   user approves, and one that differs is the user's to fix: see "Setting them up" in
   `references/note-types.md`.
3. Write a fact inventory: one line per candidate fact, in plain text, before any card formatting.
   Then cut. Most sources deserve 5 to 15 cards, not one per sentence. Cutting is the main quality
   lever you have, so say out loud what you dropped and why. From code or API docs, mark each fact
   with what the user will do with it: type it, read it, or decide with it (see Code below).
4. Pick the deck, the note type, and the `Topic` value. Run `anki_cards.py inspect "<deck>"` to see
   what the deck already uses and to get real field names. Never guess field names. See
   `references/note-types.md`. Cards learnt for a project, a client mission or a personal one, go
   to `Inbox::<project>`. When the user asks for the Inbox, says the cards are not urgent, or no
   current deck fits, the deck is `Inbox` (see "The Inbox" below). Never add to an archived deck, a
   top-level deck whose name starts with `_`.
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
  Write "as of March 2026" in the card, not in the `Source`.
- Skip facts that are trivially derivable, that you would look up rather than recall, or that only
  matter once.

Code, from source files, API docs, or a codebase the user works in:

- Card the use. A fact the user will type (a call, a command, a flag, a config key) gets a
  production card: the Front states the goal with the names and values it needs, and the Back is
  the code. Code they will read goes on the Front, asking what it returns, what it is for, or which
  line is wrong. What they will decide with (why it is built this way, what must hold, what breaks)
  gets a prose card with a one-reason answer. Neither kind trains the other, so mix them within a
  topic rather than doing one first. When the user wants to write the code without looking it up,
  most of their code cards ask for code, and each Front describes the situation they will be in
  while coding: recalling a command when asked for it is not noticing when to use it.
- Size a code answer by what it holds. One line is the best-kept card. Up to six lines is fine when
  they belong together, such as an idiom. Past six a review takes about twice as long, which is
  worth paying for code the user writes again and again, a pattern or a task from their work: a
  task card goes up to twelve lines, holds only the lines that make the pattern, ends with a
  `Check:` line, and sits on top of cards for its key line and for when to use it. Inside a longer
  snippet, blank the line that matters as a code cloze.
- Asking the user to write code, an example included, is the most direct practice for writing it.
  The Front sets the task: the setting, the names, and what the code must do, or "of your choice"
  when any example will do. The Back holds one solution, then a `Check:` line naming what every
  correct answer contains, so a different correct solution passes. What fails is a bare "Write an
  example of X" with one long answer to compare by eye, because nothing on the card says what
  counts as right. For a pattern that matters, two or three task cards in different situations, or
  one that leaves the example to the user, keep the review from turning into recall of one text.
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

- The Front never carries the `Topic` value as a label prefix. The note type renders it above the
  question already, so `"Acme R&D: which committee ..."` is redundant. Naming the subject inside the
  question is fine when it reads better, as in "What does `--frozen` do in `uv run`?".
- The `Topic` holds what you would already know when you need the fact: the tool you are working
  in, or the subject you are thinking about. It never holds an answer, so it never names the tool
  when the card asks which tool to use. If a Back or a cloze deletion equals it, widen it to the
  subject the card belongs to (`Web APIs`, not `Fetch API`). Prefer a value many cards share: one
  that only a handful of cards carry works as a hint.
- Shortest wording that stays unambiguous. Cut "What is the ...?" to the noun phrase when it reads
  cleanly, and cut preamble that the Topic line already supplies.
- One unambiguous answer. If two answers are defensible, the Front is underspecified: add the
  qualifier that picks one.
- Watch interference between sibling cards. When a source gives you six parallel items, near-identical
  Fronts will blur together under review. Differentiate by the distinguishing content, or card only
  the items that carry weight. Two Fronts that differ only in their `Topic` are the extreme case: put
  the name that tells them apart in the question.
- Match the source language. A French source gets French cards.

Formatting, in full in `references/house-style.md`:

- Back is normally one short sentence ending in a period. A code Back is the code alone, with no
  period: `<code>` for one line, `<pre><code>` for more, and a task card ends with its `Check:`
  line.
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
- `Source` on every card: a link to the page the fact came from, with the page title as the link
  text, such as `<a href="https://docs.astral.sh/uv/reference/cli/">uv CLI reference</a>`, or the
  source in plain text when it has no URL.
- Tags: `speed::fast` on every card the rule in `references/house-style.md` marks quick to review,
  and no other tag. The linter applies that rule, so a request never decides it. The subject is the
  `Topic`, the source is the `Source`, the kind of card is its note type, and the project is its
  `Inbox::<project>` deck.

## Self-audit before showing cards

Walk the drafted set once and ask:

1. The sigh test. Reading this Front cold, would you groan? A groan means it is too broad, too
   ambiguous, or not worth remembering. Fix it or cut it.
2. Does any Front ask for two things?
3. Could any two cards in this batch be confused for each other?
4. Is every answer traceable to the page its `Source` names, with no inference of your own
   presented as fact?
5. Does any Front repeat its own `Topic`, and does any `Topic` give away an answer?
6. Is any Back longer than it needs to be?
7. For each procedure, does the step that is easiest to get wrong have a card of its own?
8. Does every fact the user will type have a card that makes them produce it? Does every card that
   asks for an example, and every Back over six lines of code, end with a `Check:` line?
9. Would you want this card in six months?

## Reviewing existing cards

When asked to critique or repair cards, fetch them with `mcp__anki__findNotes` and
`mcp__anki__notesInfo`, run the same audit, and report findings per note id with a concrete
rewrite for each. Apply changes with `mcp__anki__updateNoteFields` only after approval. Rewording a
field, such as making a list's items parallel, keeps the card's review history. Splitting a
bundled card means creating new notes and deleting the old one, which loses its review history, so
call that out and let the user decide. A card that asks for code to write usually stays one: give
its Front the task and its Back a `Check:` line, which are field edits that keep its history. A
long code Back becomes a task card cut to the lines that make the pattern, a production card for
the call that matters, or an exercise for a whole program (worked examples 10 and 11).

## Improving cards from their reviews

Reviews show which cards fail, which are slow, and which have gone out of date; reading cards cold
does not. `anki_cards.py candidates <kind>` picks them from the review history: `failing`, `slow`,
`sourced` or `random`, and `unsourced` picks the cards whose `Source` links no page, to find the page
that states their fact. You diagnose each, draft one proposal, and `anki_cards.py queue add` keeps it
in a repair queue the user approves from later. Marking a note while reviewing, the `*` key, asks
for its repair. The `inbox` check also prints proposals a rule decides, ready to queue as they are:
the moves of learnt notes out of the Inbox, and the `speed::fast` changes its rule calls for.

- A run of a check never writes to the collection and asks nothing: it queues proposals, and records
  a missed run when Anki is closed.
- When the user asks to go through the queue, show the approval table, apply what they approve as
  above, and record every verdict with `anki_cards.py queue decide`.

Read `references/repair-queue.md` before running a check or going through the queue: what each
check picks, the diagnoses and their actions, the queue file, and how to run the checks on a
schedule.

## The Inbox

`Inbox` holds the cards still being learnt. A project, a client mission or a personal one, gets a
subdeck, `Inbox::<project>`, so that its cards can be studied as a set while the work lasts. Cards
with no project go to `Inbox` itself.

A card sent to the Inbox gets everything but its final deck: note type, `Topic`, `Source`, tags.
The `Topic` is what the card shows, and the deck never appears in review.

A note leaves the Inbox once it is learnt: every card of it has an interval of 21 days or more,
which Anki calls mature. It moves to the current deck holding the most cards with its `Topic`. When
no current deck does, the user names one, a broad category they study on its own, or keeps the note
with its project, and the Topic's later notes follow the deck they chose. Never move a note to an
archived deck, and never rebuild an archived tree.

The repair queue's `inbox` check proposes these moves every week. When the user asks to organize
the Inbox now:

1. Run `anki_cards.py inbox`. It groups the notes by `Topic` and says where cards with each one
   live, marks the learnt notes, counts the overdue cards, lists the project decks, and lists lint
   findings.
2. Propose one row per learnt note: the deck the rule gives, or, when it gives none, a broad deck
   under a placeholder name for the user to name, or keeping the note with its project. Notes not
   yet learnt stay where they are. A missing `Source`, or one that names a site rather than a page,
   gets the page that states the fact, found as `references/house-style.md`, "Source", says, or is
   reported when no page does. That page also settles a doubtful fact; with none, flag the fact
   instead of rewriting it. A note that names its source in a tag instead gets that name moved into
   `Source` as plain text, and the tag removed. Fixes follow "Reviewing existing cards" above.
3. Lead with what is decaying. Studied cards keep falling due, and a card that has waited more than
   two weeks is losing the context it was written in.
4. After approval, apply fixes and new notes first, then tags with `mcp__anki__addTags` and
   `mcp__anki__removeTags`, then move every card of each note with `mcp__anki__changeDeck`. Read the
   card ids after the fixes, because a new cloze index makes a new card. A move keeps the card's
   schedule and review history. Hand the user anything these tools cannot do, such as changing a
   note type, and name any emptied project deck for them to delete.

## Reference files

Load these as needed rather than up front:

- `references/note-types.md`. The skill's four note types, defined in `assets/note-types.json` and
  `assets/card.css`: their fields, how they render, which to pick, how to set up one that is missing
  or older than its `Source` field, and the API traps that break a batch or drop a field. Read this
  before choosing a note type.
- `references/house-style.md`. Formatting, HTML, the `Source` field, the two tags and the speed
  rule, language, and the prose rules for card text. Read this before drafting.
- `references/principles.md`. The research canon with attribution. Read this when a judgement call
  is genuinely unclear, for example how to handle an open-ended list, which parts of a procedure to
  card, which facts from code deserve a code card, or whether two cards on one fact is redundancy or
  waste.
- `references/worked-examples.md`. Before-and-after rewrites of real bad cards. Read this if the
  rules above feel abstract, or to calibrate how short a good Back is.
- `references/repair-queue.md`. Finding the cards worth fixing from their reviews, the repair queue,
  the weekly inbox check, and running the checks on a schedule. Read this before running a check or
  going through the queue.
