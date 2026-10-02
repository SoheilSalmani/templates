---
name: writing-exercises
description: "Writes practice exercises to learn a software tool, framework, library or language fast, or to check that the learner masters the features a codebase uses before working on it, in the activities format: a README of numbered real-world tasks, each with a check the learner can run, hidden `<details>` solutions, and one `Exercise N` commit per answer. Checks the Anki collection and existing exercise sets first, sends theory to flashcards, and writes exercises only for practice that is missing. Use when asked to write, extend, review or fix exercises or activities for learning something, to turn a tutorial, course, book or docs into exercises, to check readiness for a repository's stack, to write an activities README's missing statements from its commits, or to write an exercise's reference solution. Not for writing the flashcards, which anki-flashcards owns, or for tutorials and how-to guides, which writing-documentation owns."
---

# Writing exercises

An exercise is one attempt with a check. The learner reads a goal, produces the answer from memory and the docs, runs a check that says whether it works, and only then opens the solution to compare. Every rule below protects a part of that loop: the goal must not give the answer away, the check must not need the solution, and the solution must teach what the check cannot. Exercises are for doing; what only needs remembering goes on flashcards.

**When rules conflict, the earlier one wins: correct, then needed, then produced by the learner, then checkable, then short.** A wrong exercise is the worst kind: a learner who follows it exactly and fails concludes that they are the problem. An unneeded one spends the time the set exists to save.

## Scope

Two kinds of set:

- **Learning a tool**, framework, library or language. The target is what the learner wants to do with it.
- **Readiness for a codebase.** The target is the features a repository's code relies on, and the set checks that the learner masters them before working there.

Also in scope: more exercises for an existing set; reviewing or repairing one; turning a tutorial, course or docs into exercises; writing the statements an activities README is missing, from its `Exercise N` commits; and an exercise's reference solution, when asked.

Out of scope, and say so: writing the flashcards, which `anki-flashcards` owns once this skill has said what belongs on them; tutorials, how-to guides and reference docs, which `writing-documentation` owns; quizzing someone live; assessments that rank people; explaining the codebase itself.

## Exercise, flashcard, or nothing

Sort every candidate concept before writing anything, after checking two stores: the Anki collection, and the learner's existing sets with their `Exercise N` commits.

- **Theory goes on a flashcard, never into an exercise**: a definition, a rule, a default, a name, a syntax form, a trade-off stated in a sentence. Skip it when the collection already cards it; otherwise list it for `anki-flashcards`, which drafts the cards and asks before adding them.
- **Practice gets an exercise**: writing code with a feature, operating the tool, finding a bug, choosing under real constraints. Skip it when an exercise the learner has done already practises it.
- **Anything the target does not need, or the codebase barely uses, gets nothing.**

`references/coverage.md` has the searches for both stores and the full decision table; read it before writing or extending a set. The reply says what each concept became and why, and names any store it could not check.

## Before writing

1. **Read what exists.** In an existing set, read the whole README and `git log --reverse --format='%h %s'`: which items have an `Exercise N` commit, which are still `TODO`, which source each section follows. The learner's other sets, directories named `*-activities`, show what they already know.
2. **Pin the subject**: the tool and its version, or the codebase's stack and its versions, and the tutorial, course or book if the learner follows one. Read the official docs for every part you will use. **Never write a command, flag, API or output you have not read in the docs or run.** Record the version and the date.
3. **Know the learner**: what they already use, and what they want this for. Infer it from the request and their sets, and ask only when the target is unknown and would change the set. By default the learner is an experienced developer, so skip programming basics and spend the guidance on what is new.
4. **Write the target in one sentence**: what the learner can do at the end without looking anything up. Every exercise serves it.

## Readiness for a codebase

The set checks the features the code relies on, not the codebase itself. Inventory the stack from the manifests and the features from the code, keep what is used often, sits in the core path, or is hard to read without knowing it, and write generic exercises on those.

- **Nothing from the repository goes into the set**: no code, names, domain terms, data or secrets. The set may be public, and the repository may be a client's.
- **The set goes into the learner's activities, never into the repository**: into the set for the language or framework, as a part named after the features.

Read `references/codebase.md` for any readiness set: it has the inventory method, with Rust worked through.

## Choosing what to practise

List the core model, meaning the few nouns the tool is built from and what it does with them when it runs; the day-one loop of install, run, inspect, undo, read an error and find the right page of the docs; the operations real work uses most; the traps, such as the classic mistake, the confusing error and the false friend that looks like something the learner knows and behaves differently; and the look-alikes, such as `count` and `for_each`. Keep only what the target needs; a link in Resources is enough for the rest. Most first sets need 10 to 20 exercises. More is a second set, not a longer one.

Then **write the capstone first**: a realistic task that an hour or two can finish, built from the core of the list. Work backwards from it, so that each exercise adds a piece the capstone needs, and grow **one small project on one dataset** across the set, from inputs that will not vanish.

## Ordering

- **Exercise 1 installs what the set needs and ends in a visible result within minutes.** Give the install command even when this machine has the tool; the learner may be on another.
- **At most one concept new to the learner per exercise.** A real task often needs several concepts, and those the learner knows cost nothing; two new ones at once turn a failure into a guess about which went wrong. A readiness set assumes the learner knows them all, so its items combine them the way the codebase does.
- **Each exercise uses only what came before**, and starts from the state the previous one left.
- **Name a feature the first time it is the target, then stop naming it.** Later items that need it give only the goal, so that using it is recall. Once two look-alikes are both known, one item names neither and makes the learner choose.
- **Guide first or attempt first, by what the learner could work out.** A convention nobody could guess, such as a magic file name, is named and linked. Behaviour the learner can reason about is a prediction to make before running anything.
- **Bring every core idea back at least twice, unannounced**, with a different input each time. About every five exercises, a **review** item combines earlier ideas on new input, with no hint.
- **Now and then, change a requirement on code the learner just wrote**, as real work does.
- **Tear down** anything that costs money or leaves state behind, as its own exercise.
- **End with the capstone**, which names no features. Where the learner schedules exercise reviews in Anki, propose review notes for the set's parts; otherwise add one **recall** item for a later day: rebuild a core piece without the docs, then compare it with its commit.

## Writing an exercise

The shape is `N. <Verb> <outcome>, <inputs and constraints>. Check: <how the learner tells it works>.`

- **A task from real work.** Every item is something a developer does with the tool on a job: build a feature, fix a failing job, move data, speed up a query. Never a toy that runs a feature for no purpose.
- **State the outcome, not the steps.** Never put the answer's code in the prompt, and never turn a tutorial's "copy this" into an exercise. Code belongs in a prompt only as material: data to load, a snippet to predict, a bug to fix. Setup that the set does not teach may be given openly.
- **Make it concrete**: real names for files, tables, routes and resources; inputs inline or linked; numbers and boundaries stated, such as "strictly more than 5 words".
- **End with a sentence starting `Check:` that the learner can run alone**: a command and what it prints, a test that turns green, a behaviour to observe. A predict item's check is to run the thing and compare with what they wrote down. Anything to undo goes in the same sentence, so the check stays last.
- **Put every fact the task depends on in the item.** Learners skim, and a constraint stated three items earlier gets missed.
- **One outcome per item.** An outcome and its check are one.
- **Block the shortcut** that would skip the point: "without editing the test", "using only the CLI", "in one query".
- **Size each item for 5 to 15 minutes.** Only the capstone takes longer.
- **Keep the state straight.** Every name an item uses exists by then, and its solution uses the same names.
- **Mix the types**: build, extend, predict then run, break it on purpose, fix a bug, inspect, compare two ways, swap behind a check, choose which. Aim the predict and break items at the traps. `references/exercise-types.md` gives each type's shape, check and solution; read it when planning a set.
- **Use plain words.** No "just", "simply", "easy", "experiment with" or "explore"; no item that is only a noun, such as "Cards."; no "same but…", which hides the task in the previous item; no "test X" that does not say what to look for.

A recipe step, before:

```markdown
6. Update the AMI ID to `ami-08d70e59c07c61a3a`.
```

After, the same change becomes a prediction that the plan settles:

````markdown
6. Change the instance's AMI to `ami-08d70e59c07c61a3a`. Before you apply, write down whether Terraform will update the instance in place or replace it. Check: run `terraform plan` and find the line that settles it.

   <details>
     <summary>Solution</summary>

   It replaces it. The plan marks the instance `-/+` and flags the AMI:

   ```text
   ~ ami = "ami-830c94e3" -> "ami-08d70e59c07c61a3a" # forces replacement
   ```

   A new AMI means a new machine, so anything stored only on the old instance is gone after the apply.

   </details>
````

`references/worked-examples.md` rewrites more real exercises and names each one's defect. Read it before reviewing a set, or when a rule here feels abstract.

## Solutions

- **The check sits in the item, outside any `<details>` block**, so the learner can verify without opening the solution.
- **The `Solution` block holds what the answer commit cannot show**: commands, console or UI steps, queries typed into a console, the expected output, the answer to a predict or compare item, and, in a sentence or two, why the answer is right and which wrong turn a learner is likely to take.
- **Code that lands in a file belongs in the `Exercise N` commit**, not in the block. An exercise that changes no file has no commit.
- **A `Hint` block comes before the solution** where the likely obstacle is finding the feature or reading an error. It points at the doc page or quotes the error, and never contains the answer. Review, recall and capstone items get no hint.
- **Verify every solution.** Run it in a scratch directory outside the learner's repository when the tool runs locally; otherwise check each command, flag and API against the docs for the pinned version. Say which items ran and which were only checked. A solution that contradicts its item, boundary included, is a broken exercise, not a detail.

## The repository

`references/format.md` holds the exact Markdown, the indentation a `<details>` block needs inside a list, and the git workflow. Read it before writing or editing a README or a commit. The parts that bind:

- **A set lives in `<tool>-activities/`**, a git repository beside the learner's other sets. Its README is titled `# <Tool> Activities`, with one line under the title saying what the set builds and the version and date it was checked against.
- **Commit subjects are fixed.** `Set up the playground` for the root commit, which holds the README, `.gitignore` and starter files; `fixup! Set up the playground` for later README changes; `Exercise N` for the answer to item N, holding only that exercise's files. The number is the key that ties a commit to its item, so **these subjects win over the subject rules in `writing-commits`.**
- **Never renumber, or change the meaning of, an item that has a commit.** Renumbering means rewording every later commit. Append instead; items without commits can still move.
- **Commit only when asked.** Folding fixups in with an autosquash rebase rewrites history, so ask first, and leave it and any force-push to the user.
- Run the README's prose through `humanizer` before showing it.

## Extending or reviewing a set

- **Extending**: continue the numbering, reuse the set's project and names, and make the new items revisit earlier ideas. New items follow this skill even where the old ones do not.
- **Reviewing**: judge each item against the rules, rewrite only those that fail, and keep the rest word for word. Report what changed in each item and why; when nothing fails, change nothing and say so. Where an item and its commit disagree, say so and ask which is right: silently changing either one misdescribes the learner's work or throws it away.
- **Missing statements**: where commits exist under `TODO` items, read each commit with `git show`, then write the outcome its diff achieves, with a check, rather than a description of the diff.

## Before you finish

- Both stores were checked, or the reply names the one that could not be, and the reply says what every concept became.
- No exercise covers theory or a concept the learner already practised; theory without cards went to `anki-flashcards`.
- Every item is a task from real work, states an outcome, ends with a `Check:` sentence the learner can run alone, and fits in 15 minutes, except the capstone.
- Exercise 1 installs the tool and gives a visible result within minutes.
- Each item adds at most one concept new to the learner, and uses only what came before it.
- Features are named once; later items give only the goal; look-alikes meet in an item that names neither.
- Core ideas come back at least twice, a review item comes about every five exercises, and the set ends with a capstone, then a recall item or review notes.
- The set mixes types: at least one predict, one break or fix, one inspect, and one compare or choose.
- Every name exists by the time an item uses it, and every solution matches its item, boundaries included.
- Every command, flag and API was run or checked against the docs for the pinned version, and the reply says which.
- Solutions hold commands, output and the reason; code is in `Exercise N` commits; no hint contains its answer.
- A readiness set holds nothing from the repository, and nothing was written into the repository.
- The numbering continues the README's, and no item with a commit was renumbered or changed in meaning.

When a few items join an existing set, the per-item checks apply to them, and the set-level checks apply to the set they join.

## References

- `references/coverage.md`: searching the Anki collection and the existing sets, and deciding between an exercise, a flashcard and nothing. Read it before writing or extending a set.
- `references/codebase.md`: the inventory of a repository's stack and features, ranking, and where a readiness set goes. Read it for any readiness set.
- `references/format.md`: the README skeleton, list indentation, the hint and solution blocks, inputs, Resources, `.gitignore` and `resources/`, and the git workflow. Read it before writing a README or a commit.
- `references/exercise-types.md`: each exercise type, when it pays off, its prompt shape, its check and what its solution holds. Read it when planning a set.
- `references/worked-examples.md`: weak exercises from real sets rewritten, and strong ones kept, each with its reason. Read it before reviewing a set, or to calibrate wording.
- `references/principles.md`: the research behind these rules, with sources. Read it when a call is genuinely unclear, such as how much to guide a learner, whether to let them attempt first, or whether something needs practice or only recall.
