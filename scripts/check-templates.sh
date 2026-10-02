#!/bin/sh
# Runs `weft check` on base and every template that extends it under the
# answer combinations base's questions introduce, fails any base patch that
# installs skills and carries an answer reference, then renders each template
# to prove what the commit_* answers promise. Templates whose own gates need
# more combinations run those in their own proof; this is the floor.
#
#   scripts/check-templates.sh
. "$(dirname "$0")/lib.sh"

status=0
for t in "$BASE" $(templates); do
  name="$(basename "$t")"
  check_combinations | while IFS= read -r combo; do
    # shellcheck disable=SC2086  # the combination is a list of flags
    if out="$(weft check "$t" --answer "$RECORD_ANSWER" $combo 2>&1)"; then
      printf 'ok    %-10s %s\n' "$name" "${combo:-defaults}"
    else
      printf 'FAIL  %-10s %s\n%s\n' "$name" "${combo:-defaults}" "$out"
      exit 1
    fi
  done || status=1
done

# Each stack offers only its own stack skills, so only base can switch them
# all on at once, and prove the stack skills patches commute with the rest.
if out="$(weft check "$BASE" --answer "$RECORD_ANSWER" --answer stack_skills=dbt,slides 2>&1)"; then
  printf 'ok    %-10s %s\n' base "--answer stack_skills=dbt,slides"
else
  printf 'FAIL  %-10s %s\n%s\n' base "--answer stack_skills=dbt,slides" "$out"
  status=1
fi

# Skill prose is recorded word for word, under the name SKILLS_RECORD_ANSWER
# sets, which no skill may quote. A skills patch that carries an answer
# reference was recorded under another name, or a skill quoted that one.
for p in "$BASE"/patches/*.json; do
  grep -q '"\.agents/skills/' "$p" || continue
  if grep -q '"answer"' "$p"; then
    printf 'FAIL  %-10s %s carries an answer reference; record skills under "%s"\n' base "$(basename "$p")" "${SKILLS_RECORD_ANSWER#*=}"
    status=1
  fi
done

# The commit_* answers reach .gitignore, the README and slides' talk guide
# through hand-written expr segments, which `weft patch amend` flattens into
# literal text, and `weft check` would not notice. So render for real and ask
# git: with every commit_* answer false the tooling is rendered but ignored, and
# no committed file says to run mise or points at the skills; with the defaults,
# git would commit it all.
tooling='^(\.agents/|\.claude/skills/|\.mcp\.json$|\.codex/|\.omp/|mise\.toml$|AGENTS\.md$|CLAUDE\.md$|paseo\.json$|\.weft/)'
render() {
  src="$1" dest="$2"
  shift 2
  weft new "$src" "$dest" --answer "$RECORD_ANSWER" "$@" --skip-tasks --non-interactive >/dev/null 2>&1 &&
    git -C "$dest" init -q
}
scratch="$(mktemp -d)"
trap 'rm -rf "$scratch"' EXIT
for t in "$BASE" $(templates); do
  name="$(basename "$t")"
  private="$scratch/$name-private" committed="$scratch/$name-committed"
  # shellcheck disable=SC2086  # PRIVATE_ANSWERS is a list of flags
  if ! render "$t" "$private" $PRIVATE_ANSWERS || ! render "$t" "$committed"; then
    printf 'FAIL  %-10s could not render\n' "$name"
    status=1
    continue
  fi
  problems="$(
    git -C "$private" ls-files --others --exclude-standard | grep -E "$tooling" | sed 's/^/committed: /'
    for f in paseo.json mise.toml AGENTS.md .agents/skills; do
      [ -e "$private/$f" ] || echo "not rendered: $f"
    done
    git -C "$private" grep -l --untracked 'mise install' | sed 's/^/says mise install: /'
    git -C "$private" grep -l --untracked '\.agents/skills' | sed 's/^/points at the skills: /'
    git -C "$committed" check-ignore paseo.json mise.toml AGENTS.md .agents/skills | sed 's/^/ignored by default: /'
  )" || true
  if [ -n "$problems" ]; then
    printf 'FAIL  %-10s commit_* answers (%s problems)\n' "$name" "$(printf '%s\n' "$problems" | wc -l | tr -d ' ')"
    printf '%s\n' "$problems" | head -n 10
    status=1
  else
    printf 'ok    %-10s commit_* answers keep the tooling out of git\n' "$name"
  fi
done
exit "$status"
