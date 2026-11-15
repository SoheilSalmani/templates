# The repair queue

Reviews show which cards fail, which are slow to answer, and, through the `Source`, which have gone
out of date. Reading a card cold shows none of that: in the [Memory Machines
study](https://memory-machines.com/report) (Kirkby and Matuschak, 2026), no model judging prompts it
had never reviewed passed 70% at telling usable ones from broken ones, and the flaws it missed most
were wordiness and questions with several right answers. So the checks pick cards from the review
history, in code, and your part is the judgement: why this card, what to change, or nothing.

A check never changes the collection. It adds proposals to a queue, and the user approves them later
through the same approval table as every other change.

## The checks

`anki_cards.py candidates <kind>` prints the candidates as JSON: each note's fields, tags, cards,
lapses and reviews, and the `signal` that picked it.

| Kind | Picks | Why it is worth a look |
| --- | --- | --- |
| `failing` | Notes marked for repair; cards first answered in the last 60 days and failed 3 or more times since; cards with 2 or more lapses. Each failed in the last `--days`, 7 by default | The plainest evidence that a card is broken, and a new card costs the least to fix |
| `slow` | Cards in the slowest tenth by median answer time in review, over 3 or more answers in the last 90 days, or at `--seconds` and slower | A card passed slowly is usually wordy, vague, or a list in disguise, the flaws models judge worst |
| `sourced` | Notes with a `Source`, at random | A wrong or outdated fact passes every review. The source gives the check something to compare with |
| `random` | Notes studied in the last 90 days, at random | A control. When it finds little the other checks missed, stop running it |
| `inbox` | Notes in the Inbox and its project decks with a lint error. Beside them, under `proposals`: each learnt Inbox note's move, and every note in the collection whose `speed::fast` tag disagrees with its rule | New cards get a second look while they are still being learnt, and two rules move notes on and keep the tag true without anyone deciding |

Marking is how the user asks for a repair while reviewing: Mark Note, the `*` key, puts Anki's
`marked` tag on the note, and the next `failing` run picks it up whether or not the card failed.

The queue holds a note back while a proposal for it is pending, for a cool-down after a check of the
same kind closed one (30 days for `failing`, 90 for `slow`, `random` and `inbox`, 180 for
`sourced`), and for 30 days after any fix was applied, so that the fix has reviews to show for
itself. A marked note waits only while a proposal is pending: marking it again is a new request.
The inbox check rests its moves, its tag changes and its diagnoses apart, so a kept diagnosis never
holds back a move, and a move or a tag change, which fixes nothing, holds a note back from no check.

`--max` caps the candidates, worst first for `failing` and `slow`; the inbox check's proposals are
never capped. `--no-client` leaves out notes tagged `client::<name>`, for a run on a model the
client has not cleared.

## Diagnosis and action

Run the self-audit in SKILL.md on each candidate, read its signal, and give it one diagnosis and one
action. The signal says where to look, not what is wrong: a card fails because it asks for two
things, because the fact is hard, or because the user never learnt what it builds on.

| Diagnosis | Action | The proposal carries |
| --- | --- | --- |
| Fine as it is: the signal has another cause, such as a code task that is long by design | `keep` | the reason, in `diagnosis` |
| Badly formed: a set, two questions, several defensible answers, a vague Front | `rewrite`, or `split` when it holds two facts | `fields`, or `newNotes`; a split deletes the old note |
| Missing prerequisite: it cannot be answered without something the collection does not hold | `prerequisite` | `newNotes` for the missing facts, filed to `Inbox`, or a `resource` to read first |
| Confused with a sibling, found with `mcp__anki__findNotes` on the same `Topic` | `differentiate` | `fields` that put the name telling them apart in the question |
| Wrong or out of date against its `Source` | `fix-fact` | `fields`, with the date or version in the text |
| Not worth its reviews: it fails the sigh test, or nothing the user does needs it | `suspend` or `delete` | the reason, in `diagnosis` |

Every proposal follows SKILL.md: house style, and no fact its source does not state. Keep the
`Source` the note has. When it has none, say so in the diagnosis rather than guess one, as in the
Inbox; only a prerequisite card, a new fact, names the page it comes from. Before writing a
prerequisite card, search the collection for the fact under every name it goes by. A rewrite that
keeps the fact keeps the card's history; a split, a delete and a change of note type lose it, so the
diagnosis says so.

Before drafting, read the verdicts already given on the subject:
`anki_cards.py queue list --status decided --topic "<Topic>"`. A rejection's reason is the user's
taste, stated once. Follow it rather than proposing the same change again.

## Proposals

`anki_cards.py queue add <file>` takes one proposal or a JSON array of them. It checks each against
its note as it stands and refuses a batch in which any proposal brings a lint error the note did not
already have, appending nothing until the whole batch passes. An old gap, such as a `Source` nobody
can name any more, does not block a fix; it shows in the approval table instead.

```json
[
  {"kind": "failing", "noteId": 1794100000001, "action": "rewrite", "model": "<the model drafting>",
   "signal": "lapsed 4 times, last failed on 2026-11-12",
   "diagnosis": "\"What about autovacuum?\" fits several answers. Ask for the one the Back gives.",
   "fields": {"Front": "When does autovacuum process a table?"}},
  {"kind": "slow", "noteId": 1794100000002, "action": "keep",
   "diagnosis": "A nine-line task card ending in a Check: line, slow by design and never failed."}
]
```

`fields` holds only the fields that change. Each of `newNotes` has the shape of a draft,
`{"deckName", "modelName", "fields", "tags"}`, and never names an archived deck. A field fix needs no
`tags`: when its new fields change what the `speed::fast` rule says, `queue add` records the tag
change beside it, to apply with the fields.

## The inbox check

Its `proposals` come from rules and carry their own diagnosis: queue the array exactly as printed.
Each is one of two actions:

| Action | Decided by | The proposal carries |
| --- | --- | --- |
| `move` | Every card of the note has an interval of 21 days or more. It goes to the current deck holding the most cards with its `Topic` | `toDeck`, or null when no current deck holds the Topic and the user names one |
| `retag` | The `speed::fast` rule in `house-style.md` disagrees with the note's tag | `tags`, `{"add": ["speed::fast"]}` or `{"remove": ["speed::fast"]}` |

`queue add` refuses a move for a note that is not learnt, a move to an archive or into the Inbox, a
tag change the rule does not call for, and either action from any other check. The check's
`candidates` are notes in the Inbox with a lint error, which get a diagnosis and an action like any
check's. A note gets one proposal a run, a diagnosis first, then a tag change, then a move: the
others wait for the next run.

## Running unattended

A scheduled run has nobody to approve, so it calls no Anki tool that writes: no `addNotes`,
`updateNoteFields`, `deleteNotes`, `changeDeck`, `addTags`, `removeTags`, suspension or
`createModel`. It asks no questions either.

1. Run `anki_cards.py candidates <kind>` with the flags the schedule names. When AnkiConnect is
   unreachable, run `anki_cards.py queue skip --kind <kind> --reason "AnkiConnect unreachable"` and
   stop: the report counts missed runs, so silence never reads as a clean week.
2. Work through the candidates in order. After every few, write their proposals to a file and run
   `queue add`, so that a run cut short keeps what it finished. Fix a refused batch and add it again.
   The inbox check's `proposals` go to `queue add` first, as printed.
3. Queue a `keep` for every candidate that needs nothing. It counts in the report and holds the note
   back from the next runs.
4. End with one line: the candidates, and how many of each action.

## Going through the queue

When the user asks to go through their repair queue:

1. Run `anki_cards.py queue list`. It names any report saved since the last verdict; show that
   first.
2. Read the proposals from `queue list --json` and show them as the approval table: the card as it
   stands, the proposal, the diagnosis, and what the change costs in review history.
3. Apply what the user approves as "Reviewing existing cards" in SKILL.md says, then record each
   verdict: `anki_cards.py queue decide <id>... --status applied`, or `--status rejected --reason
   "<their reason>"`. A rejection needs the reason, in the user's words, because later runs read it.
   A rule's proposals go in the table grouped, the moves by destination and the tag changes as one
   row. A `move` goes through `mcp__anki__changeDeck`, with every card of the note read fresh from
   `notesInfo`, to its `toDeck`. When `toDeck` is null, ask for a deck, a broad category the user
   studies on its own, or reject the move with their words when they keep the note with its
   project. A proposal's `tags`, on a `retag` or beside a field fix, goes through
   `mcp__anki__addTags` or `mcp__anki__removeTags`.
4. Remove the `marked` tag from the notes `queue decide` names, with `mcp__anki__removeTags`.

## The report

`anki_cards.py queue report` tabulates, for each check over the last 30 days, the notes checked, the
share that needed a change, the share of proposals the user accepted, the pending ones, and the runs
that could not reach Anki. For field fixes applied at least 30 days ago, it compares Again presses
per answer in the 30 days before the proposal with the 30 days after the fix. `--save` also writes
it to `reports/` beside the queue file.

Read it for what to change, not as a score. A check whose proposals are mostly rejected costs the
user time: pause it. A fix that keeps coming back, the same flaw in card after card, belongs in this
skill as a rule or a worked example, where it stops the next cards from being written that way.

## The queue file

`anki-flashcards/queue.jsonl` in the XDG state directory, `~/.local/state` unless `$XDG_STATE_HOME`
says otherwise; `--queue` points elsewhere. It holds card text, so it stays out of every repository.
One JSON record per line, appended and never rewritten:

- `proposal`: `id`, `at`, `kind`, `noteId`, `cardIds`, `topic`, `action`, `diagnosis`, `signal`,
  `fields`, `newNotes`, `resource`, `toDeck`, `tags`, `model`
- `decision`: `id`, `at`, `status` (`applied` or `rejected`), `reason`
- `skip`: `at`, `kind`, `reason`

## On a schedule

Each check runs as a schedule of its own, which starts a fresh agent in a project that installs this
skill and the anki MCP server. With Paseo, unattended in oh-my-pi's full mode:

```sh
paseo schedule create --name anki-failing --cron "0 20 * * *" --timezone <zone> \
  --provider omp/<model> --mode full --thinking medium --cwd <project> \
  "Run the failing check of the anki-flashcards repair queue unattended, as its references/repair-queue.md says: python3 .agents/skills/anki-flashcards/scripts/anki_cards.py candidates failing --max 20"
```

- Run `failing` daily, `inbox` weekly, the other checks weekly or monthly, and `queue report --save`
  monthly.
- Archive on finish can stay on: everything a run produces is in the queue.
- Anki must be open when a run fires. On macOS, App Nap must be off for Anki, or AnkiConnect stops
  answering in the background: `defaults write net.ankiweb.dtop NSAppSleepDisabled -bool true`, then
  restart Anki.
- Client cards go only to a model the client has cleared, so give the other runs `--no-client`. The
  inbox check moves client cards too, so it runs on a cleared model, without the flag.
