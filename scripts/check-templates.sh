#!/bin/sh
# Runs `weft check` on base and every stack template under the answer
# combinations the portable set introduces. Templates whose own gates need
# more combinations run those in their own proof; this is the floor.
#
#   scripts/check-templates.sh
. "$(dirname "$0")/lib.sh"

status=0
for t in "$DONOR" $(templates); do
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
exit "$status"
