# Worked examples

Real items from one learner's activity sets, with the defect named and a rewrite. Read the defect before the rewrite: the same defect turns up in every tool, and spotting it is the skill.

## Contents

- Items that are not tasks
- Items that are theory
- Items that dictate the steps
- Items with no check
- Items that depend on another item
- Items whose solution disagrees
- Sets that repeat themselves
- Strong items, kept

## Items that are not tasks

**A noun.** `web-development-activities/README.md:93`

```markdown
15. Cards.
```

A note to self: no outcome, no input, no way to finish. Rewrite:

```markdown
15. Add a row of three cards to the home page with shadcn's `Card`, one each for revenue, orders and refunds, showing the value and the change since last month. Check: at 375 px wide the cards stack into one column.
```

**A vague verb.** `javascript-activities/README.md:26`

```markdown
8. Experiment `import.meta`.
```

"Experiment" has no end. Find what the feature is for, and make that the outcome:

```markdown
8. Make `src/read.mjs` load `data.json` from its own directory using `import.meta.url`, whichever directory you run it from. Check: `node src/read.mjs` and `cd src && node read.mjs` print the same data.
```

**A topic, not a task.** `lua-activities/README.md:21`

```markdown
9. Write a program that works with time.
```

Split the topic into what the learner should be able to do with it, one item each:

```markdown
9. Print today's date as `YYYY-MM-DD (Weekday)` using `os.date`. Check: the output matches `date '+%Y-%m-%d (%A)'` in your shell.
```

**A toy, not a task.** `lua-activities/README.md:9`

```markdown
3. Create a `Vector` table and test the colon operator.
```

"Test the operator" has no purpose and no end. Give the feature a job:

```markdown
3. Write a `Vector` module whose values support `v:add(w)` and `v:length()`, and use it to work out how far a walker ends up from where it started. Check: a walk of 3 steps east, then 4 steps north, ends 5 steps away.
```

## Items that are theory

**A fact asked as an exercise.** `javascript-activities/README.md:16`

```markdown
6. What are the four types of module specifiers?
```

The answer is a sentence to remember, not something to do, so it is no exercise at all. It goes to `anki-flashcards`, unless the collection already cards it, as one question with one answer: which module specifiers a browser accepts without an import map. If a real task needs the fact, the task carries it instead: "Load `chart.js` from a CDN and `./stats.js` from the site in one page", whose check fails on a bare specifier.

## Items that dictate the steps

**A tutorial step pasted in.** `nextjs-activities/README.md:14`

```markdown
2. Add global styles to your application by navigating to `/app/layout.tsx` and importing the `global.css` file. Copy the code below and paste it above the `<p>` element in `/app/page.tsx`:
```

Two outcomes, the first given away as steps, the second a paste with nothing to learn. Keep the outcome that teaches something and say how it shows:

```markdown
2. Make the styles in `app/ui/global.css` apply to every page of the app. Check: the home page, unstyled until now, is styled.
```

**The method in place of the goal.** `terraform-activities/README.md:54` is rewritten in `SKILL.md`: "Update the AMI ID" becomes a prediction of whether the instance is replaced, which `terraform plan` settles.

## Items with no check

**Build it, and then what?** `mastra-activities/README.md:95`

```markdown
22. Create a chat route.
```

Nothing says what the route takes, returns or proves. Rewrite:

```markdown
22. Expose the Financial Assistant Agent at `POST /api/chat` in the Next.js app, streaming its reply. Check: with `curl -N`, the reply arrives in pieces, not all at once.
```

**The wrong tool, and an output that cannot match.** `kubernetes-activities/README.md:29-36`

```markdown
1. Print "Hello, World!" using the `busybox` image.
```

Its solution runs `docker run busybox echo "Hello World"`: no Kubernetes, and the text differs from the item. Rewrite, with a check that fixes both:

````markdown
1. Run a one-off pod from the `busybox` image that prints `Hello, World!` and exits. Check: `kubectl logs` for the pod prints exactly `Hello, World!`.

   <details>
     <summary>Solution</summary>

   ```bash
   kubectl run hello --image=busybox --restart=Never -- echo 'Hello, World!'
   kubectl logs hello
   ```

   </details>
````

## Items that depend on another item

**"Same as the previous."** `nextjs-activities/README.md:42`

```markdown
7. Same as the previous exercise but for the `hero-mobile.png` image. The image should be revealed on mobile screens.
```

A learner who reads this item alone cannot do it. Restate the task in full:

```markdown
7. Show `hero-mobile.png` instead of `hero-desktop.png` on screens narrower than 768 px. Check: at 375 px and at 1280 px wide, exactly one hero image is visible.
```

**"Two ways", unnamed.** `python-activities/README.md:20`

```markdown
3. Write a CLI which uses nesting commands (two ways).
```

The ways exist only in the book. Make each one an item, and let the second compare with the first:

```markdown
3. Write `todo`, a Click CLI with two subcommands, `todo add TEXT` and `todo list`, grouped with `@click.group`. Check: `todo --help` lists both.

4. Register `list` on the group with `add_command` instead of the decorator. Check: `todo --help` prints the same as before.
```

**A name that does not exist yet.** `snowflake-activities/README.md:540-547`

```markdown
21. Move a table in a different schema.
```

The solution moves `DEMO3B_DB.PUBLIC.SUMMARY` into `DEMO3B_DB.BANKING`, but the only `BANKING` schema created so far is in `DEMO3A_DB`, so it fails. Name the table and the target, and create the target first:

```markdown
21. Move `DEMO3B_DB.PUBLIC.SUMMARY` into a new schema, `DEMO3B_DB.BANKING`, without copying its rows. Check: `SHOW TABLES IN SCHEMA DEMO3B_DB.BANKING` lists `SUMMARY`, and the `PUBLIC` schema no longer does.
```

**A typo hiding the goal.** `dlt-activities/README.md:79`

```markdown
12. Update the tranformer to not used `data_from`.
```

Say what replaces `data_from` and how the learner knows nothing broke:

```markdown
12. Remove `data_from` from the `pokemon_details` transformer and bind it to the `pokemon` resource where you build the source instead. Check: the pipeline loads the same `pokemon_details` rows as in exercise 11.
```

## Items whose solution disagrees

**A boundary the check never tests.** `mastra-activities/README.md:56` asks for a step where "a valid text is one that has a word count of strictly more than 5 words", whose output says "whether it is valid or not". The committed step uses `wordCount >= 5` and throws on invalid text. A check would have caught both, so put the boundary in it:

```markdown
11. … Check: a 5-word text comes back with `isValid: false`, and a 6-word text with `isValid: true`.
```

**Expected values copied wrong.** `python-activities/README.md:255-259` lists three expected positions, all labelled `Particle(0.3, 0.5, 1)`. The particles in `simul.py` are `(0.3, 0.5, 1)`, `(0.0, -0.5, -1)` and `(-0.1, -0.4, 3)`. Expected values are the strongest check a set can give, so a slip in them does the most damage:

```markdown
3. Test `ParticleSimulator.evolve` with `assert` statements. After `evolve(0.1)`, the three particles from `test_visualize` must be within `1e-5` of:

   - `(0.210269, 0.543863)` for `Particle(0.3, 0.5, 1)`
   - `(-0.099334, -0.490034)` for `Particle(0.0, -0.5, -1)`
   - `(0.191358, -0.365227)` for `Particle(-0.1, -0.4, 3)`

   Check: `python test_simul.py` runs without an `AssertionError`.
```

**A statement the answer ignores.** `weft-activities/README.md:14` asks for "three questions to ask the user for the project name, package name, and whether to include a Dockerfile", and the `Exercise 2` commit computes the package name instead of asking for it. When reviewing, report it and ask which the learner meant; if the commit is right, the item becomes:

```markdown
2. Ask for the project name and whether to include a Dockerfile, and derive the package name from the project name instead of asking for it. Check: `weft new` asks two questions, not three.
```

**A solution that does not run.** `rollup-activities/README.md:17` gives `rollup src/main.js -o bundle.js cjs`, which is missing `-f` before the format. Every command in a solution is run or checked against the docs before it ships.

## Sets that repeat themselves

`mastra-activities/README.md:99-115` has nine items of the form "Write a demo page using the `X` component from AI Elements." Each one is a docs example copied into a page: the same task nine times, with the feature always named. Keep one build item to introduce the library, then make the learner choose:

```markdown
24. Write a demo page using the `Message` component from AI Elements. Check: a user message and an assistant message render with different styles.

25. Build `/chat-demo`: a conversation that shows the agent's reasoning while it thinks, and a prompt box that is disabled while a reply streams. Use AI Elements components, and choose them yourself. Check: sending a message shows the reasoning, then the answer, and the prompt box comes back when the stream ends.
```

## Strong items, kept

Keep these shapes, and add the check where it is missing.

- **Inline input and a run.** `dlt-activities/README.md:15-23` gives the Pokémon list as a block in the item, asks for a pipeline that ingests it, and asks for it to be run. Later items reuse the same data.
- **A behavioural probe as the check.** `mastra-activities/README.md:27`: "Add memory to your agent. Test the memory in Mastra Studio by asking your agent about the transactions it has seen so far." The check proves the feature works without looking at its code.
- **Break, then fix.** `python-activities/README.md:481-483`: a Flask route that must be vulnerable to injection, then "Fix the route by escaping the value captured from the URL." The learner sees the failure before the cure.
- **One concept changing at a time.** `snowflake-activities/README.md:52`, `:97`, `:143` and `:191` load four CSV files, one each through a table stage, a user stage, a named internal stage and a named external stage, adding one new constraint per item.
- **A check that tries to fail.** `amazon-web-services-activities/README.md:61`: "test that the S3 bucket requires connections to use HTTPS". The solution makes the same call over `http://`, which must fail, and over `https://`, which must succeed.
- **A specification with its edge case named.** `_kim/dbt-activities/README.md:197-205` lists each renamed column, then "`is_food_item` is a new column that is true if the product type (which can be `null`) is `"jaffle"` and false otherwise".
- **A difference made visible.** `sqlmesh-activities/README.md:42` and `:53` create a development environment, then query the same model in `dev` and in `prod`.
- **Understanding forced by a reset.** `meltano-activities/README.md:170`: "Drop the `tap_github.commits` and the `analytics.authors` tables. Run the final pipeline alltogether (ignore the stored state)." The learner has to know what state is to do it.
