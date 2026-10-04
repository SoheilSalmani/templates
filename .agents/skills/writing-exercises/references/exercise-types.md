# Exercise types

Most sets need only a handful of these, and each is a shape for a task from real work, not a drill. Build and extend items carry the project forward; the others make the learner think about what the tool does, which plain building rarely forces. An experienced developer gains most from predict, break, fix, compare and choose items aimed at where this tool differs from the ones they know, and least from fill-in-the-blank drills, unless the syntax itself is new.

There is no explain type. An answer that fits in a sentence is theory, and theory goes on a flashcard.

## Contents

- Build
- Extend
- Predict, then run
- Break it on purpose
- Fix the bug
- Inspect
- Compare two ways
- Swap behind a check
- Choose which
- Change the requirement
- Same result, another interface
- Tear down
- Recall
- Capstone

## Build

**When**: a feature's first appearance, and the start of each new part of the project.

**Shape**: `<Create|Write|Add> <artefact> that <does what>. Check: <how it shows>.` Name the feature the first time, as the docs name it.

> Write a Dockerfile for `app.py` that serves it with Python 3.12 on port 8000. Check: after `docker run -p 8000:8000 <image>`, `curl localhost:8000/health` prints `ok`.

**Solution**: the build and run commands, and the output. The Dockerfile itself is in the commit.

## Extend

**When**: most of the set. The learner bends working code to new behaviour, which is how developers adopt a tool for real.

**Shape**: `Make <existing thing> <new behaviour>. Check: <observable difference>.`

> Make `GET /items/{id}` answer 404 with `{"detail": "Item not found"}` when the item does not exist. Check: `curl -i localhost:8000/items/999` shows `404 Not Found` and that body.

**Solution**: the command, and the response that confirms it.

## Predict, then run

**When**: the tool's semantics differ from what the learner expects, such as evaluation order, laziness, state, caching, or what a command changes. It is the cheapest way to expose a wrong mental model.

**Shape**: `Before running <X>, write down <what you expect>. Check: run it, and compare with what you wrote.` The prediction must be specific enough to be wrong.

> On a branch with three commits, write down how many commits `git log --oneline` will show after `git commit --amend -m "Fix typo"`, and whether the last hash will change. Check: run it, and compare with what you wrote.

**Solution**: the actual result first ("still three; the last hash changes"), then the reason ("amend replaces the commit rather than editing it"), then the tempting wrong answer and why it is wrong.

## Break it on purpose

**When**: the tool's classic error is one the learner will meet at work and should recognise on sight.

**Shape**: `<Make the specific mistake>, read the error, then put it right. Check: <the error names X>.`

> In `main.rs`, use `v` after passing it to `consume(v)`. Build, and read the error before fixing it. Check: the compiler reports `E0382`, pointing at both the move and the later use.

**Solution**: the error's key lines, what they mean, and the usual fixes. Keep the quoted error to the lines that matter.

## Fix the bug

**When**: reading and diagnosis matter, or the learner should meet a classic misuse in someone else's code. Finding a bug is the hard part; fixing it once found usually is not.

**Shape**: the buggy code is input, given inline or in the setup commit. `<What goes wrong>. Fix it so that <correct behaviour>. Check: <proof>.`

> `add_tag(tag, tags=[])` keeps the tags from earlier calls. Fix it so that every call without `tags` starts from an empty list. Check: `add_tag("a")` then `add_tag("b")` return `['a']` and `['b']`.

**Solution**: the cause in one sentence, then the commands that confirm the fix. The fix itself is in the commit.

## Inspect

**When**: the tool keeps state or metadata the learner must learn to read, such as a plan, a state file, logs, a query plan or a lockfile.

**Shape**: `Using only <the tool's own commands>, find <a fact>. Check: <how to confirm it another way>.`

> Using only git, find which commit last changed line 12 of `README.md`. Check: `git show` on that commit includes the change to that line.

**Solution**: the command, `git blame -L 12,12 README.md` here, with the output that answers it.

## Compare two ways

**When**: the tool offers two approaches with different trade-offs, and choosing between them is the judgement the learner lacks. This reaches the expert's gap, which build items do not.

**Shape**: `<Do X> with <A>, then with <B>. In one sentence, say when you would pick each.` Name the principle in the solution, after the learner has compared.

> Paginate `GET /orders`, newest first, with offset and limit, then with a cursor. With each version, create a new order between fetching page 1 and page 2. Check: one version repeats an order on page 2; write down which before you try, then see.

**Solution**: offset repeats one, because the new order shifts every row down by one; the cursor does not, because it continues after the last order seen. Then the principle: a cursor names a position in the data, while an offset counts rows that can move.

## Swap behind a check

**When**: the learner should see that a design survives a change of implementation, or should learn the tool's idiomatic version of something they wrote clumsily earlier.

**Shape**: `Replace <implementation> with <another> without changing <the tests or the output>. Check: <the same check still passes>.`

> Replace the in-memory store with SQLite without editing a test. Check: `pytest` still passes.

**Solution**: the commands, and what the change touched and did not touch.

## Choose which

**When**: the learner knows two or more look-alike features. This item names none of them, so the learner must recognise which one applies, which is what work asks of them.

**Shape**: the goal only, plus a check.

> Show each customer's most recent order, one row per customer. Choose the construct yourself. Check: a customer with three orders appears once, with the latest date.

**Solution**: the construct that fits, why the look-alike does not, and the result.

## Change the requirement

**When**: right after a build item, now and then. Real requirements shift, and the change shows whether the first design bends.

**Shape**: `The requirement changes: <new fact>. Make <the earlier artefact> handle it. Check: <proof>.`

> Orders can now be partly refunded. Make the revenue report from exercise 9 show revenue net of refunds. Check: an order of 100 with a refund of 30 adds 70.

**Solution**: what had to change, and what a better first design would have left untouched.

## Same result, another interface

**When**: the tool has a UI and a CLI, or a CLI and an SDK, and the learner will use both.

**Shape**: `Create <the same artefact> again, this time <using the other interface>.`

> Create a second bucket with the AWS CLI, with the same settings as the one you made in the console. Check: `aws s3 ls` lists both.

**Solution**: the commands, and any setting the UI chose silently that the CLI made explicit.

## Tear down

**When**: anything costs money or leaves state behind: cloud resources, containers, databases, global configuration.

**Shape**: `Destroy everything <scope> created. Check: <proof that nothing is left>.`

> Destroy everything this set created. Check: `terraform state list` prints nothing.

**Solution**: the commands, and where leftovers usually hide.

## Recall

**When**: at the end of a set, and when a learner returns to it on a later day.

**Shape**: `Without the docs or your earlier commits, <rebuild X> in an empty directory. Check: <its original check>, then compare with the Exercise N commit.`

**Solution**: none beyond the pointer to the commit.

## Capstone

**When**: once, at the end. It integrates the core of the set in a task close to the learner's real use.

**Shape**: a goal, the inputs, the constraints, and an acceptance check, as short as combining the core allows. It names no features.

**Solution**: the acceptance commands and their output. The code is in the commit.
