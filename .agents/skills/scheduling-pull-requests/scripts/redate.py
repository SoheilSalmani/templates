#!/usr/bin/env python3
"""Move a branch's unpushed commits onto one day, for a scheduled pull request.

Gives every commit in BASE..HEAD a new author and committer date on DAY, at
random times between --from and --to, in the commits' order, and picks the
time the pull request opens: 15 to 45 minutes after the last commit, on a
whole minute. Contents, messages and authors stay as they are. The working
tree and the index are not touched: only the branch moves, and its old tip
stays in the reflog.

    python3 redate.py --base REF --day YYYY-MM-DD [--tz IANA]
                      [--from HH:MM] [--to HH:MM] [--seed N] [--apply]

Without --apply it prints the plan and changes nothing; the same --seed gives
the same times on both runs. --to is the latest time the pull request may
open, so the commits end 45 minutes before it.

Prints JSON: the branch, the old and new tips, each commit with its new date,
the pull request time and its cron fields, the undo command, and
content_dates: file names and added lines that carry a day a commit was
really made, such as a migration timestamp, which the script cannot move.

Exit codes: 0 when planned or applied; 1 when refused: a detached HEAD, a
rebase, merge, cherry-pick or revert in progress, merge commits in the range,
commits already on a remote branch, or a window that starts in the past or
before the commit the branch grew from; 2 on bad usage or a git error.
"""

import argparse
import json
import os
import random
import re
import subprocess
import sys
from datetime import date, datetime, time, timedelta, timezone

try:
    from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
except ImportError:  # Python 3.8 and older
    sys.exit("redate.py needs Python 3.9 or later for zoneinfo")

MAX_FINDINGS = 50
IDENTITY = re.compile(rb"^(author|committer) (.*) (\d+) ([+-]\d{4})$")


class Refused(Exception):
    """The repository is in a state this script will not rewrite."""


class Failed(Exception):
    """Bad usage, or git did not do what was asked."""


def git(*args, stdin=None):
    result = subprocess.run(["git", *args], input=stdin, capture_output=True)
    if result.returncode != 0:
        message = result.stderr.decode(errors="replace").strip()
        raise Failed(f"git {' '.join(args)}: {message}")
    return result.stdout


def git_text(*args):
    return git(*args).decode().strip()


def clock(value, flag):
    try:
        return time.fromisoformat(value)
    except ValueError:
        raise Failed(f"{flag} takes HH:MM, not {value!r}")


def branch_ref():
    result = subprocess.run(["git", "symbolic-ref", "-q", "HEAD"], capture_output=True, text=True)
    if result.returncode != 0:
        raise Refused("HEAD is detached; check out the branch the pull request is for")
    return result.stdout.strip()


def refuse_operation_in_progress():
    for marker, name in (
        ("rebase-merge", "rebase"),
        ("rebase-apply", "rebase"),
        ("MERGE_HEAD", "merge"),
        ("CHERRY_PICK_HEAD", "cherry-pick"),
        ("REVERT_HEAD", "revert"),
    ):
        if os.path.exists(git_text("rev-parse", "--git-path", marker)):
            raise Refused(f"a {name} is in progress; finish or abort it first")


def plan_times(count, start, commit_end, rng):
    """Random, ordered, at least a few minutes apart, all inside the window."""
    window = (commit_end - start).total_seconds()
    gap = min(20 * 60, window / (2 * count))
    free = window - gap * (count - 1)
    offsets = sorted(rng.uniform(0, free) for _ in range(count))
    return [start + timedelta(seconds=int(offset + index * gap)) for index, offset in enumerate(offsets)]


def rewrite(sha, parents, when):
    """Write a copy of the commit with new dates and parents; return its sha."""
    raw = git("cat-file", "commit", sha)
    header, separator, message = raw.partition(b"\n\n")
    stamp = f"{int(when.timestamp())} {when.strftime('%z')}".encode()
    lines, dropped, in_signature = [], False, False
    for line in header.split(b"\n"):
        if in_signature and line.startswith(b" "):
            continue
        in_signature = False
        if line.startswith((b"gpgsig ", b"gpgsig-sha256 ")):
            in_signature, dropped = True, True
            continue
        if line.startswith(b"parent "):
            old = line[len(b"parent "):].decode()
            line = b"parent " + parents.get(old, old).encode()
        elif line.startswith((b"author ", b"committer ")):
            match = IDENTITY.match(line)
            if not match:
                raise Failed(f"cannot read the {line.split(b' ')[0].decode()} line of {sha}")
            line = match.group(1) + b" " + match.group(2) + b" " + stamp
        lines.append(line)
    new = git("hash-object", "-t", "commit", "-w", "--stdin", stdin=b"\n".join(lines) + separator + message)
    return new.decode().strip(), dropped


def real_days(commits):
    days = set()
    for sha in commits:
        for field in ("%ad", "%cd"):
            days.add(git_text("log", "-1", f"--format={field}", "--date=format:%Y-%m-%d", sha))
    return sorted(days)


def content_dates(base, days):
    """File names and added lines in the pull request's diff that carry a real day."""
    patterns = []
    for day in days:
        d = date.fromisoformat(day)
        patterns += [d.isoformat(), d.strftime("%Y%m%d"), d.strftime("%Y/%m/%d"), d.strftime("%d/%m/%Y"), d.strftime("%d.%m.%Y")]
    found = []
    for path in git_text("diff", "--name-only", f"{base}...HEAD").splitlines():
        if any(p in path for p in patterns):
            found.append({"file": path, "line": None, "text": "the file name"})
    current, number = None, 0
    diff = git("diff", "--no-color", "--no-ext-diff", "-U0", f"{base}...HEAD").decode(errors="replace")
    for line in diff.splitlines():
        if line.startswith("+++ "):
            current = line[6:] if line.startswith("+++ b/") else None
        elif line.startswith("@@"):
            match = re.search(r"\+(\d+)", line)
            number = int(match.group(1)) if match else 0
        elif line.startswith("+") and current:
            if any(p in line for p in patterns):
                found.append({"file": current, "line": number, "text": line[1:].strip()[:160]})
            number += 1
    return found[:MAX_FINDINGS]


def run(args):
    try:
        zone = ZoneInfo(args.tz)
    except (ZoneInfoNotFoundError, ValueError):
        raise Failed(f"unknown time zone {args.tz!r}")
    try:
        day = date.fromisoformat(args.day)
    except ValueError:
        raise Failed(f"--day takes YYYY-MM-DD, not {args.day!r}")
    start = datetime.combine(day, clock(args.from_, "--from"), zone)
    latest = datetime.combine(day, clock(args.to, "--to"), zone)
    commit_end = latest - timedelta(minutes=45)
    if commit_end <= start:
        raise Failed("the window is too short: --to must be more than 45 minutes after --from")

    ref = branch_ref()
    refuse_operation_in_progress()
    base = git_text("rev-parse", "--verify", f"{args.base}^{{commit}}")
    commits = git_text("rev-list", "--reverse", "--topo-order", f"{base}..HEAD").split()
    if not commits:
        raise Refused(f"no commits between {args.base} and HEAD")
    if git_text("rev-list", "--merges", f"{base}..HEAD"):
        raise Refused("the range holds merge commits; this script only moves a straight line of commits")
    on_remote = git_text("branch", "-r", "--contains", commits[0])
    if on_remote:
        remote = on_remote.splitlines()[0].strip()
        raise Refused(f"{commits[0][:7]} is already on {remote}; moving its date would need a force push")
    if start <= datetime.now(timezone.utc):
        raise Refused(f"the window starts in the past ({start.isoformat()})")
    parent_line = git_text("log", "-1", "--format=%P", commits[0])
    if parent_line:
        grown_from = datetime.fromtimestamp(int(git_text("log", "-1", "--format=%ct", parent_line.split()[0])), timezone.utc)
        if start <= grown_from:
            raise Refused("the window starts before the commit the branch grew from")

    rng = random.Random(args.seed)
    times = plan_times(len(commits), start, commit_end, rng)
    opens = (times[-1] + timedelta(seconds=rng.uniform(15 * 60, 45 * 60))).replace(second=0, microsecond=0)
    days = real_days(commits)
    old_tip = commits[-1]

    entries, mapping, dropped = [], {}, 0
    for sha, when in zip(commits, times):
        entry = {
            "old": sha[:12],
            "subject": git_text("log", "-1", "--format=%s", sha),
            "old_date": git_text("log", "-1", "--format=%aI", sha),
            "new_date": when.isoformat(),
        }
        if args.apply:
            new, signature = rewrite(sha, mapping, when)
            mapping[sha] = new
            dropped += signature
            entry["new"] = new[:12]
        entries.append(entry)

    new_tip = mapping.get(old_tip)
    if args.apply:
        if git_text("rev-parse", f"{old_tip}^{{tree}}") != git_text("rev-parse", f"{new_tip}^{{tree}}"):
            raise Failed("the rewritten tip does not hold the same files; nothing was moved")
        git("update-ref", "-m", f"scheduling-pull-requests: move commit dates to {day}", ref, new_tip, old_tip)

    return {
        "branch": ref[len("refs/heads/"):],
        "day": day.isoformat(),
        "time_zone": args.tz,
        "applied": bool(args.apply),
        "old_tip": old_tip,
        "new_tip": new_tip,
        "commits": entries,
        "pull_request_at": opens.isoformat(),
        "cron": f"{opens.minute} {opens.hour} {opens.day} {opens.month} *",
        "signatures_dropped": dropped,
        "content_dates": content_dates(base, days),
        "undo": f"git update-ref {ref} {old_tip} {new_tip}" if new_tip else None,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--base", required=True, help="the ref the pull request targets, such as origin/main")
    parser.add_argument("--day", required=True, help="the day to move the commits onto, YYYY-MM-DD")
    parser.add_argument("--tz", default="UTC", help="IANA time zone the times are in (default: UTC)")
    parser.add_argument("--from", dest="from_", default="10:00", help="earliest commit time (default: 10:00)")
    parser.add_argument("--to", default="18:00", help="latest pull request time (default: 18:00)")
    parser.add_argument("--seed", type=int, help="fix the random times, so a plan and its --apply agree")
    parser.add_argument("--apply", action="store_true", help="move the commits; without it, only print the plan")
    args = parser.parse_args()
    try:
        print(json.dumps(run(args), indent=2))
    except Refused as error:
        print(f"refused: {error}", file=sys.stderr)
        return 1
    except Failed as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
