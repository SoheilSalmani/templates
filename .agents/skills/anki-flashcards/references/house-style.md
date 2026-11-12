# House style for card text

Derived from sampled notes in the live collection, plus the writing rules from the `humanizer` skill.
Cards are prose that gets read hundreds of times, so the writing rules matter more here than in
ordinary text, not less.

## Real cards from the collection

These are verbatim. They are the target.

```
Tool:  uv
Front: What does the <code>--frozen</code> option do when using <code>uv run</code>?
Back:  Run without updating the lockfile.

Tool:  Vim
Front: What is the difference between a temporary setting and a permanent setting in Vim?
Back:  A temporary setting (e.g., <code>:set number</code>) is lost when Vim closes. A permanent setting is written to vimrc and persists across sessions.

Tool:  Dagster
Front: Which tool is used to quickly scaffold a Python package containing a Dagster <code>Definitions</code> object?
Back:  The <code>create-dagster</code> CLI.

Topic: Bot Detection
Front: Which tool uses the WebDriver protocol?
Back:  Selenium WebDriver.

Topic: Causal Inference
Front: Why can ML models not answer causal questions?
Back:  ML is about prediction and correlation, not causal structure. It cannot handle inverse causality, like low prices being associated with low hotel sales during off-season.

Topic: Mutuelle
Front: De quelles manières la part prise en charge par la mutuelle peut-elle être exprimée ?
Back:  <ul><li>En euros</li><li>En pourcentage de la BR</li><li>En pourcentage du PMSS ou PASS</li></ul>
```

Note what is absent: no bold, no emoji, no em dash, no topic prefix in the Front, no multi-paragraph
Back, no "Note that", no headers inside a field.

## The context field, precisely

The rule is about label prefixes, not about the word appearing at all. These three Fronts all sit on
notes whose `Tool` is `uv`, `Vim`, and `Dagster`, and all three are correct, because the subject is
part of the sentence rather than a heading bolted to the front of it:

```
What does the <code>--frozen</code> option do when using <code>uv run</code>?
What is the difference between a temporary setting and a permanent setting in Vim?
Which tool is used to quickly scaffold a Python package containing a Dagster <code>Definitions</code> object?
```

What is wrong is `"uv: what does --frozen do?"` or `"Sanofi R&D: which committee approves Gate 4?"`.
The reviewer reads the context line, then reads it again. Drop the prefix, keep the sentence natural.

## Length

The Back is normally one sentence. Two when the second earns its place, as in the Vim card above
where the contrast is the fact. Past roughly 200 characters, ask whether you are carding one fact or
several. Past 400, you almost certainly have a bundle: split it.

The Front is normally under 100 characters. Longer is acceptable only when the extra words remove a
genuine ambiguity, or when the card presents a concrete case to reason about.

## Steps

The limit is the count: a Back holds at most three steps. Four or more is more than one card,
whether written as a list or as a sentence, and the linter counts list items for that reason.

Two steps are one sentence, joined with "then":

```
Back:  Add the package to <code>packages.yml</code>, then run <code>dbt deps</code>.
```

Three steps are an `<ol>`. The numbers show the order and the count, so the reviewer knows how many
to recall and can check each one. Keep the items short and parallel, each opening with its verb.

Before, a real card from the collection:

```
Tool:  Snowflake
Front: How do you rotate a key held in a user's <code>RSA_PUBLIC_KEY</code> property?
Back:  <ol><li>Set the new key in <code>RSA_PUBLIC_KEY_2</code></li><li>Switch clients to the new private key</li><li><code>UNSET RSA_PUBLIC_KEY</code></li></ol>
```

After:

```
Back:  <ol><li>Set the new public key in <code>RSA_PUBLIC_KEY_2</code></li><li>Switch clients to the new private key</li><li>Run <code>UNSET RSA_PUBLIC_KEY</code></li></ol>
```

The third item was a bare command among instructions, and "new key" did not say which of the two
new keys goes in the property.

When the outline itself must be known, lay the procedure out as a cloze Text instead: one cloze per
`<li>`, each step cut to the words that matter, always in the same order so that the position
becomes part of the cue:

```
Topic: Networking
Text:  The TCP handshake: <ol><li>{{c1::SYN}}</li><li>{{c2::SYN-ACK}}</li><li>{{c3::ACK}}</li></ol>
```

Keep each deletion inside its own `<li>`. Anki parses cloze markers as text, so a deletion that runs
across `</li><li>` renders as broken HTML. Numbers tell the reader that the order matters, so a set,
a list of criteria, or two conditions that must both hold never goes in an `<ol>`.

## HTML

Anki fields hold HTML. Use it sparingly.

| Use | Do not use |
| --- | --- |
| `<code>` for identifiers, flags, paths, commands, field names | `<b>` or `<strong>` for emphasis |
| `<i>` for a term being defined or a foreign phrase | `<b>` to mark the answer inside the Back |
| `<ul><li>` for a closed list of two or three items | `<h1>` to `<h6>`, headings inside a field |
| `<ol><li>` for three ordered steps on a Back, or one cloze per item in a cloze Text | `<ol>` around items in no particular order, or for two steps |
| `<br>` to separate two short related lines | `<div>` wrappers added by hand |
| `<img src="...">` for a diagram that is the answer | Tables, unless the fact genuinely is a table |
| `&amp;`, `&lt;`, `&gt;` escaped correctly | Raw `&` or `<` in text |

The editor sometimes leaves `<div>` wrappers and `&nbsp;` in existing notes. Do not replicate those
deliberately, and do not go out of your way to strip them from notes you are not otherwise editing.

## Prose rules

Straight from the humanizer patterns, restricted to the ones that show up in card writing:

- No em dash. Use a comma, a period, or parentheses.
- No emoji anywhere. Source pages full of emoji headings get stripped, not mirrored.
- Straight quotes only, not curly.
- No bold for emphasis, and no bold-header bullet lists (`- **Thing:** explanation`).
- No significance inflation. Cut "plays a crucial role in", "is a key part of", "serves as".
  Write "is". A card that says a thing is important is not testing anything.
- No "-ing" tails bolted onto a sentence: "..., highlighting the importance of governance".
- No rule-of-three padding. Three items only when there are exactly three.
- No hedging. "may possibly indicate" is not a recallable answer. If the source hedges, say who
  hedges and how, or drop the card.
- No filler openers: "Note that", "It is important to note that", "Basically", "Essentially".
- Sentence case for anything heading-like.

## Tags

138 of the 158 tags in this collection are lowercase kebab-case. Match that. Examples in use:
`causal-inference`, `regime-social`, `browser-support`, `access-control`, `cdp-limitations`,
`abbreviation`, `config`, `exemple`.

Rules:

- Lowercase kebab-case. Not Title Case, not `snake_case`, and no `&`.
  `Sanofi`, `R&D`, `Governance`, `Organization` are all wrong here.
- Sparse. Many good notes carry zero topical tags because the deck and the Topic field already say
  what the card is about. Add a tag only when it expresses something the deck does not, typically a
  cross-cutting theme you would want to search on later.
- Exactly one source tag per card, naming where the fact came from. Format: a short slug for the
  source, for example `confluence-rcgrwe`, `supermemo-20-rules`, `uv-docs`. This is SuperMemo rule 18
  adapted to note types that have no Source field, and it is what makes a stale fact findable later.
- A card from client work also carries `client-<name>`, for example `client-sanofi` or
  `client-air-liquide`. It is not the source tag, which still names the document the fact came
  from. It keeps the client findable once the card leaves the Inbox, where a subdeck used to say it.
  A source tag that names a client's document, such as `air-liquide-iac-tencent`, stays a source
  tag, and the client tag goes beside it.
- Volatility goes in the card text, not the tag. Write "as of March 2026" in the Back or the cloze
  sentence, because tags are invisible during review.

Acronym tags that already exist in uppercase (`NYSE`, `PFU`, `EI`, `IS`, `TODO`) are the exception
that proves the rule. Do not add more.

## Language

Match the source and the deck. This collection has French cards under `Mutuelle`, `Freelance`,
`Bourse`, and `Fiscalité`, and English cards everywhere else. Do not translate a French source into
English cards, and do not mix languages inside one card except for a term of art.

French cards follow French typography, including the space before `?` and `:`.
