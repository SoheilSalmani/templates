#!/bin/sh
# Keeps the portable patches in sync, in two steps:
#
#   1. With SKILLS_DIR given, re-records every skills-bearing patch in base
#      from that checkout of SoheilSalmani/skills (weft patch amend, replace
#      the skill directories the patch owns, weft commit). A patch whose
#      skills did not change is left untouched.
#   2. Copies every portable patch from base into each stack template, then
#      runs scripts/check-templates.sh.
#
#   scripts/sync-portable.sh [SKILLS_DIR]
#
# Requires: weft, python3. Leaves no session open. Never commits to git.
. "$(dirname "$0")/lib.sh"

SKILLS_DIR="${1:-}"

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

# The bare gate identifier of a patch (its `when`), or nothing.
gate_of() {
  python3 -c 'import json,sys; print(json.load(open(sys.argv[1])).get("when") or "")' "$1"
}

refresh_skills() {
  [ -d "$SKILLS_DIR/.agents/skills" ] || { printf 'error: %s has no .agents/skills\n' "$SKILLS_DIR" >&2; exit 1; }
  for p in "$DONOR"/patches/*.json; do
    name="$(basename "$p" .json)"
    skills="$(owned_skills "$p")"
    [ -n "$skills" ] || continue
    gate="$(gate_of "$p")"
    set -- --answer "$RECORD_ANSWER"
    [ -n "$gate" ] && set -- "$@" --answer "$gate=true"
    before="$(mktemp)"; cp "$p" "$before"
    worktree="$(cd "$DONOR" && weft patch amend "$name" "$@")"
    case "$worktree" in /*) ;; *) worktree="$DONOR/$worktree" ;; esac
    for s in $skills; do
      src="$SKILLS_DIR/.agents/skills/$s"
      [ -d "$src" ] || { printf 'error: %s owns skill %s, absent from %s\n' "$name" "$s" "$SKILLS_DIR" >&2; exit 1; }
      rm -rf "$worktree/.agents/skills/$s"
      cp -R "$src" "$worktree/.agents/skills/$s"
    done
    # An amend session always lists the patch's own files as changes, so the
    # commit is unconditional and a byte comparison tells whether anything moved.
    (cd "$worktree" && weft commit --yes >/dev/null)
    if cmp -s "$before" "$p"; then printf 'unchanged %s\n' "$name"; else printf 'refreshed %s\n' "$name"; fi
    rm -f "$before"
    # Abstraction only matches answer values; a bool gate can never leak, but
    # a distinctive project_name in skill prose would. Refuse that outright.
    if grep -q '"answer"' "$p"; then
      printf 'error: %s now carries an answer reference; a skill mentioned "%s"\n' "$name" "${RECORD_ANSWER#*=}" >&2
      exit 1
    fi
  done
}

copy_out() {
  for t in $(templates); do
    for p in $(portable_patches); do
      cp "$DONOR/patches/$p.json" "$t/patches/$p.json"
    done
    printf 'copied portable set into %s\n' "$(basename "$t")"
  done
}

[ -n "$SKILLS_DIR" ] && refresh_skills
copy_out
"$ROOT/scripts/check-templates.sh"
