---
name: scheduling-pull-requests
description: Schedules a finished branch's pull request for a later day, so the work reads as done that day. It moves the branch's commit dates onto that day, writes the note for the first client meeting after the pull request opens, and leaves a one-off Paseo schedule that pushes the branch and opens the pull request that day. Use when asked to schedule, open, submit or publish a pull request later, on a given day, or in so many days, such as "schedule a PR for this in 2 days". Not for opening one now, which writing-pull-requests owns, and not for reminders, recurring schedules, or later actions on a pull request that already exists, such as marking it ready or merging it.
compatibility: Needs git, gh with push access, Python 3.9 or later, and the Paseo daemon running on this machine. Inside a Paseo session the CLI is at $PASEO_CLI.
---

# Scheduling pull requests

"Nice, now schedule a PR for this in 2 days" makes finished work read as though it was done on that day: its commits dated that day, the note for the meeting that reports it already written, and the pull request opened that day by a scheduled agent. One request covers all of it. Do the steps below in order without stopping to ask between them, and report once at the end.

## The request is the authorisation

Asking for the schedule authorises, for this branch only: committing the work still in the tree, moving the dates of its unpushed commits, writing the meeting note, creating the schedule, and opening the pull request with the text shown in the final reply. Here that outranks the ask-first defaults of writing-commits, rewriting-history and writing-pull-requests.

It never authorises a force push, and never a push before the opening time. GitHub records when a branch arrives, and a remote copy would show the new dates early.

## Before scheduling

Read the branch state; do not assume it.

```sh
git status --short                                      # uncommitted work
git log --oneline "origin/$base..HEAD"                  # what will be published
gh pr list --head "$(git branch --show-current)" --state all --json url,state
"${PASEO_CLI:-paseo}" status                            # the daemon that will run it
```

`$base` is the branch the user names, or else the default: `gh repo view --json defaultBranchRef --jq .defaultBranchRef.name`.

| Finding | Then |
| --- | --- |
| A pull request already exists for the branch | Nothing to schedule, because it is already public. Say so and stop |
| No commits ahead of the base and nothing uncommitted | Nothing to publish. Say so and stop |
| Uncommitted changes that are the work just done | Commit them with writing-commits first: they are what "this" means. Ask only about changes that look unrelated to it |
| The branch is already on the remote | Its dates cannot move without a force push. Stop, say so, and offer to schedule it with the dates as they are |
| No daemon answers | Stop. Nothing else can run the schedule |

## The day

- Resolve the day against today on this machine and state it with its weekday: "in 2 days", said on Wednesday 30 September 2026, is Friday 2 October.
- If it falls on a weekend, keep it and say so in the reply. The user moves it if they want.
- The time zone is the machine's, as an IANA name: `readlink /etc/localtime | sed 's|.*/zoneinfo/||'` on macOS and most Linux systems.
- The commits land between 10:00 and 17:15, and the pull request opens by 18:00. Pass `--from` and `--to` when the user names other hours.

## 1. Move the commit dates

```sh
python3 <this skill's directory>/scripts/redate.py --base "origin/$base" --day 2026-10-02 --tz Europe/Paris --apply
```

It gives every commit on the branch a new author and committer date on that day, at random times in the commits' order and some minutes apart, and picks when the pull request opens: 15 to 45 minutes after the last commit. Contents, messages and authors do not change, the working tree and the index are untouched, and the old tip stays in the reflog. It prints JSON. Keep `new_tip`, `pull_request_at`, `cron`, `undo` and `content_dates` for the steps below.

It refuses a detached HEAD, a rebase or merge in progress, merge commits on the branch, commits already on a remote branch, and a window that starts in the past. Report a refusal as it is; never work around one with a rebase or a filter.

`content_dates` lists file names and added lines that still carry the day the work was really done, such as a migration named `20260930_add_exports.sql` or a changelog heading. The script cannot move them. Name each one in the reply, and change none unless the user asks. A signed commit loses its signature, counted in `signatures_dropped`; say so too.

## 2. Write the meeting note

When preparing-client-meetings is available and its roster has a row for this repository, hand the scheduled pull request to it, as its section "A scheduled pull request" describes: the repository, the branch, `pull_request_at`, the ticket key, and one plain sentence saying what changed. It writes the section for the first meeting after the opening time. With a 09:30 daily and a pull request opening on Friday at 17:12, that is Monday's daily, because Friday's took place before the pull request existed.

Without the skill, or without a row, write no note, and say why in the reply.

## 3. Draft the text

Write the title and description with writing-pull-requests, from the diff and the commits. A ticket key goes in the title suffix, as in `Export invoices as CSV [ACME-9]`. Open it ready for review unless the user asked for a draft. The text goes in the final reply rather than waiting for approval, and the user can still change it before the opening time.

## 4. Create the schedule

These commands are for the agent, run unattended.

The run needs a provider, a model and a mode. Inside a Paseo session, take them from this agent:

```sh
"$PASEO_CLI" inspect "$PASEO_AGENT_ID" --json    # Provider, Model, AvailableModes
```

`--provider` takes `<Provider>/<Model>` from that output, such as `omp/anthropic/claude-opus-5-5` for oh-my-pi. Outside a session, `paseo provider ls` lists providers and their modes. The mode must never ask, because an unattended run fails the moment it waits for permission. For oh-my-pi that mode is `full`.

Write the prompt below to a file with the file tool, or with a heredoc whose delimiter is quoted (`<<'EOF'`): an unquoted one expands `$d` and `$(…)` in step 5 while writing, and the run gets a broken command. Then create the schedule with the script's `cron`. The prompt is the last argument. For a pull request opening on Friday 2 October at 17:12 in Paris, scheduled on Wednesday at 01:00:

```sh
"${PASEO_CLI:-paseo}" schedule create --json \
  --cron "12 17 2 10 *" --timezone Europe/Paris \
  --max-runs 1 --expires-in 65h \
  --provider omp/anthropic/claude-opus-5-5 --mode full \
  --cwd "$(git rev-parse --show-toplevel)" \
  --name "Open the csv-export pull request" \
  "$(cat "$prompt_file")"
```

| Flag | Why |
| --- | --- |
| `--cron "<minute> <hour> <day> <month> *"` | One date and time. Cron has no year, so the next two flags keep it to one run |
| `--max-runs 1` | Completes the schedule after its first run, whether it succeeded or failed. Nothing retries |
| `--expires-in` | Hours from now until a day after the opening time, rounded up: 65 from Wednesday 01:00 to Saturday 17:12. If the run was skipped, the schedule ends here instead of firing a year later |
| `--timezone` | Reads the cron fields as wall-clock time there, daylight saving included |
| `--cwd` | The worktree the work is in. The run happens there |
| `--json` | Prints a summary with the id the next command needs. It does not show the run limit or the expiry, even when both are set |

Then check what Paseo stored, which only `inspect` shows in full:

```sh
"${PASEO_CLI:-paseo}" schedule inspect <id> --json    # nextRunAt, maxRuns, expiresAt
```

`nextRunAt` must be `pull_request_at` in UTC, `2026-10-02T15:12:00.000Z` for 17:12 in Paris that day, with `maxRuns` at 1 and `expiresAt` after it. If any of them is wrong, delete the schedule and create it again with the flags fixed.

## The prompt

The new agent starts with this prompt and the repository, nothing else. Replace every angle-bracketed field, and leave nothing for it to work out. The worktree path is `git rev-parse --show-toplevel`, the same path `--cwd` gets, and the commit is the script's `new_tip`.

```text
Publish the pull request for branch <branch> in <worktree path>. It was scheduled for <weekday, date, time and zone>, and its title and description were written for commit <full sha>. If any command fails, stop and report its output.

1. If `git rev-parse refs/heads/<branch>` is not <full sha>, stop: the branch changed after scheduling. Publish nothing and report both commits.
2. If `gh pr list --head <branch> --state all --json url` lists a pull request, stop and report its URL.
3. Run `git push -u origin <branch>`.
4. Run `mkdir -p "$(git rev-parse --git-path scheduled-pull-request)"`. In that directory, write the title below to `title` and the description below to `body.md`, exactly as given, replacing any files already there.
5. Run: d="$(git rev-parse --git-path scheduled-pull-request)"; gh pr create --base <base> --head <branch> --title "$(cat "$d/title")" --body-file "$d/body.md"
6. Report the pull request URL and anything that did not go as planned.

Do not rebase, amend, request reviewers or write to a tracker.

The title is the line between BEGIN TITLE and END TITLE, and the description is every line between BEGIN DESCRIPTION and END DESCRIPTION.

BEGIN TITLE
<title>
END TITLE

BEGIN DESCRIPTION
<description>
END DESCRIPTION
```

For a draft, end step 5 with `--draft`. The title goes through a file because house titles carry backticks, which a shell would run inside double quotes, and both files sit in the git directory, out of the working tree.

The run never rebases, even when the base has moved: a pull request behind its base is ordinary, GitHub shows it, and the user updates it as they would any other.

## The reply

One message, after everything above is done:

- the day, with its weekday, and each commit's subject with its old and new date;
- where the note went, with its lines, or why there is none;
- the exact title and description, and that `paseo schedule update <id> --prompt "…"` changes them before the opening time;
- the schedule id and the opening time in the user's zone;
- every content date the script found, and any signature it dropped;
- how to undo each part: `paseo schedule delete <id>`, the script's `undo` command, and removing the note's section;
- that nothing announces a skipped or failed run, so after the opening time they check the pull request, or `paseo schedule inspect <id>`;
- that the workspace must stay open until the pull request exists.

To move the day, run the script again with the new day, which moves every commit again, then `paseo schedule update <id> --cron "…" --prompt "…"` with the new tip, and hand the new opening time to preparing-client-meetings.

## What can stop it

Read in the Paseo 0.7.2 daemon source (`schedule/service.js` and `workspace-archive-service.js`) on 2026-09-30. Check again after upgrading Paseo.

- **The daemon was not running at the opening time.** When it starts, Paseo moves every missed run to the next matching time, which for a one-date cron is a year later, so the expiry ends the schedule with no run. The pull request does not open. A machine that was only asleep is fine: the run starts when it wakes.
- **The worktree is gone.** A run whose directory no longer exists ends the schedule. Archiving a Paseo workspace deletes its worktree, so the workspace the work was done in stays open until the pull request exists. When the run ends, Paseo archives the workspace it opened for the run and deletes the worktree unless another open workspace still uses it, so the one kept open is also what keeps the worktree afterwards.
- **The branch changed after scheduling.** The run stops at its first step and publishes nothing. To include new commits, go through the steps again: the script moves every commit onto the day again, and `paseo schedule update <id> --cron "…" --prompt "…"` takes the new tip and time.
- **The run asked for permission.** It fails at once, which is why the mode must be one that never asks.

## Before you finish

- The branch state was read, and uncommitted work that belonged to "this" was committed first.
- `redate.py --apply` ran for the resolved day, or its refusal was reported and not worked around.
- The note sits under the first meeting after the opening time, or the reply says why there is none.
- `paseo schedule inspect` shows `nextRunAt` at `pull_request_at`, `maxRuns` at 1 and an `expiresAt`.
- The prompt names the branch, the new tip, the base, the title and the description, with no placeholder left.
- The reply covers the dates, the note, the text, the schedule, the content dates, and how to undo each.
- Nothing was pushed or force pushed.
