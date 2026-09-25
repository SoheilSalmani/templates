#!/bin/sh
# Shared helpers for the scripts in this directory. Source it; do not run it.
set -eu

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DONOR="$ROOT/base"
RECORD_ANSWER="project_name=Demo Service"

# Every template directory except the donor: a directory holding weft.toml.
templates() {
  for t in "$ROOT"/*/weft.toml; do
    d="$(dirname "$t")"
    [ "$d" = "$DONOR" ] && continue
    printf '%s\n' "$d"
  done
}

# The portable set: every patch in base except its root, which is the one
# patch that is not copied out (it owns README.md, .gitignore and the git hooks).
portable_patches() {
  for p in "$DONOR"/patches/*.json; do
    n="$(basename "$p" .json)"
    [ "$n" = "base" ] && continue
    printf '%s\n' "$n"
  done
}

# Answer combinations every template must pass `weft check` under. Each line
# is a set of --answer flags; the template's own gates are its author's job.
check_combinations() {
  printf '%s\n' \
    "" \
    "--answer use_linear=false --answer use_jira=true" \
    "--answer use_github=false --answer use_linear=false" \
    "--answer use_anki=true --answer use_obsidian=true --answer use_jira=true"
}
