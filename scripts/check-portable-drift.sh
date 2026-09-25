#!/bin/sh
# Fails when a stack template's copy of a portable patch differs from, or is
# missing against, the donor copy in base/patches. Portable patches are copied
# files, so this is the only thing that keeps them identical; an identical file
# also means an identical patch id in every template.
#
#   scripts/check-portable-drift.sh
. "$(dirname "$0")/lib.sh"

status=0
for t in $(templates); do
  name="$(basename "$t")"
  for p in $(portable_patches); do
    theirs="$t/patches/$p.json"
    if [ ! -f "$theirs" ]; then
      printf 'missing  %s/patches/%s.json\n' "$name" "$p"
      status=1
    elif ! cmp -s "$DONOR/patches/$p.json" "$theirs"; then
      printf 'differs  %s/patches/%s.json\n' "$name" "$p"
      status=1
    fi
  done
done

if [ "$status" -eq 0 ]; then
  printf 'ok: every template carries the %s portable patches byte-for-byte\n' "$(portable_patches | wc -l | tr -d ' ')"
else
  printf '\nrun scripts/sync-portable.sh to re-copy from base, then weft check each template\n' >&2
fi
exit "$status"
