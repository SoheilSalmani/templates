# The research canon

Load this when a judgement call is genuinely unclear. The condensed rules in `SKILL.md` are the
operational form of what follows.

Sources:

- Piotr Wozniak, [Twenty rules of formulating knowledge](https://www.supermemo.com/en/blog/twenty-rules-of-formulating-knowledge), SuperMemo.
- Andy Matuschak, [How to write good prompts: using spaced repetition to create understanding](https://andymatuschak.org/prompts/).
- Andy Matuschak, [Important attributes of good spaced repetition memory prompts](https://notes.andymatuschak.org/z42J1vxsMjhkdbrqVfoqjiEesSzfaEqurBtoJ).

Behind the procedures section, read 2026-10-25:

- Trabasso and van den Broek (1985), [Causal thinking and the representation of narrative events](https://doi.org/10.1016/0749-596X(85)90049-X), Journal of Memory and Language.
- Hurlstone, Hitch and Baddeley (2014), [Memory for serial order across domains](https://pubmed.ncbi.nlm.nih.gov/24079725), Psychological Bulletin.
- Dunlosky, Hartwig, Rawson and Lipko (2011), [Improving college students' evaluation of text learning using idea-unit standards](https://pubmed.ncbi.nlm.nih.gov/20700858), Quarterly Journal of Experimental Psychology.
- Jansen (2014), [How bulleted lists and enumerations in formatted paragraphs affect recall and evaluation of functional text](https://doi.org/10.1075/idj.21.2.06jan), Information Design Journal.
- Mautone and Mayer (2001), Signaling as a cognitive guide in multimedia learning, Journal of Educational Psychology 93(2).
- Nielsen Norman Group, [7 Tips for Presenting Bulleted Lists in Digital Content](https://www.nngroup.com/articles/presenting-bulleted-lists/), and Google's [procedures style guide](https://developers.google.com/style/procedures).

## The five attributes

Matuschak's test for a prompt. Run a doubtful card against all five.

1. Focused. One detail. Too much detail in either the question or the answer produces a partial
   retrieval, which is a partial memory.
2. Precise. The question specifies exactly what is being asked for. Vague questions produce vague
   answers that do not reinforce anything in particular.
3. Consistent. The same answer every time. A prompt with several valid answers causes
   retrieval-induced forgetting: recalling one answer actively inhibits the others.
4. Tractable. You should be right about ninety percent of the time. A card you keep failing is not
   teaching you, it is churning.
5. Effortful. Retrieval, not inference. If the answer follows from the question by reasoning, you are
   practising reasoning and not building the memory.

Consistent and effortful pull against each other, and that tension is where most bad cards live. Add
enough context to force one answer, but not so much that the question's shape becomes the cue.

## Minimum information principle (SuperMemo 4)

Formulate the smallest piece of knowledge that stands on its own. Simple items get scheduled well by
the algorithm because performance on them is stable. Complex items produce partial recall, which the
scheduler cannot interpret, so they need redundant repetition at awkward intervals.

The canonical example is a "characteristics of the Dead Sea" card carrying location, depth, length,
salinity, and density at once. It becomes five cards, each of which the scheduler can then handle
independently, dropping the easy ones fast and drilling the hard one.

Practical consequence: cards are cheap. Matuschak puts the lifetime cost of a prompt at ten to thirty
seconds of review across its first year. Splitting one bad card into three good ones is close to free.
Write more cards than feels necessary, but only about material you actually care about.

## Sets, enumerations, and closed lists (SuperMemo 9 and 10)

Three distinct cases, three different treatments.

A set is an unordered group: "which countries are in the EU". Never card it directly. Listing members
in a different order each review has, in Wozniak's words, a disastrous effect on memory. Convert to
individual membership facts, or to the historical sequence that produced the set, or drop it.

An enumeration is ordered: steps in a process, a pipeline, a gate sequence. Better than a set because
the order forces a consistent traversal, but still hard. Wozniak's fix is overlapping cloze
deletions, so each card asks for one step in context rather than the whole chain. Anki's stock cloze
is the weaker form: each card blanks one step and shows all the others, later ones included. Hiding
the later steps would need a cloned Cloze note type styled through Anki's `.cloze-inactive` class,
and this collection has none, so do not promise that behaviour. Procedures get their own section
below.

A closed list has a fixed, small, known membership: the five R&D pillars, the four criteria for
selecting a country. Write one cloze card per member on a single note, so each member is retrieved
separately with the others visible as context. That is the one case where a multi-index cloze note is
the right answer.

An open list has no fixed membership: "examples of a design pattern", "functions this library
exposes". Do not write a fill-in-the-blank card. Instead write cards linking each instance to the
category, cards about the pattern the instances share, and a generative card asking for any example.

## Procedures

A procedure is an enumeration with a purpose, and the purpose decides what to card. Matuschak works
through a recipe in the prompts essay. A cloze per step over the full step list is "an awfully
unfocused prompt", so he cuts the procedure down instead:

1. Drop the steps anyone doing the task would infer. Of the recipe's four steps, "the first and
   fourth steps aren't worth writing prompts about."
2. Card the keywords: the verb, adverb, or quantity that is easy to get wrong.
3. Card the transitions: "conditions or heuristics describing when to move between verbs are
   important." In a key rotation, that is when the old key may be removed.
4. Card the why: "Explanation-type prompts are especially valuable when studying procedures."
5. Optionally, one card for the whole sequence. Wozniak grades a whole sequence next to the items
   that cover its parts (the EU example under rule 9), and lets poems stay whole "due to strong
   semantic connections" until you stumble, then splits them with cloze. Do the same: three steps
   at most, each leading to the next, and split the card when it starts to lapse.

When the outline itself must be known, Matuschak's list form is simpler: a numbered cloze, one index
per step, each step cut to its keywords, in a fixed order. "When each element has a consistent
(though arbitrary) location, you'll end up learning the list's visual 'shape'."

All of this is practitioner experience, and no controlled study compares procedure cards. Cognitive
science agrees with it indirectly. Story events on a causal chain are recalled better than dead ends
(Trabasso and van den Broek, 1985). Ordered recall degrades as a sequence grows, mostly by swapping
neighbouring items (Hurlstone, Hitch and Baddeley, 2014). Learners grading their own multi-part
answers often credit partial or wrong recall (Dunlosky and colleagues, 2011).

### Lists and sentences on the Back

No study compares list and sentence answers on flashcards. The sources agree on the count rather
than the markup: Wozniak treats every enumeration as hard, and
[Woehlke](https://www.lesswrong.com/posts/7Q7DPSk4iGFJd8DRk/an-opinionated-guide-to-using-anki-correctly)
puts the ceiling at "3 logical bullets". On format, they split by count:

- Two items read better as one line. Nielsen Norman Group: shorter lists "work better embedded in a
  sentence". Woehlke finds a two-bullet card "quicker to recall as one long bullet". The connective
  carries the order, as pointer words carried structure in Mautone and Mayer (2001).
- From three items, a numbered list. Nielsen Norman Group numbers a list when "the order or the
  final count" matters. Wozniak numbers his own sequence answer, "(1) France and (2) Germany, Italy
  and the Benelux", and in [knowledge structuring](https://super-memory.com/english/ol/ks.htm) finds
  that when enumerated items keep their order, "their spatial location will strongly be imprinted".
  Matuschak keeps lists in a fixed order so the reviewer learns their visual "shape". In Jansen
  (2014), bulleted lists improved recall of the items in three of five studies. Separate items also
  make it easy to check an answer one idea at a time, which cuts overconfident self-grading
  (Dunlosky and colleagues, 2011).
- The owner of this collection finds that the visible count helps recall.

The size problem is the count, not the markup. On 2026-10-25, 107 of the 291 current Q&A Backs
written as HTML lists held four or more items. The linter counts list items, so a long list is
flagged like a long sentence.

## Interference (SuperMemo 11)

Wozniak calls interference probably the single greatest cause of forgetting in a mature collection.
It is the failure mode of carding a source that presents many parallel items, which is exactly what
an org chart, an acronym glossary, or an API surface looks like.

Symptoms: you recall that there are six committees but cannot attach the right mandate to the right
acronym, and each review reinforces the confusion.

Countermeasures, in order of preference:

1. Card fewer of them. Six near-identical facts you half-remember are worth less than two you know.
2. Differentiate by content. Ask for the distinguishing property, not the label. "Which committee
   makes major investment decisions" separates cleanly from "which committee evaluates benefit and
   risk", where "what does PIC stand for" and "what does BRC stand for" do not.
3. Add a personal or concrete hook (rules 14 and 15), such as the one decision you actually saw a
   committee make.
4. Space the introduction. Card two today and two next week rather than six at once.

## Optimize wording (SuperMemo 12) and context cues (SuperMemo 16)

Every word in a card is read on every review, so redundant words have a recurring cost and no
benefit. The SuperMemo example compresses "What does GRE stand for in biochemistry?" to
`bioch: GRE`, moving the domain out of the question and into a context label.

This collection's note types implement that label as the `Topic` and `Tool` fields. Using them is not
optional politeness, it is the mechanism that lets Fronts stay short without becoming ambiguous.

## Legitimate redundancy (SuperMemo 17)

Redundancy does not contradict the minimum information principle when it encodes the same fact from a
genuinely different angle:

- Both directions of a pairing. Term to definition and definition to term. Use `c1` and `c2` on one
  cloze note.
- An explanation card alongside a fact card. What it is, and why it is that way.
- Intermediate steps of a derivation as their own cards.
- The same concept in a different representation, for example a formula and a graph.

Two cards asking the same question in slightly different words is not redundancy, it is waste, and it
creates the inconsistency problem from attribute 3.

## Prompt types beyond bare recall

Recall cards are the floor, not the ceiling. When the material is conceptual rather than factual,
reach for:

- Explanation. Why does this hold, how does the mechanism work.
- Application. Given this situation, what does this concept tell you to do.
- Connection. How does this relate to, differ from, or generalise something already known.
- Creative or generative. Produce a new example. The answer varies, so accept anything valid. Judge
  these against attribute 4 rather than 3.
- Salience. Keep an idea available at the moment it is relevant, by tying it to a decision you make.

## How much to card

Start at five to ten cards per article or chapter. Completionism is the failure mode: it drains the
motivation that the whole system depends on, and produces cards about material you do not care about,
which you will then fail and resent.

It is hard to write good cards on first exposure to unfamiliar material. For a difficult source, card
the basic factual scaffolding first, and write the conceptual cards on a second pass once you
understand it.

Delete cards you no longer care about. A card that survives only out of sunk cost is a tax.

## Sources and date stamps (SuperMemo 18 and 19)

Record where a fact came from, so you can verify it, judge its reliability, and update it when it
changes. Stamp anything volatile with a date or version: statistics with the year collected, software
behaviour with the version, org structures and prices with the date read.

In this collection, the source goes in a tag and the date goes in the visible card text, because tags
are not shown during review. See `house-style.md`.
