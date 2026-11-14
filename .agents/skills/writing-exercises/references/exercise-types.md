# Exercise types

Most sets need only a handful of these, and each is a shape for a task from real work, not a drill. Build and extend items carry the project forward; the others make the learner think about what the tool does, which plain building rarely forces. An experienced developer gains most from predict, break, fix, compare and choose items aimed at where this tool differs from the ones they know, and least from fill-in-the-blank drills, unless the syntax itself is new.

There is no explain type. An answer that fits in a sentence is theory, and theory goes on a flashcard.

Every shape below is one or two short sentences. Its answer is one possible `Exercise N` commit, and its `Solution` block holds only what the diff cannot show: the commands, and a result in a few words. Why the answer is what it is never goes in the block; it is a flashcard.

## Contents

- Build
- Extend
- Predict, then run
- Break it on purpose
- Fix the bug
- Inspect
- Compare two ways
- Swap behind the tests
- Choose which
- Change the requirement
- Same result, another interface
- Tear down
- Recall
- Capstone

## Build

**When**: a feature's first appearance, and the start of each new part of the project.

**Shape**: `<Create|Write|Add> <artefact> that <does what>.` Name the feature the first time, as the docs name it.

> Containerise the app.

**Answer**: the Dockerfile, in the commit. The block: the build and run commands.

## Extend

**When**: most of the set. The learner bends working code to new behaviour, which is how developers adopt a tool for real.

**Shape**: `Make <existing thing> <new behaviour>.`

> Return a 404 when the item does not exist.

**Answer**: the change, in the commit. The block: the command that shows the new behaviour.

## Predict, then run

**When**: the tool's semantics differ from what the learner expects, such as evaluation order, laziness, state, caching, or what a command changes. It is the cheapest way to expose a wrong mental model.

**Shape**: `Before <X>, predict <what you expect>.` The prediction must be specific enough to be wrong.

> Before amending the last commit, predict how many commits the log will show and whether the last hash changes.

**Answer**: the result, in the block: "Still three; the last hash changes." The reason, that amend replaces the commit, is a flashcard.

## Break it on purpose

**When**: the tool's classic error is one the learner will meet at work and should recognise on sight.

**Shape**: `<Make the specific mistake>, read the error, then put it right.`

> Use a vector after moving it, read the compiler's error, then fix it.

**Answer**: the fix, in the commit. The block: the error's key line, so the learner knows they broke it the expected way.

## Fix the bug

**When**: reading and diagnosis matter, or the learner should meet a classic misuse in someone else's code. Finding a bug is the hard part; fixing it once found usually is not.

**Shape**: `<What goes wrong>. Fix it.`, with the buggy code as fenced material or in the setup commit.

> This function keeps the tags from earlier calls. Fix it.
>
> ```python
> def add_tag(tag, tags=[]):
>     tags.append(tag)
>     return tags
> ```

**Answer**: the fix, in the commit, with no block. The cause is a flashcard.

## Inspect

**When**: the tool keeps state or metadata the learner must learn to read, such as a plan, a state file, logs, a query plan or a lockfile.

**Shape**: `Using only <the tool>, find <a fact>.`

> Using only git, find which commit last changed a line of `README.md`.

**Answer**: no commit. The block: the command, such as `git blame -L 12,12 README.md`, and the fact it finds.

## Compare two ways

**When**: the tool offers two approaches with different trade-offs, and choosing between them is the judgement the learner lacks. This reaches the expert's gap, which build items do not.

**Shape**: `<Do X> with <A>, then with <B>, and find which one <behaves some observable way>.` The principle behind the difference is a flashcard, never part of the item.

> Paginate the orders with an offset, then with a cursor, and say which one repeats an order created between two pages.

**Answer**: both ways, in the commit, and the result in the block: "The offset repeats it." The principle, that an offset counts rows that can move, is a flashcard.

## Swap behind the tests

**When**: the learner should see that a design survives a change of implementation, or should learn the tool's idiomatic version of something they wrote clumsily earlier.

**Shape**: `Replace <implementation> with <another> without touching the tests.`

> Replace the in-memory store with SQLite without touching the tests.

**Answer**: the new implementation, in the commit, whose diff shows what the change touched. The block: the test command.

## Choose which

**When**: the learner knows two or more look-alike features. This item names none of them, so the learner must recognise which one applies, which is what work asks of them.

**Shape**: the goal only.

> Show each customer's latest order, one row per customer.

**Answer**: the commit, built with the construct that fits, and no block. Why the look-alike does not fit is a flashcard.

## Change the requirement

**When**: right after a build item, now and then. Real requirements shift, and the change shows whether the first design bends.

**Shape**: `<New fact>. Make <the earlier artefact> handle it.`

> Orders can now be partly refunded. Make the revenue report net of refunds.

**Answer**: the commit; its diff is what had to change.

## Same result, another interface

**When**: the tool has a UI and a CLI, or a CLI and an SDK, and the learner will use both.

**Shape**: `Create <the same artefact> again with <the other interface>.`

> Create the same bucket again with the CLI.

**Answer**: the commands, in the block. A setting the UI chose silently is a flashcard.

## Tear down

**When**: anything costs money or leaves state behind: cloud resources, containers, databases, global configuration.

**Shape**: `Destroy everything <scope> created.`

> Destroy everything this set created.

**Answer**: the commands, in the block, leftovers included.

## Recall

**When**: at the end of a set, and when a learner returns to it on a later day.

**Shape**: `Without the docs, rebuild <X>, then compare with its commit.`

**Answer**: the commits it rebuilds; no block.

## Capstone

**When**: once, at the end. It integrates the core of the set in a task close to the learner's real use.

**Shape**: a goal and its constraints, in as few sentences as combining the core allows. It names no features.

**Answer**: the code, in the commit. The block: the commands that build and run it.
