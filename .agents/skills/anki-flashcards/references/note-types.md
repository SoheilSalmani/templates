# Note types in this collection

Counts taken from the live collection on 2026-11-12. "Current" excludes the `_Legacy` and `_Legacy2`
deck trees, where the old deck hierarchy is archived. Re-check with `anki_cards.py inspect` rather
than trusting these numbers indefinitely.

## Pick from these

| Note type | Fields | Current / total | Use for |
| --- | --- | --- | --- |
| `Q&A by topic` | `Front`, `Topic`, `Back` | 56 / 3180 | Any question and answer: tools, concepts, domains, finance, licences, science |
| `Cloze by topic` | `Text`, `Topic` | 9 / 1760 | Sentence-shaped facts, acronym pairs, closed lists, code with the line that matters blanked |
| `Keyboard Shortcut` | `Front`, `Tool`, `Shortcut`, `Shortcut (macOS)`, `Shortcut (Windows)`, `Shortcut (Linux)` | 0 / 85 | Key bindings, with per-OS variants when they differ |
| `Image Occlusion (for a topic)` | `Occlusion`, `Topic`, `Image`, `Header`, `Back Extra`, `Comments` | 0 / 19 | Diagrams, maps, anatomy, UI screenshots |

The first two carry 98 percent of these notes. Default to `Q&A by topic` unless the fact genuinely
reads better as a cloze.

Tools, licences and body parts had note types of their own until 2026-11-12, with the context field
named `Tool`, `License` or `Body part`. They differed from the topic types only in that name and in
the colour of the line, and the split did not hold: seven of the ten largest topics were software.
Every one of those notes now sits in a topic type with its value in `Topic`, and the old types are
empty. Only `Keyboard Shortcut` and `Tutorial (platform-specific)` still call the field `Tool`.

## Do not use for new cards

| Note type | Why |
| --- | --- |
| `Q&A (for a tool)`, `Cloze (for a tool)`, `Image Occlusion (for a tool)`, `Q&A (for a license)`, `Cloze (for a license)`, `Q&A (for a body part)`, `Cloze (for a body part)` | Empty since their notes moved to the topic types on 2026-11-12. Use the topic type, with the tool, licence or body part as the `Topic`. |
| `Basic` | Legacy, 3783 notes, all in the archived trees. It has no context field, and only one Front in six names its subject, so the others leaned on the deck they were filed in. |
| `Cloze` | Legacy, now empty. Its 10 notes moved to `Cloze by topic` on 2026-11-12, with an empty `Topic`. |
| `Basic (and reversed card)` | Legacy, 81 notes, all in the archived trees. For a two-direction fact use one cloze note with `c1` and `c2` instead. |
| `Basic (optional reversed card)`, `Basic (type in the answer)`, `Basic (and reversed card) (without question in answer)`, `Alphabet` | Zero notes. Not part of this collection's practice. |
| `Language Reactor - Phrase` | Written by the Language Reactor browser extension. Do not hand-author. |
| `Recipe`, `Coding Exercises`, `Practice Activity`, `Tutorial (platform-specific)`, `Keyboard Layout`, `Vocabulary (Chinese)`, `Alphabet (Vietnamese)` | Purpose-built for one narrow workflow each. Use only when the user asks for that specific kind of note. |

One of these is worth knowing when a source calls for writing a whole function or program, which is
practice rather than a card. `Coding Exercises` has two fields, `Repository` and `Range`, and its
one card reads "Finish exercices {{Range}} in the <code>{{Repository}}</code> repository." Anki
schedules the session, and the work happens in an editor. Offer it instead of a long code Back, and
only the user can name the repository: never invent one.

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
`Keyboard Shortcut` renders its `Tool` field the same way.

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
`--like JS` finds `Next.js` but not `JavaScript`, the value 32 notes use.

Existing values are short noun phrases naming a tool or a subject, not sentences and not
hierarchies: `Causal Inference`, `Ableton Live`, `Mutuelle`, `PEA`, `Snowflake`,
`Server-sent events`, `Music Theory`, `Permis B`. Match that register.

Decks no longer say what a card is about: `Inbox` holds every tool, and the decks are broad. The
`Topic` is the only place a card's subject shows during review.

## Two traps that break a batch

1. `Cloze by topic` has no `Back Extra` field, only `Text` and `Topic`. The MCP `modelFieldNames`
   tool helpfully returns an `example` object mentioning `Back Extra` for anything cloze-shaped,
   which is wrong here. Passing that key rejects the whole batch. The plain legacy `Cloze` type, now
   empty, is the one that has it.
2. `mcp__anki__addNotes` takes one `deckName` and one `modelName` per call, capped at 100 notes.
   A mixed set of Q&A and cloze cards therefore needs one call per model. Duplicates are skipped
   individually, but a validation error such as an empty required field or a bad tag rejects the
   entire batch, so lint before sending.

## Cloze conventions used in this collection

Taken from real notes, verbatim:

```
{{c2::FR}} est l'acronyme de {{c1::<i>Frais Réels</i>}}.
A <code>scope="module"</code> fixture defined in {{c1::conftest.py}} is {{c1::shared by all test modules}} in that directory.
In the metric system, the prefix {{c1::deci-}} means {{c2::1/10}}.
```

Three patterns worth copying:

- Reuse the same index (`c1` twice) for blanks that must be recalled together on one card.
- Use `c1` and `c2` on the two halves of a pairing to get both directions from a single note. This is
  the legitimate redundancy of SuperMemo rule 17, and it replaces the legacy reversed note type.
- Blank the whole meaningful chunk, not one word out of a phrase. `{{c1::shared by all test modules}}`
  rather than `shared by all {{c1::test modules}}`.

On index count: three is the ceiling when the blanks are separate facts sharing a sentence, because
past that the note is a bundle wearing a cloze costume. A genuine closed list, or a procedure laid
out as an `<ol>` with one index per step, is the exception, and one index per member is correct
there even at five or six. The linter warns above three either way, so justify the warning rather
than suppressing it.
