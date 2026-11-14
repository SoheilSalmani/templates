# The skill's note types

Every card this skill writes uses one of four note types. They are defined in
`assets/note-types.json`, each in the shape Anki's `createModel` takes, and share the styling in
`assets/card.css`.

| Note type | Fields | Use for |
| --- | --- | --- |
| `Q&A by topic` | `Front`, `Topic`, `Back` | Any question and answer: tools, concepts, domains, rules, science |
| `Cloze by topic` | `Text`, `Topic` | Sentence-shaped facts, acronym pairs, closed lists, a code line blanked in context |
| `Keyboard Shortcut` | `Front`, `Topic`, `Shortcut`, `Shortcut (macOS)`, `Shortcut (Windows)`, `Shortcut (Linux)` | Key bindings. `Shortcut` when the keys are the same everywhere, the per-OS fields when they differ |
| `Coding Exercises` | `Repository`, `Range` | A pointer to exercises worked in an editor, never a card about code |

Default to `Q&A by topic` unless the fact genuinely reads better as a cloze.

`Coding Exercises` is for a source that calls for writing a whole function or program, which is
practice rather than a card. Its one card reads "Finish exercises {{Range}} in the
<code>{{Repository}}</code> repository." Anki schedules the session, and the work happens in an
editor. Offer it instead of a long code Back, and only the user can name the repository: never
invent one.

## Setting them up

`anki_cards.py check` reports each of the four as `ok`, `missing`, or `differs`:

- **Missing.** Tell the user what the note type holds and that you would create it. Once they
  approve, call `mcp__anki__createModel` with the arguments `anki_cards.py note-type "<name>"`
  prints. Adding a note type does not force a one-way sync.
- **Differs.** The type exists but lacks a field, is the wrong kind, or does not show `{{Topic}}`
  on its question. Report what differs and leave the fix to the user, because it changes notes
  they already review. Renaming a field keeps every note, its templates follow, and it needs no
  one-way sync. Adding, removing or reordering fields, and deleting a note type, force one.

Styling is the user's to change. `check` never compares colours or layout.

Image occlusion is not in the file. Anki's occlusion editor works only on note types derived from
its built-in Image Occlusion type, which `createModel` cannot make. For a diagram, have the user
add a copy of that type in Tools › Manage Note Types, give it a `Topic` field, and show
`<p id="topic">{{Topic}}</p>` above the image on its front.

## Other note types in a collection

A collection usually holds more: Anki's stock `Basic` and `Cloze`, types added by an extension,
types built for one narrow workflow. Use none of them for a new card unless the user asks for that
type by name, and never hand-author notes for a type an extension writes. `Basic` has no context
field, so its Fronts lean on the deck to say what they are about and turn ambiguous once decks are
mixed or reorganised. For a fact that needs both directions, use one cloze note with `c1` and `c2`
rather than a reversed type. The linter warns on any type outside the four.

## How the context field renders

This is the reason the Front must not repeat the topic. `Q&A by topic` template:

```html
Front: <p id="topic">{{Topic}}</p>
       <p>{{Front}}</p>
Back:  {{FrontSide}}
       <hr id=answer>
       {{Back}}
```

`Cloze by topic` renders the same line above `{{cloze:Text}}` on both sides of the card, and
`Keyboard Shortcut` adds the operating system beside it on the per-OS cards.

So the reviewer already sees the topic on its own styled line. A Front of
`"Acme R&D: which committee approves Gate 4?"` renders as:

```
R&D governance
Acme R&D: which committee approves Gate 4?
```

Write `"Which committee approves Gate 4?"` and let the field do its job. This is SuperMemo rule 16,
context cues simplify wording, built into the note type.

## Choosing the context value

`Topic` is free text, so consistency is on you. Reuse a value that already exists in the collection
instead of coining a near-duplicate. Check with:

```bash
python3 scripts/anki_cards.py topics --like "R&D"
```

The filter matches text, not meaning, so search under every name the subject goes by:
`--like JS` finds `Next.js` but not `JavaScript`.

Values are short noun phrases naming a tool or a subject, not sentences and not hierarchies, such as
`Causal Inference`, `Ableton Live`, `PEA`, `Snowflake`, `Server-sent events`, `Music Theory`.

The value is what the reviewer would already know at the moment they need the fact: the tool they
are working in, or the subject they are thinking about. Pick it at that level, never at the level of
the thing a card asks for:

- Never an answer. A value equal to a Back or a cloze deletion prints the answer above the question.
  The usual case is a definition filed under a topic named after the thing it defines, as in
  `{{c1::Fetch API}}` under the topic `Fetch API`, where `Web APIs` belongs. The linter rejects such
  a note (worked example 12).
- Broad and shared. A value many cards share tells subjects apart; one that only a few cards carry
  works as a hint.
- Never the tool when the card asks which tool to use. "Which tool both lints and formats Python,
  replacing Flake8 and Black?" goes under `Python`, not `Ruff`.
- Never the only difference between two cards. "Give the Literal interface." under `hast` and again
  under `mdast` is one question twice. The name that tells them apart goes in the question.

With broad decks and an `Inbox`, the deck does not say what a card is about. The `Topic` is the only
place a card's subject shows during review.

## Two traps that break a batch

1. `Cloze by topic` has no `Back Extra` field, only `Text` and `Topic`. The MCP `modelFieldNames`
   tool helpfully returns an `example` object mentioning `Back Extra` for anything cloze-shaped,
   which is wrong here. Passing that key rejects the whole batch.
2. `mcp__anki__addNotes` takes one `deckName` and one `modelName` per call, capped at 100 notes.
   A mixed set of Q&A and cloze cards therefore needs one call per model. Duplicates are skipped
   individually, but a validation error such as an empty required field or a bad tag rejects the
   entire batch, so lint before sending.

## Cloze conventions

Taken from real notes, verbatim:

```
{{c2::FR}} est l'acronyme de {{c1::<i>Frais Réels</i>}}.
A <code>scope="module"</code> fixture defined in {{c1::conftest.py}} is {{c1::shared by all test modules}} in that directory.
In the metric system, the prefix {{c1::deci-}} means {{c2::1/10}}.
```

Three patterns worth copying:

- Reuse the same index (`c1` twice) for blanks that must be recalled together on one card.
- Use `c1` and `c2` on the two halves of a pairing to get both directions from a single note. This is
  the legitimate redundancy of SuperMemo rule 17, and it replaces a reversed note type.
- Blank the whole meaningful chunk, not one word out of a phrase. `{{c1::shared by all test modules}}`
  rather than `shared by all {{c1::test modules}}`.

On index count: three is the ceiling when the blanks are separate facts sharing a sentence, because
past that the note is a bundle wearing a cloze costume. A genuine closed list, or a procedure laid
out as an `<ol>` with one index per step, is the exception, and one index per member is correct
there even at five or six. The linter warns above three either way, so justify the warning rather
than suppressing it.
