#!/bin/sh
# Re-records the skills patches in base from a checkout of
# SoheilSalmani/skills, then runs scripts/check-templates.sh. Every other
# template extends base, so it takes the new skills without any copying.
#
# For each base patch that installs skills, opens `weft patch amend` with the
# answers that switch the patch on, replaces the skill directories the patch
# owns with the checkout's, and commits. A patch whose skills did not change is
# left untouched. A patch whose skills the checkout does not have is kept as
# recorded: writing-slides lives here, extended by the slides template's
# features.
#
#   scripts/sync-skills.sh SKILLS_DIR
#
# Requires: weft, python3. Leaves no session open. Never commits to git.
. "$(dirname "$0")/lib.sh"

SKILLS_DIR="${1:?usage: scripts/sync-skills.sh SKILLS_DIR}"
[ -d "$SKILLS_DIR/.agents/skills" ] || { printf 'error: %s has no .agents/skills\n' "$SKILLS_DIR" >&2; exit 1; }

# Skill directory names a patch owns, from the paths of its create_file ops.
owned_skills() {
  python3 - "$1" <<'PY'
import json, sys
patch = json.load(open(sys.argv[1]))
names = set()
for op in patch.get("ops") or []:
    path = op.get("path")
    if isinstance(path, list):
        path = "".join(s if isinstance(s, str) else "" for s in path)
    if path and path.startswith(".agents/skills/"):
        names.add(path.split("/")[2])
print("\n".join(sorted(names)))
PY
}

# The answer that switches a patch on, from its `when`: nothing when it has
# none, `use_linear=true` for a bool, `stack_skills=dbt` for a choice test.
gate_answer() {
  python3 - "$1" <<'PY'
import json, re, sys
when = json.load(open(sys.argv[1])).get("when") or ""
choice = re.fullmatch(r"'([^']+)' in ([a-z_]+)", when)
if choice:
    print(f"{choice.group(2)}={choice.group(1)}")
elif re.fullmatch(r"[a-z_]+", when):
    print(f"{when}=true")
elif when:
    sys.exit(f"error: cannot open the gate `{when}` of {sys.argv[1]}")
PY
}

for p in "$BASE"/patches/*.json; do
  name="$(basename "$p" .json)"
  skills="$(owned_skills "$p")"
  [ -n "$skills" ] || continue
  present="" absent=""
  for s in $skills; do
    if [ -d "$SKILLS_DIR/.agents/skills/$s" ]; then present="$present $s"; else absent="$absent $s"; fi
  done
  if [ -z "$present" ]; then
    printf 'kept %s: %s not in %s\n' "$name" "${absent# }" "$SKILLS_DIR"
    continue
  fi
  [ -z "$absent" ] || { printf 'error: %s owns%s, absent from %s\n' "$name" "$absent" "$SKILLS_DIR" >&2; exit 1; }
  gate="$(gate_answer "$p")"
  set -- --answer "$SKILLS_RECORD_ANSWER"
  [ -n "$gate" ] && set -- "$@" --answer "$gate"
  before="$(mktemp)"; cp "$p" "$before"
  worktree="$(cd "$BASE" && weft patch amend "$name" "$@")"
  case "$worktree" in /*) ;; *) worktree="$BASE/$worktree" ;; esac
  for s in $skills; do
    rm -rf "$worktree/.agents/skills/$s"
    cp -R "$SKILLS_DIR/.agents/skills/$s" "$worktree/.agents/skills/$s"
  done
  # An amend session always lists the patch's own files as changes, so the
  # commit is unconditional and a byte comparison tells whether anything moved.
  (cd "$worktree" && weft commit --yes >/dev/null)
  if cmp -s "$before" "$p"; then printf 'unchanged %s\n' "$name"; else printf 'refreshed %s\n' "$name"; fi
  rm -f "$before"
  # Abstraction only matches answer values; a bool gate can never leak, but
  # a distinctive project_name in skill prose would. Refuse that outright.
  if grep -q '"answer"' "$p"; then
    printf 'error: %s now carries an answer reference; a skill mentioned "%s"\n' "$name" "${SKILLS_RECORD_ANSWER#*=}" >&2
    exit 1
  fi
done

"$ROOT/scripts/check-templates.sh"
