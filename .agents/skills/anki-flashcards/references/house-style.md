# House style for card text

Derived from real cards, plus the writing rules from the `humanizer` skill.
Cards are prose that gets read hundreds of times, so the writing rules matter more here than in
ordinary text, not less.

## Real cards

These are verbatim. They are the target.

```
Topic: uv
Front: What does the <code>--frozen</code> option do when using <code>uv run</code>?
Back:  Run without updating the lockfile.

Topic: Vim
Front: What is the difference between a temporary setting and a permanent setting in Vim?
Back:  A temporary setting (e.g., <code>:set number</code>) is lost when Vim closes. A permanent setting is written to vimrc and persists across sessions.

Topic: Dagster
Front: Which tool is used to quickly scaffold a Python package containing a Dagster <code>Definitions</code> object?
Back:  The <code>create-dagster</code> CLI.

Topic: Bot Detection
Front: Which tool uses the WebDriver protocol?
Back:  Selenium WebDriver.

Topic: Causal Inference
Front: Why can ML models not answer causal questions?
Back:  ML is about prediction and correlation, not causal structure. It cannot handle inverse causality, like low prices being associated with low hotel sales during off-season.

Topic: Finances publiques
Front: Qu'est-ce que les finances sociales ?
Back:  Ensemble des dépenses liées à la protection sociale et des ressources nécessaires à leur financement.
```

Note what is absent: no bold, no emoji, no em dash, no topic prefix in the Front, no multi-paragraph
Back, no "Note that", no headers inside a field.

## The context field, precisely

The rule is about label prefixes, not about the word appearing at all. These three Fronts all sit on
notes whose `Topic` is `uv`, `Vim`, and `Dagster`, and all three are correct, because the subject is
part of the sentence rather than a heading bolted to the front of it:

```
What does the <code>--frozen</code> option do when using <code>uv run</code>?
What is the difference between a temporary setting and a permanent setting in Vim?
Which tool is used to quickly scaffold a Python package containing a Dagster <code>Definitions</code> object?
```

What is wrong is `"uv: what does --frozen do?"` or `"Acme R&D: which committee approves Gate 4?"`.
The reviewer reads the context line, then reads it again. Drop the prefix, keep the sentence natural.

The line is read before the question, so it is part of the cue: it never holds an answer, and two
cards never differ by the line alone. How to pick its value is in `note-types.md`, "Choosing the
context value".

## Length

The Back is normally one sentence. Two when the second earns its place, as in the Vim card above
where the contrast is the fact. Past roughly 200 characters of prose, ask whether you are carding one
fact or several. Past 400, you almost certainly have a bundle: split it. Code is counted in lines
instead: one when it can be, up to six for lines that belong together, up to twelve for a task card
ending in a `Check:` line (see Code below).

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

Before, a real card:

```
Topic: Snowflake
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

## Code

Pick the form by what the user will do with the code:

| The user will | Front | Back |
| --- | --- | --- |
| Type it | The goal, with the names and values the code needs | The code: one line when it can be, up to six when the lines belong together |
| Write it for a task, a pattern, or an example | The task: the setting, the names, what the code must do, or "of your choice" | One solution, at most twelve lines, then a `Check:` line naming what every correct answer contains |
| Read it | A short snippet, asking what it returns, what it is for, or which line is wrong | The value, the purpose in one sentence, or the line and why |
| Recognise its key line | The snippet as a cloze Text, with the line that matters blanked | None, it is a cloze |
| Decide with it | Why it is built this way, what must hold, what breaks | One reason, in one sentence |

Real cards, the target:

```
Topic: JavaScript
Front: How do you add or update a value in a <code>Map</code>?
Back:  <pre><code>map.set(key, value);</code></pre>

Topic: Helm
Front: Which command prints the Kubernetes manifests a deployed release was rendered into?
Back:  <code>helm get manifest &lt;release&gt;</code>.
```

Drop the period after the second when you next edit it: after a command, a period reads as part of
the command. In the review data in `principles.md`, one-line code answers were the best-kept cards
and long code Backs among the costliest.

Before, a real card:

```
Topic: React
Front: Write an example of a component that uses <code>useMemo()</code>.
Back:  <pre><code>import { useMemo } from 'react';

function TodoList({ todos, tab }) {
  const visibleTodos = useMemo(
    () =&gt; filterTodos(todos, tab),
    [todos, tab]
  );
  // ...
}</code></pre>
```

Asking for the component is not the problem. The card sets no task and says nothing about what
counts as right, so the review compares yours by eye with nine lines someone else chose. Two fixes
keep the code. If the call is what the user keeps forgetting, card the call:

```
Topic: React
Front: Which call caches the result of <code>filterTodos(todos, tab)</code> between renders?
Back:  <code>useMemo(() =&gt; filterTodos(todos, tab), [todos, tab])</code>
```

The dependency list is part of the answer, and only one is right: every reactive value the
calculation reads. If writing the component is the point, keep the task and say what counts:

```
Topic: React
Front: Write a component <code>TodoList({ todos, tab })</code> that computes <code>filterTodos(todos, tab)</code> only when its inputs change.
Back:  <pre><code>function TodoList({ todos, tab }) {
  const visibleTodos = useMemo(
    () =&gt; filterTodos(todos, tab),
    [todos, tab]
  );
  // ...
}</code></pre>Check: <code>useMemo</code> takes a function that makes the call, and the dependency list is <code>[todos, tab]</code>.
```

Both are field edits to the old card, so either keeps its review history. A Front may also leave the
example open, as in "Write a generator-based context manager for a resource of your choice", when
the Check line names what every correct one contains. Any answer that meets it passes, and the user
writes a different one each time, which keeps the card from turning into recall of one text.

A scenario is a task with its data on the Front, the form closest to work:

```
Topic: PostgreSQL
Front: Table <code>weather_reports(location, time, report)</code>. Write the query that returns the latest report for each location, with <code>DISTINCT ON</code>.
Back:  <pre><code>SELECT DISTINCT ON (location) location, time, report
FROM weather_reports
ORDER BY location, time DESC;</code></pre>Check: <code>DISTINCT ON (location)</code>, <code>ORDER BY</code> starting with <code>location</code>, then <code>time DESC</code>.
```

The Front names `DISTINCT ON` because that is what the card trains; without it, a correct query with
a window function would fail the Check line. When the Check line can only describe the result, the
user runs the answer to grade it.

Twins are the other common waste. One collection held six pairs of Snowflake Scripting blocks, one
"that can be run in Snowsight" and one for the Snowflake CLI or the Python connector. Within a pair
the code is the same apart from the wrapper the CLI needs, so twelve cards of 5 to 15 lines test one
fact. Card the difference and its reason:

```
Topic: Snowflake Scripting
Front: How do you run an anonymous block from the Snowflake CLI or the Python connector's <code>execute_string()</code>?
Back:  Pass it to <code>EXECUTE IMMEDIATE</code> as a string literal: <code>EXECUTE IMMEDIATE $$ ... $$</code>.

Topic: Snowflake Scripting
Front: Why must the Snowflake CLI receive a Snowflake Scripting block as a string literal?
Back:  It does not parse Snowflake Scripting blocks correctly, as of November 2026.
```

A code cloze blanks the line or token that matters, inside a snippet cut to what the blank needs.
Code carries two characters that Anki's cloze syntax claims. A real card:

```
Topic: Rust
Text:  Only types that {{c1::implement <code>fmt::Display</code>}} can be formatted with <code>{{c2::{}}}</code>.
```

Anki reads whatever follows a `::` inside a deletion as a hint, so the first card shows "Display"
as the hint of its own blank and its answer stops at "implement fmt". A deletion also ends at the
first `}}`, so the second card's answer is `{` and the closing brace stays in plain sight. An empty
HTML comment between the characters fixes both and renders as nothing:

```
Text:  Only types that {{c1::implement <code>fmt:<!-- -->:Display</code>}} can be formatted with <code>{{c2::{}<!-- -->}}</code>.
```

Rust and C++ paths, Jinja, Helm and Go templates, JavaScript objects, and format strings all hit
this. The linter catches both.

A pattern the user writes again and again earns the longest Back, up to twelve lines. A context
manager written as a generator, as a task card:

```
Topic: Python
Front: Write a generator-based context manager <code>timed</code> that prints how long its block took, even when the block raises.
Back:  <pre><code>@contextmanager
def timed():
    start = time.perf_counter()
    try:
        yield
    finally:
        print(time.perf_counter() - start)</code></pre>Check: setup before <code>yield</code>, <code>yield</code> inside <code>try</code>, cleanup in <code>finally</code>.
```

The Front fixes the names and the behaviour, so one solution is right, and the Back holds nothing
incidental: no imports, no usage. The `Check:` line names what the review is graded on, because
someone grading a long answer from memory credits most near misses. When you show a task card, tell
the user how to review it: write the answer out, on paper or in an editor rather than in their
head, before revealing it; grade it against the Check line, not against the solution shown, so a
different correct answer passes; press Again when any part on the Check line is missing; and run it
when only running it would tell.

The task card is the integrative card. The cards it cannot hold come first: when to reach for the
pattern, and the part people get wrong.

```
Topic: Python
Front: Why does a generator-based context manager put its <code>yield</code> inside <code>try</code>?
Back:  An exception in the <code>with</code> block is raised at the <code>yield</code>, so only a <code>finally</code> still runs the cleanup.
```

For a design pattern such as Strategy or Builder, keep the problem it answers and what it costs
against the simpler alternative as prose, and the way the user's language writes it as code, which
is often shorter than the book's: a Python strategy is usually a function passed as an argument.
Write task cards for the patterns the user actually writes, two or three in different situations
when the pattern matters, and a card that gives a situation and asks which pattern fits, since
choosing the pattern is a skill of its own.

## HTML

Anki fields hold HTML. Use it sparingly.

| Use | Do not use |
| --- | --- |
| `<code>` for identifiers, flags, paths, commands, field names | `<b>` or `<strong>` for emphasis |
| `<i>` for a term being defined or a foreign phrase | `<b>` to mark the answer inside the Back |
| `<ul><li>` for a closed list of two or three items | `<h1>` to `<h6>`, headings inside a field |
| `<ol><li>` for three ordered steps on a Back, or one cloze per item in a cloze Text | `<ol>` around items in no particular order, or for two steps |
| `<br>` to separate two short related lines | `<div>` wrappers added by hand |
| `<pre><code>` for more than one line of code | A whole program on a Back |
| `<img src="...">` for a diagram that is the answer | Tables, unless the fact genuinely is a table |
| `&amp;`, `&lt;`, `&gt;` escaped correctly, inside code too | Raw `&` or `<` in text or code |

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

## Source

Every card on the skill's note types says where its fact came from, so that the fact can be
checked, judged, and updated when the page changes (SuperMemo rule 18). The note type shows the
`Source` under the answer, in small type, and it is never part of what is recalled.

- A link to the exact page, with the page title as the link text. If the link dies, the title still
  says what it was:
  `<a href="https://docs.snowflake.com/en/user-guide/key-pair-auth">Snowflake docs: Key-pair authentication</a>`.
- Plain text when the source has no URL: a book and its chapter, a talk, or
  `Conversation, 12 November 2026`. Never guess an address.
- Every card from one page carries the same `Source`. `"source:*docs.snowflake.com*"` finds every
  card from that site, and `source:` with nothing after it finds the cards that have none.
- From a repository, link the file on its forge, under the repository's own address, as
  `remembering-what-you-built` describes.

Volatility goes in the card text, not in the `Source`. Write "as of March 2026" in the Back or the
cloze sentence: the `Source` says where a fact came from, not how long it holds.

## Tags

Tags are for what no field and no note type says. The skill writes one, and a rule decides it, not
taste.

`speed::fast` goes on every card that is quick to review by its shape, and on no other. A review
is reading the question, recalling, reading the answer and grading it, so a card is quick when there
is little to read and little to produce:

- each card's answer is at most 3 words and 30 characters: a Back, the text of one cloze index, or
  the keys of a `Keyboard Shortcut` card, which always count as short;
- the question is at most 100 characters, and a cloze sentence at most 120 with its blanks filled;
- neither side holds a list, a code block, a table or an image.

A reversed note asks each side for the other, so both sides must be short. The linter applies the
rule to every draft, so a card asked to be tagged fast that the rule does not mark stays untagged,
and the response says why. A filtered deck searching `tag:speed::fast is:due` makes a queue of quick
reviews. Answer times would not do instead: a single card's are noisy (`principles.md`, "Tags").

Nothing else is a tag:

- The subject is the `Topic`.
- Where the fact came from is the `Source`.
- The kind of card is its note type: `note:"Keyboard Shortcut"` finds every shortcut.
- The project a card is learnt for is its `Inbox::<project>` deck, until the card moves on.
- A card to fix gets marked during review, the `*` key, which the repair queue's `failing` check
  picks up.

Anki writes `leech`, `marked`, `duplicate` and `db-check` itself. Never add one, and remove `leech`
only as part of a fix the user approved. Any other tag already in a collection is the user's: leave
it unless asked to clean up.

## Language

Match the source: a French source gets French cards. Do not translate a French source into English
cards, and do not mix languages inside one card except for a term of art.

French cards follow French typography, including the space before `?` and `:`.
