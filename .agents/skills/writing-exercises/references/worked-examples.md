# Worked examples

Real items from one learner's activity sets, with the defect named and a rewrite. Read the defect before the rewrite: the same defect turns up in every tool, and spotting it is the skill. The rewrites stay as short as the learner's own strong items: one sentence, the outcome, nothing the learner can choose for themselves.

## Contents

- Items that are not tasks
- Items that are theory
- Items that dictate the steps
- Items that depend on another item
- Items whose solution disagrees
- Sets that repeat themselves
- Strong items, kept

## Items that are not tasks

**A noun.** `web-development-activities/README.md:93`

```markdown
15. Cards.
```

A note to self: no outcome, no way to finish. Rewrite:

```markdown
15. Add a row of stat cards to the home page.
```

**A vague verb.** `javascript-activities/README.md:26`

```markdown
8. Experiment `import.meta`.
```

"Experiment" has no end. Find what the feature is for, and make that the outcome:

```markdown
8. Load a JSON file that sits next to the script, whichever directory you run it from.
```

**A topic, not a task.** `lua-activities/README.md:21`

```markdown
9. Write a program that works with time.
```

Split the topic into what the learner should be able to do with it, one item each:

```markdown
9. Print today's date with its weekday.
```

**A toy, not a task.** `lua-activities/README.md:9`

```markdown
3. Create a `Vector` table and test the colon operator.
```

"Test the operator" has no purpose and no end. Give the feature a job:

```markdown
3. Write a vector type with methods, and use it to work out how far a walker ends up from where it started.
```

## Items that are theory

**A fact asked as an exercise.** `javascript-activities/README.md:16`

```markdown
6. What are the four types of module specifiers?
```

The answer is a sentence to remember, not something to do, so it is no exercise at all. It goes to `anki-flashcards`, unless the collection already cards it. If a real task needs the fact, the task carries it instead: "Load a charting library from a CDN and a local module in one page."

## Items that dictate the steps

**A tutorial step pasted in.** `nextjs-activities/README.md:14`

```markdown
2. Add global styles to your application by navigating to `/app/layout.tsx` and importing the `global.css` file. Copy the code below and paste it above the `<p>` element in `/app/page.tsx`:
```

Two outcomes, the first given away as steps, the second a paste with nothing to learn. Keep the outcome that teaches something:

```markdown
2. Make the global styles apply to every page.
```

**The method in place of the goal.** `terraform-activities/README.md:54` is rewritten in `SKILL.md`: "Update the AMI ID" becomes a prediction of whether the instance is replaced.

## Items that depend on another item

**"Same as the previous."** `nextjs-activities/README.md:42`

```markdown
7. Same as the previous exercise but for the `hero-mobile.png` image. The image should be revealed on mobile screens.
```

A learner who reads this item alone cannot do it. Restate the task:

```markdown
7. Show the mobile hero image instead of the desktop one on small screens.
```

**"Two ways", unnamed.** `python-activities/README.md:20`

```markdown
3. Write a CLI which uses nesting commands (two ways).
```

The ways exist only in the book. Make each one an item:

```markdown
3. Write a todo CLI with add and list subcommands, grouped.

4. Register one of the subcommands without its decorator.
```

**A name that does not exist yet.** `snowflake-activities/README.md:540-547`

```markdown
21. Move a table in a different schema.
```

The solution moves the table into a schema that only exists in another database, so it fails. Ask for the schema in the item, and make the solution create it:

```markdown
21. Move the summary table into a new schema without copying its rows.
```

**A typo hiding the goal.** `dlt-activities/README.md:79`

```markdown
12. Update the tranformer to not used `data_from`.
```

Say what replaces it:

```markdown
12. Bind the details transformer where you build the source instead of in its decorator.
```

## Items whose solution disagrees

**A boundary the solution ignores.** `mastra-activities/README.md:56` asks for a step where "a valid text is one that has a word count of strictly more than 5 words". The committed step uses `wordCount >= 5`. Keep the boundary in the item, and fix the solution to match it:

```markdown
11. Add a step that marks a text valid when it has more than five words.
```

**Expected values copied wrong.** `python-activities/README.md:255-259` lists three expected positions, all labelled `Particle(0.3, 0.5, 1)`, while the particles in `simul.py` differ. The item needs none of the values; the solution needs them right:

```markdown
3. Test the simulator's evolve method on the three particles of the visualisation test.
```

**A statement the answer ignores.** `weft-activities/README.md:14` asks for "three questions to ask the user for the project name, package name, and whether to include a Dockerfile", and the `Exercise 2` commit computes the package name instead of asking for it. When reviewing, report it and ask which the learner meant; if the commit is right, the item becomes:

```markdown
2. Ask for the project name and whether to add a Dockerfile, and derive the package name.
```

**The wrong tool.** `kubernetes-activities/README.md:29-36` asks to print a greeting with the busybox image, and its solution runs `docker run`: no Kubernetes at all. Rewrite, with a solution that uses the tool the set teaches:

````markdown
1. Run a one-off pod that prints a greeting.

   <details>
     <summary>Solution</summary>

   ```bash
   kubectl run hello --image=busybox --restart=Never -- echo 'Hello, World!'
   kubectl logs hello
   ```

   </details>
````

**A solution that does not run.** `rollup-activities/README.md:17` gives `rollup src/main.js -o bundle.js cjs`, which is missing `-f` before the format. Every command in a solution is run or checked against the docs before it ships.

## Sets that repeat themselves

`mastra-activities/README.md:99-115` has nine items of the form "Write a demo page using the `X` component from AI Elements." The same task nine times, with the feature always named. Keep one build item to introduce the library, then make the learner choose:

```markdown
24. Write a demo page with the message component.

25. Build a chat demo that shows the agent's reasoning while it thinks, choosing the components yourself.
```

## Strong items, kept

Keep these shapes.

- **Short and open.** `terraform-activities/README.md`: "Inspect the current state." and "Add a variable to define the instance name." `prisma-activities/README.md`: "Write a script to print all the records." One sentence, an outcome, and the solution shows one way.
- **Inline input and a run.** `dlt-activities/README.md:15-23` gives the Pokémon list as a block in the item, asks for a pipeline that ingests it, and asks for it to be run. Later items reuse the same data.
- **A behavioural probe.** `mastra-activities/README.md:27`: "Add memory to your agent. Test the memory in Mastra Studio by asking your agent about the transactions it has seen so far."
- **Break, then fix.** `python-activities/README.md:481-483`: a Flask route that must be vulnerable to injection, then "Fix the route by escaping the value captured from the URL." The learner sees the failure before the cure.
- **One concept changing at a time.** `snowflake-activities/README.md:52`, `:97`, `:143` and `:191` load four CSV files, one each through a table stage, a user stage, a named internal stage and a named external stage.
- **A test that tries to fail.** `amazon-web-services-activities/README.md:61`: "test that the S3 bucket requires connections to use HTTPS". The solution makes the same call over HTTP, which must fail, and over HTTPS, which must succeed.
- **A difference made visible.** `sqlmesh-activities/README.md:42` and `:53` create a development environment, then query the same model in dev and in prod.
- **Understanding forced by a reset.** `meltano-activities/README.md:170`: "Drop the `tap_github.commits` and the `analytics.authors` tables. Run the final pipeline alltogether (ignore the stored state)." The learner has to know what state is to do it.
