# The activities format

## Contents

- The README of an activity
- An item and its block
- Inputs
- Numbering and parts
- Parts and Resources
- The repository and its root README
- Commits
- Finding an answer

## The README of an activity

````markdown
# <Tool> Activities

1. <Verb> <outcome>.

   <details>
     <summary>Solution</summary>

   ```bash
   <command>
   ```

   </details>

2. <Verb> <outcome>.
````

- The title uses the tool's own casing: `# dbt Activities`, `# systemd Activities`, `# Amazon Web Services Activities`.
- **The list comes straight after the title.** No description, no version line, no notes: the version and date the set was checked against go in the reply.
- No `## TODOs` or notes sections. Planning notes stay out of the README.
- An item whose `Exercise N` commit is its whole answer, like item 2, has no block.

## An item and its block

````markdown
3. <Verb> <outcome>.

   <details>
     <summary>Solution</summary>

   ```bash
   <command>
   ```

   <The result, in a few words, for a predict, inspect, compare or choose item.>

   </details>
````

- **Indent everything under an item to the column where its text starts**: 3 spaces under `1.` to `9.`, 4 under `10.` to `99.`. With less, the block falls out of the item: it renders flush left, between two halves of the list.
- `<summary>` sits 2 spaces deeper than its `<details>`.
- **Leave a blank line after `</summary>`**, or the Markdown inside shows as plain text, fences and all; GitHub and GitLab both need it. Leave one before `</details>` too, as the sets already do.
- Leave a blank line between items, and between an item's text and its first block.
- The only block is labelled exactly `Solution`. Items carry no hint.
- **The block holds no code.** Its fences are shell, matching the README's `bash` or `sh` (`bash` in a new README), and `text` for an output line that is the result. Code, configuration and queries are in the item's `Exercise N` commit.
- **The result is a few words**, such as "Blocked." or "The first project.", never a sentence of why. Show output only where a line of it is the result, and only that line.

## Inputs

- **The smallest input the task needs.** Where the content is not what the set teaches, a one-line file or "any content" does.
- **Data or code to work on**, when it is short: a fenced block inside the item, indented with it.
- **A file too large to inline**: a link to a stable URL, or a file committed in the setup commit and named by its path.
- **A specification with several rules**: `-` bullets under the item, one rule each:

  ```markdown
  23. Create a staging model for products so that:

      - the SKU becomes the product ID
      - a product is a food item when its type, which can be null, is jaffle
  ```

- **Setup that is not what the set teaches** goes in the setup commit, or in an answer, never in an item of its own.

## Numbering and parts

- **One list per README, numbered 1 to N**, so that each `Exercise N` names exactly one commit on the branch.
- A long set can be split with `##` headings that name its parts, such as the course or chapter each part follows. The numbering continues across them: the list after a heading starts at the next number, which GitHub and GitLab both honour.
- Older READMEs restart at 1 under each `## <Source>` section and keep each section's answers on a branch of its own. When extending one of those, keep its scheme.
- Never write `1. TODO.` as a placeholder. A part with no exercises yet is left out.

## Parts and Resources

- Resources are optional. A part that follows a course, book or tutorial ends with `### Resources`, linking it; a set that follows nothing has none.
- One bullet per source: `- [<Title> (<Publisher or site>)](<url>)`, such as `- [Terraform in Action (Manning)](...)`.

## The repository and its root README

One repository holds every activity:

```text
activities/
├── README.md        the table of activities
├── .gitignore
├── weft/
│   └── README.md    one activity: its title and numbered list
└── rust/
    └── README.md
```

- `master` holds a single commit, `Set up the playground`, with the tooling, the root `README.md`, `.gitignore`, and every activity's folder with its `README.md` and starter files.
- The root `README.md` is the title and one table, a row per activity, linking the activity's `README.md` and its branch:

  ```markdown
  # Activities

  | Activity | Branch |
  | --- | --- |
  | [Weft](weft/README.md) | [weft](https://github.com/<owner>/activities/tree/weft) |
  ```

  The branch link is the forge's tree URL. GitHub: `https://github.com/<owner>/activities/tree/<branch>`; GitLab: `https://<host>/<namespace>/activities/-/tree/<branch>`.

- An activity's folder is named after the tool, lowercase and hyphenated, and its branch takes the same name.
- Everything an exercise produces lives in its activity's folder, and the commands in the blocks run from there.
- `.gitignore` groups its patterns into blocks, each under a `# <What> (<Tool>)` comment, with a blank line between blocks:

  ```gitignore
  # Virtual environment (uv)
  .venv/

  # Secrets (dlt)
  .dlt/secrets.toml
  ```

- A book's or course's companion code goes under `<activity>/resources/<slug>` as a git submodule, and only when an exercise uses it.
- Starter files the exercises need, such as code to fix, data to load, or a project to predict about, go in the activity's folder in `Set up the playground`.
- An older set, a `<tool>-activities` repository of its own, keeps its `README.md` at the root and its own `Set up the playground`.

## Commits

| Subject | Where | Holds |
| --- | --- | --- |
| `Set up the playground` | `master`, its only commit | The tooling, the root `README.md`, `.gitignore`, `.gitmodules`, and every activity's `README.md` and starter files |
| `fixup! Set up the playground` | `master` | A new activity, or a change to any `README.md` or starter file, until it is folded in |
| `Exercise N` | The activity's branch | The answer to item N: every file it creates or changes, inside the activity's folder, and nothing else. Never a `README.md` |
| `fixup! Exercise N` | The activity's branch | A correction to the answer to item N |

- **The subject is the whole message.** No body, no prefix, no trailer.
- **The commit is the answer.** All of an answer's code is in its `Exercise N`, and none of it in the `Solution` block. An exercise that changes no file has no commit; its answer lives entirely in its block.
- **Build the answers in order, on the branch.** For a new activity, commit its `README.md` and starter files on `master` as `fixup! Set up the playground`, and create its branch there. Then, item by item, run the item's commands in the activity's folder and commit what they leave before starting the next, so each answer starts where the last one ended, as the learner's will. Side-products such as a virtual environment or a build directory go in `.gitignore`, never in a commit. A README change found while building is one more fixup on `master`, with the unpublished branch rebased onto it.
- **Write the item before its answer.** A statement written afterwards describes the diff instead of the goal.
- **The numbers are keys.** An item inserted before committed ones means rewording every later `Exercise N` commit, so append instead. Items without commits can be reordered freely.
- **Folding fixups in rewrites history.** `git rebase -i --autosquash --root` on `master` moves every `fixup!` into `Set up the playground` and gives it a new hash, so every activity branch is then rebased onto the new `master` with `git rebase --onto master <old-setup> <branch>`, and all of them need a force-push. Ask once for the whole step, naming the branches it moves, and run it all on a yes; `rewriting-history` covers the mechanics.

## Finding an answer

```bash
git log --oneline --grep='^Exercise 4$' weft --   # the commit that answers item 4 of the weft activity
git show <sha>                                     # that answer, as a diff
```

The `--` tells git that `weft` is the branch, not the folder of the same name.

To redo an item from scratch, branch from the commit before its answer, and compare with `git diff <your-branch> <sha>` once yours works.
