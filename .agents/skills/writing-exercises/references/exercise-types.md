# Exercise types

Most sets need only a handful of these, and each is a shape for a task from real work, not a drill. Build and extend items carry the project forward; the others make the learner think about what the tool does, which plain building rarely forces. An experienced developer gains most from predict, break, fix, compare and choose items aimed at where this tool differs from the ones they know, and least from fill-in-the-blank drills, unless the syntax itself is new.

There is no explain type. An answer that fits in a sentence is theory, and theory goes on a flashcard.

Every shape below is one or two short sentences, and its solution is one possible answer.

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

**Solution**: the build and run commands. The Dockerfile itself is in the commit.

## Extend

**When**: most of the set. The learner bends working code to new behaviour, which is how developers adopt a tool for real.

**Shape**: `Make <existing thing> <new behaviour>.`

> Return a 404 when the item does not exist.

**Solution**: the command that shows it, and the response.

## Predict, then run

**When**: the tool's semantics differ from what the learner expects, such as evaluation order, laziness, state, caching, or what a command changes. It is the cheapest way to expose a wrong mental model.

**Shape**: `Before <X>, predict <what you expect>.` The prediction must be specific enough to be wrong.

> Before amending the last commit, predict how many commits the log will show and whether the last hash changes.

**Solution**: the actual result first ("still three; the last hash changes"), then the reason ("amend replaces the commit rather than editing it").

## Break it on purpose

**When**: the tool's classic error is one the learner will meet at work and should recognise on sight.

**Shape**: `<Make the specific mistake>, read the error, then put it right.`

> Use a vector after moving it, read the compiler's error, then fix it.

**Solution**: the error's key lines and the usual fix. Keep the quoted error to the lines that matter.

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

**Solution**: the cause in one sentence. The fix itself is in the commit.

## Inspect

**When**: the tool keeps state or metadata the learner must learn to read, such as a plan, a state file, logs, a query plan or a lockfile.

**Shape**: `Using only <the tool>, find <a fact>.`

> Using only git, find which commit last changed a line of `README.md`.

**Solution**: the command, such as `git blame -L 12,12 README.md`, with the output that answers it.

## Compare two ways

**When**: the tool offers two approaches with different trade-offs, and choosing between them is the judgement the learner lacks. This reaches the expert's gap, which build items do not.

**Shape**: `<Do X> with <A>, then with <B>, and say when you would pick each.` Name the principle in the solution, after the learner has compared.

> Paginate the orders with an offset, then with a cursor, and say which one repeats an order created between two pages.

**Solution**: offset repeats one, because the new order shifts every row down by one; the cursor does not. Then the principle: a cursor names a position in the data, while an offset counts rows that can move.

## Swap behind the tests

**When**: the learner should see that a design survives a change of implementation, or should learn the tool's idiomatic version of something they wrote clumsily earlier.

**Shape**: `Replace <implementation> with <another> without touching the tests.`

> Replace the in-memory store with SQLite without touching the tests.

**Solution**: the commands, and what the change touched.

## Choose which

**When**: the learner knows two or more look-alike features. This item names none of them, so the learner must recognise which one applies, which is what work asks of them.

**Shape**: the goal only.

> Show each customer's latest order, one row per customer.

**Solution**: the construct that fits, and why the look-alike does not.

## Change the requirement

**When**: right after a build item, now and then. Real requirements shift, and the change shows whether the first design bends.

**Shape**: `<New fact>. Make <the earlier artefact> handle it.`

> Orders can now be partly refunded. Make the revenue report net of refunds.

**Solution**: what had to change.

## Same result, another interface

**When**: the tool has a UI and a CLI, or a CLI and an SDK, and the learner will use both.

**Shape**: `Create <the same artefact> again with <the other interface>.`

> Create the same bucket again with the CLI.

**Solution**: the commands, and any setting the UI chose silently that the CLI made explicit.

## Tear down

**When**: anything costs money or leaves state behind: cloud resources, containers, databases, global configuration.

**Shape**: `Destroy everything <scope> created.`

> Destroy everything this set created.

**Solution**: the commands, and where leftovers usually hide.

## Recall

**When**: at the end of a set, and when a learner returns to it on a later day.

**Shape**: `Without the docs, rebuild <X>, then compare with its commit.`

**Solution**: none beyond the pointer to the commit.

## Capstone

**When**: once, at the end. It integrates the core of the set in a task close to the learner's real use.

**Shape**: a goal and its constraints, in as few sentences as combining the core allows. It names no features.

**Solution**: the commands that build it, and one decision that matters. The code is in the commit.
