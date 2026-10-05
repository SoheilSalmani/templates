---
name: writing-exercises
description: "Writes practice exercises to learn a software tool, framework, library or language fast, or to check that the learner masters the features a codebase uses before working on it, in the activities format: a README of short numbered real-world tasks with hidden `<details>` example solutions, and one `Exercise N` commit per answer. Checks the Anki collection and existing exercise sets first, sends theory to flashcards, and writes exercises only for practice that is missing. Use when asked to write, extend, review or fix exercises or activities for learning something, to turn a tutorial, course, book or docs into exercises, to check readiness for a repository's stack, to write an activities README's missing statements from its commits, or to write an exercise's reference solution. Not for writing the flashcards, which anki-flashcards owns, or for tutorials and how-to guides, which writing-documentation owns."
---

# Writing exercises

An exercise is one short attempt. The learner reads a one-line goal, produces an answer from memory and the docs, and only then opens the solution, one possible answer, to compare. Every rule below protects that loop: the goal must be quick to read and must not give the answer away, and the solution must show an answer that works. Exercises are for doing; what only needs remembering goes on flashcards.

**When rules conflict, the earlier one wins: correct, then needed, then produced by the learner, then short.** A wrong exercise is the worst kind: a learner who follows it exactly and fails concludes that they are the problem. An unneeded one spends the time the set exists to save.

## Scope

Two kinds of set:

- **Learning a tool**, framework, library or language. The target is what the learner wants to do with it.
- **Readiness for a codebase.** The target is the features a repository's code relies on, and the set checks that the learner masters them before working there.

Also in scope: more exercises for an existing set; reviewing or repairing one; turning a tutorial, course or docs into exercises; writing the statements an activities README is missing, from its `Exercise N` commits; and an exercise's reference solution, when asked.

Out of scope, and say so: writing the flashcards, which `anki-flashcards` owns once this skill has said what belongs on them; tutorials, how-to guides and reference docs, which `writing-documentation` owns; quizzing someone live; assessments that rank people; explaining the codebase itself.

## Exercise, flashcard, or nothing

Sort every candidate concept before writing anything, after checking two stores: the Anki collection, and the learner's existing sets with their `Exercise N` commits.

- **Theory goes on a flashcard, never into an exercise**: a definition, a rule, a default, a name, a syntax form, a trade-off stated in a sentence, and how to install the tool. Skip it when the collection already cards it; otherwise list it for `anki-flashcards`, which drafts the cards and asks before adding them.
- **Practice gets an exercise**: writing code with a feature, operating the tool, finding a bug, choosing under real constraints. Skip it when an exercise the learner has done already practises it.
- **Anything the target does not need, or the codebase barely uses, gets nothing.**

`references/coverage.md` has the searches for both stores and the full decision table; read it before writing or extending a set. The reply says what each concept became and why, and names any store it could not check.

## Before writing

1. **Read what exists.** In an existing set, read its whole `README.md` and the log of its answers, `git log --reverse --format='%h %s' <branch> --` (the `--` because the branch and the activity's folder share a name): which items have an `Exercise N` commit, which are still `TODO`, which source each section follows. The learner's other sets, folders of the activities repository and older `*-activities` repositories, show what they already know and how they write.
2. **Pin the subject**: the tool and its version, or the codebase's stack and its versions, and the tutorial, course or book if the learner follows one. Read the official docs for every part you will use. **Never write a command, flag, API or output you have not read in the docs or run.** The reply names the version and the date the set was checked against.
3. **Know the learner**: what they already use, and what they want this for. Infer it from the request and their sets, and ask only when the target is unknown and would change the set. By default the learner is an experienced developer, so skip programming basics and spend the set on what is new.
4. **Write the target in one sentence**: what the learner can do at the end without looking anything up. Every exercise serves it.

## Readiness for a codebase

The set checks the features the code relies on, not the codebase itself. Inventory the stack from the manifests and the features from the code, keep what is used often, sits in the core path, or is hard to read without knowing it, and write generic exercises on those.

- **Nothing from the repository goes into the set**: no code, names, domain terms, data or secrets. The set may be public, and the repository may be a client's.
- **The set goes into the learner's activities, never into the repository**: into the set for the language or framework, as a part named after the features.

Read `references/codebase.md` for any readiness set: it has the inventory method, with Rust worked through.

## Choosing what to practise

List the core model, meaning the few nouns the tool is built from and what it does with them when it runs; the day-one loop of run, inspect, undo, read an error and find the right page of the docs; the operations real work uses most; the traps, such as the classic mistake, the confusing error and the false friend that looks like something the learner knows and behaves differently; and the look-alikes, such as `count` and `for_each`. Keep only what the target needs. Most first sets need 10 to 20 exercises. More is a second set, not a longer one.

Then **write the capstone first**: the shortest realistic task that combines the core of the list. Work backwards from it, so that each exercise adds a piece the capstone needs, and grow **one small project** across the set.

## Ordering

- **Exercise 1 is the first thing done with the tool**, which the set assumes is installed, and ends in a visible result within minutes. No item installs anything.
- **At most one concept new to the learner per exercise.** A real task often needs several concepts, and those the learner knows cost nothing; two new ones at once turn a failure into a guess about which went wrong. A readiness set assumes the learner knows them all, so its items combine them the way the codebase does.
- **Each exercise uses only what came before**, and starts from the state the previous one left.
- **Name a feature the first time it is the target, then stop naming it.** Later items that need it give only the goal, so that using it is recall. Once two look-alikes are both known, one item names neither and makes the learner choose.
- **Guide first or attempt first, by what the learner could work out.** A convention nobody could guess, such as a magic file name, is named. Behaviour the learner can reason about is a prediction to make before running anything.
- **Bring every core idea back at least twice, unannounced**, with a different input each time. About every five exercises, a **review** item combines earlier ideas on new input.
- **Now and then, change a requirement on code the learner just wrote**, as real work does.
- **Tear down** anything that costs money or leaves state behind, as its own exercise.
- **End with the capstone**, which names no features. Where the learner schedules exercise reviews in Anki, propose review notes for the set's parts; otherwise add one **recall** item for a later day: rebuild a core piece without the docs, then compare it with its commit.

## Writing an exercise

The shape is `N. <Verb> <outcome>.`, one short sentence, two at most.

- **A task from real work.** Every item is something a developer does with the tool on a job: build a feature, fix a failing job, move data, speed up a query. Never a toy that runs a feature for no purpose.
- **Minimal.** Give the outcome and nothing the learner could do without. Leave out paths, file names, names and values the learner can choose; the solution shows one possible answer. An item reads in seconds and is done in minutes.
- **Practise the target and nothing else.** Material from outside the target shrinks to the smallest stand-in that works, or disappears: a set on a template engine records placeholder files, not a service the learner has to read; a set on a CI system runs one-line steps, not a build.
- **State the outcome, not the steps.** Never put the answer's code in the prompt, and never turn a tutorial's "copy this" into an exercise. Code belongs in a prompt only as material: data to load, a snippet to predict, a bug to fix.
- **Keep code out of the sentence.** Name things in words where words are clear, such as "the project name" or "a Dockerfile". Inline code only for a name the learner must type exactly and words cannot carry; anything longer is fenced material. A file is the exception: give its name, such as `README.md`, never a paraphrase like "the README".
- **Give only the facts the task cannot do without**, such as data to load or a value a later item reuses.
- **One outcome per item.**
- **Block a shortcut only where it would skip the point**: "without adding a patch", "using only the CLI".
- **Size each item for 5 to 10 minutes**, never more than 15. Only the capstone takes longer.
- **Keep the state straight.** Every name a solution uses exists by then, and later solutions reuse it.
- **Mix the types**: build, extend, predict then run, break it on purpose, fix a bug, inspect, compare two ways, swap behind the tests, choose which. Aim the predict and break items at the traps. `references/exercise-types.md` gives each type's shape and solution; read it when planning a set.
- **Use plain words.** No "just", "simply", "easy", "experiment with" or "explore"; no item that is only a noun, such as "Cards."; no "same but…", which hides the task in the previous item.

A recipe step, before:

```markdown
6. Update the AMI ID to `ami-08d70e59c07c61a3a`.
```

After, the same change becomes a prediction:

````markdown
6. Change the instance's AMI. Before you apply, predict whether Terraform updates the instance or replaces it.

   <details>
     <summary>Solution</summary>

   It replaces it: the plan marks the instance `-/+`.

   ```text
   ~ ami = "ami-830c94e3" -> "ami-08d70e59c07c61a3a" # forces replacement
   ```

   </details>
````

An item that spends its words outside the target, before:

```markdown
1. Create a template `service` and record its first patch, `base`, from these four files: a `README.md`, a `package.json`, a seven-line Node.js `server.js` and a runbook, 40 lines to copy in all. Check: `weft check service` passes.
```

After, the same Weft practice:

```markdown
1. Create a template for Python projects that asks for the project name.
```

`references/worked-examples.md` rewrites more real exercises and names each one's defect. Read it before reviewing a set, or when a rule here feels abstract.

## Solutions

- **The `Solution` block is one possible answer, as short as it can be**: the commands, the few lines of code or configuration the answer turns on, and the answer to a predict or compare item. A sentence of why only where the commands alone would mislead.
- **Longer code belongs in the `Exercise N` commit**, not in the block. An exercise that changes no file has no commit.
- **No hints and no check.** An item is its sentence and its `Solution` block, nothing else.
- **Verify every solution.** Run it in a scratch directory outside the learner's repository when the tool runs locally; otherwise check each command, flag and API against the docs for the pinned version. Say which items ran and which were only checked. A solution that contradicts its item is a broken exercise, not a detail.

## The repository

`references/format.md` holds the exact Markdown, the indentation a `<details>` block needs inside a list, and the git workflow. Read it before writing or editing a README or a commit. The parts that bind:

- **One repository holds every activity.** Its `master` has a single commit, `Set up the playground`: the tooling, a root `README.md` with a table of every activity linking to its branch, and one folder per activity, named after the tool, holding that activity's `README.md`. An activity's `README.md` is its title, `# <Tool> Activities`, then the numbered list: no description and no version line.
- **Each activity has a branch named after its folder**, and its commits after `Set up the playground` are its answers and nothing else: one `Exercise N` per item, holding only that exercise's files, inside the activity's folder.
- **Commit subjects are fixed**, `Set up the playground` and `Exercise N`; the number is the key that ties a commit to its item, so **these subjects win over the subject rules in `writing-commits`.** A new activity or a change to any `README.md` is a `fixup! Set up the playground` on `master`, folded in by an autosquash rebase, after which every activity branch is rebased onto the new `master`.
- **Never renumber, or change the meaning of, an item that has a commit.** Renumbering means rewording every later commit. Append instead; items without commits can still move.
- **Commit only when asked.** Folding fixups in and rebasing the branches rewrite history, so ask first, and leave the force-push to the user unless they ask for it.
- Older sets are separate `<tool>-activities` repositories, with their `README.md` at the root and their own `Set up the playground`. When extending one, keep its layout.
- Run the README's prose through `humanizer` before showing it.

## Extending or reviewing a set

- **Extending**: continue the numbering, reuse the set's project and names, and make the new items revisit earlier ideas. New items follow this skill even where the old ones do not.
- **Reviewing**: judge each item against the rules, rewrite only those that fail, and keep the rest word for word. Report what changed in each item and why; when nothing fails, change nothing and say so. Where an item and its commit disagree, say so and ask which is right: silently changing either one misdescribes the learner's work or throws it away.
- **Missing statements**: where commits exist under `TODO` items, read each commit with `git show`, then write, in one sentence, the outcome its diff achieves rather than a description of the diff.

## Before you finish

- Both stores were checked, or the reply names the one that could not be, and the reply says what every concept became.
- No exercise covers theory, installation, or a concept the learner already practised; theory without cards went to `anki-flashcards`.
- Every item is a task from real work in one or two short sentences, with no check, no hint, and code kept out of its sentence, and fits in 15 minutes, except the capstone.
- No item needs knowledge outside the target: material from elsewhere is a stand-in.
- Exercise 1 is a first visible result with the tool, and nothing installs it.
- Each item adds at most one concept new to the learner, and uses only what came before it.
- Features are named once; later items give only the goal; look-alikes meet in an item that names neither.
- Core ideas come back at least twice, a review item comes about every five exercises, and the set ends with a capstone, then a recall item or review notes.
- The set mixes types: at least one predict, one break or fix, one inspect, and one compare or choose.
- Every name a solution uses exists by then, and every solution answers its item.
- Every command, flag and API was run or checked against the docs for the pinned version, and the reply says which, with the version and date.
- Solutions are one possible answer, mostly commands; longer code is in `Exercise N` commits.
- The activity's `README.md` is the title and the list, with no description, in the activity's folder, and the root `README.md` lists the activity with a link to its branch.
- A readiness set holds nothing from the repository, and nothing was written into the repository.
- The numbering continues the README's, and no item with a commit was renumbered or changed in meaning.

When a few items join an existing set, the per-item checks apply to them, and the set-level checks apply to the set they join.

## References

- `references/coverage.md`: searching the Anki collection and the existing sets, and deciding between an exercise, a flashcard and nothing. Read it before writing or extending a set.
- `references/codebase.md`: the inventory of a repository's stack and features, ranking, and where a readiness set goes. Read it for any readiness set.
- `references/format.md`: the README skeleton, list indentation, the solution block, inputs, parts and Resources, `.gitignore` and `resources/`, and the git workflow. Read it before writing a README or a commit.
- `references/exercise-types.md`: each exercise type, when it pays off, its prompt shape and what its solution holds. Read it when planning a set.
- `references/worked-examples.md`: weak exercises from real sets rewritten, and strong ones kept, each with its reason. Read it before reviewing a set, or to calibrate wording.
- `references/principles.md`: the research behind these rules, with sources. Read it when a call is genuinely unclear, such as how much to guide a learner, whether to let them attempt first, or whether something needs practice or only recall.
