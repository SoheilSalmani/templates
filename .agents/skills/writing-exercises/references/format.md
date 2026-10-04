# The activities format

## Contents

- The README
- An item and its blocks
- Inputs
- Numbering and parts
- Parts and Resources
- The repository
- Commits
- Finding an answer

## The README

````markdown
# <Tool> Activities

1. <Verb> <outcome>.

   <details>
     <summary>Solution</summary>

   ```bash
   <command>
   ```

   </details>

2. <Next item.>
````

- The title uses the tool's own casing: `# dbt Activities`, `# systemd Activities`, `# Amazon Web Services Activities`.
- **The list comes straight after the title.** No description, no version line, no notes: the version and date the set was checked against go in the reply.
- No `## TODOs` or notes sections. Planning notes stay out of the README.

## An item and its blocks

````markdown
3. <Verb> <outcome>.

   <details>
     <summary>Solution</summary>

   ```bash
   <command>
   ```

   ```text
   <output, only where it is the answer>
   ```

   <One sentence, only where the commands alone would mislead.>

   </details>
````

- **Indent everything under an item to the column where its text starts**: 3 spaces under `1.` to `9.`, 4 under `10.` to `99.`. With less, the block falls out of the item: it renders flush left, between two halves of the list.
- `<summary>` sits 2 spaces deeper than its `<details>`.
- **Leave a blank line after `</summary>`**, or GitHub shows the Markdown inside as plain text, fences and all. Leave one before `</details>` too, as the sets already do.
- Leave a blank line between items, and between an item's text and its first block.
- The only block is labelled exactly `Solution`. Items carry no hint.
- Every fence names a language. Match the fence the README already uses for shell, `bash` or `sh`, and use `bash` in a new README. Use `text` for output, and the tool's language for code and queries: `sql`, `python`, `hcl`, `json`.
- Show output only where it answers the item, such as a predict item's result, and only the lines that do.

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

- **Setup that is not what the set teaches** goes in the setup commit, or in the solution, never in an item of its own.

## Numbering and parts

- **One list per README, numbered 1 to N**, so that each `Exercise N` names exactly one commit on the branch.
- A long set can be split with `##` headings that name its parts, such as the course or chapter each part follows. The numbering continues across them: the list after a heading starts at the next number, which GitHub honours.
- Older READMEs restart at 1 under each `## <Source>` section and keep each section's answers on a branch of its own. When extending one of those, keep its scheme.
- Never write `1. TODO.` as a placeholder. A part with no exercises yet is left out.

## Parts and Resources

- Resources are optional. A part that follows a course, book or tutorial ends with `### Resources`, linking it; a set that follows nothing has none.
- One bullet per source: `- [<Title> (<Publisher or site>)](<url>)`, such as `- [Terraform in Action (Manning)](...)`.

## The repository

- The directory is `<tool>-activities/`, lowercase and hyphenated, beside the learner's other sets.
- `.gitignore` groups its patterns into blocks, each under a `# <What> (<Tool>)` comment, with a blank line between blocks:

  ```gitignore
  # Virtual environment (uv)
  .venv/

  # Secrets (dlt)
  .dlt/secrets.toml
  ```

- A book's or course's companion code goes under `resources/<slug>` as a git submodule, and only when an exercise uses it:

  ```bash
  git submodule add <url> resources/<slug>
  ```

- Starter files the exercises need, such as code to fix, data to load, or a project to predict about, go in the setup commit.

## Commits

| Subject | Holds |
| --- | --- |
| `Set up the playground` | The root commit: README, `.gitignore`, `.gitmodules`, starter files |
| `fixup! Set up the playground` | A later change to the README, committed on its own |
| `Exercise N` | The answer to item N, and nothing else. Never the README |
| `fixup! Exercise N` | A correction to the answer to item N |

- **The subject is the whole message.** No body, no prefix, no trailer.
- **An exercise that changes no file has no commit.** Its answer lives entirely in its `Solution` block.
- **Write the item before its answer.** A statement written afterwards describes the diff instead of the goal.
- **The numbers are keys.** An item inserted before committed ones means rewording every later `Exercise N` commit, so append instead. Items without commits can be reordered freely.
- **Folding fixups in rewrites history.** `git rebase -i --autosquash --root` moves every `fixup!` into its target and changes every hash after the root, so the remote needs a force-push. Both are the user's call; `rewriting-history` covers the mechanics.

## Finding an answer

```bash
git log --oneline --grep='^Exercise 4$'    # the commit that answers item 4
git show <sha>                              # that answer, as a diff
```

To redo an item from scratch, branch from the commit before its answer, and compare with `git diff <your-branch> <sha>` once yours works.
