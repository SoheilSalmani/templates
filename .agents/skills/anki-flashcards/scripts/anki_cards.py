#!/usr/bin/env python3
"""Read-only helper for the anki-flashcards skill.

Subcommands:
  check                     Is AnkiConnect reachable, which profile is open, and are the skill's
                            note types there and usable.
  note-type <name>          One of the skill's note types as createModel arguments, to create it.
  inspect <deck>            What note types a deck uses, with real field names.
  topics [--like PATTERN]   Existing Topic values, so you reuse instead of coining.
  lint <draft.json>         Check drafted notes against the mechanical house rules.
  inbox                     What waits in the Inbox deck and its project subdecks, which notes are
                            learnt, and where each could move.
  candidates <kind>         Notes the review history says to look at, as JSON: failing, slow,
                            sourced, random or inbox. What a run of the repair queue works through.
  queue add|list|decide|skip|report
                            The repair queue: proposals, verdicts and what they changed, kept in a
                            file outside the collection (references/repair-queue.md).

Never writes to the collection. Adding notes and creating a missing note type stay with the Anki
MCP tools, so that the approval gate in SKILL.md cannot be bypassed by a script. The repair queue
is a file of its own, which `queue` appends to.

Exit codes for lint: 0 clean, 1 errors found, 2 bad usage or unreadable draft.
With --strict, warnings also exit 1.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import random
import re
import shlex
import statistics
import sys
import unicodedata
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path

ANKI_URL = "http://localhost:8765"

# The skill's own note types: note-types.json holds each in the shape Anki's createModel takes.
ASSETS = Path(__file__).resolve().parent.parent / "assets"

# The field each of those note types shows on its own line above the question.
CONTEXT_FIELD = "Topic"

# Where a card's fact came from, shown under its answer: a link to the page, or plain text.
SOURCE_FIELD = "Source"

# A top-level deck whose name starts with "_" is an archive: nothing is added or filed there.
# Anki reads "_" in a search as any one character, so the search escapes it.
ARCHIVE_PREFIX = "_"
ARCHIVE_SEARCH = r'"deck:\_*"'

EMOJI_RE = re.compile(
    "["
    "\U0001f300-\U0001faff"
    "\U0001f000-\U0001f2ff"
    "☀-➿"
    "⬀-⯿"
    "️⃣"
    "]"
)
CLOZE_RE = re.compile(r"\{\{c(\d+)::")
# The tags the skill writes. A subject, a source and a kind of card each have a place of their own.
CLIENT_TAG_RE = re.compile(r"^client::[a-z0-9]+(-[a-z0-9]+)*$")
# On every card quick to review by its shape, and on no other: little to read, little to produce.
# The rule decides it, never a request (references/house-style.md, "Tags").
FAST_TAG = "speed::fast"
FAST_ANSWER_WORDS, FAST_ANSWER_CHARS = 3, 30
FAST_QUESTION_CHARS, FAST_CLOZE_CHARS = 100, 120
FAST_BLOCK_RE = re.compile(r"<(li|pre|table|img)\b", re.I)
FAST_NEAR_MISS_RE = re.compile(r"^(speed[-_:]*)?(fast|quick)$", re.I)
# Its answers are key combinations, short by nature, so only its question is measured.
SHORTCUT_MODEL = "Keyboard Shortcut"
# Tags Anki writes itself: for a leech, Mark Note, Tag Duplicates, and Check Database.
ANKI_TAGS = {"leech", "marked", "duplicate", "db-check"}
SOURCE_LINK_RE = re.compile(r"""<a\b[^>]*?\bhref\s*=\s*["']([^"']*)["'][^>]*>(.*?)</a>""", re.I | re.S)
BINARY_RE = re.compile(r"^\s*(true or false|vrai ou faux|yes or no)\b", re.I)
BOLD_LI_RE = re.compile(r"<li>\s*<(b|strong)>[^<]*:", re.I)
HEADING_RE = re.compile(r"</?h[1-6]\b", re.I)
CONJUNCTION_RE = re.compile(r"\b(and|or|et|ou)\b|/", re.I)
# Phrasings where a conjunction is one question, not two.
CONJUNCTION_OK_RE = re.compile(
    r"\b(difference|differences|relationship|distinction|between|versus|vs\.?|compare|"
    r"trade-?off|entre|diff[ée]rence)\b",
    re.I,
)
FILLER_RE = re.compile(
    r"\b(note that|it is important to note|keep in mind that|basically|essentially)\b", re.I
)
# "Acme R&D: what does ..." and friends. The label belongs in the context field.
TOPIC_PREFIX_RE = re.compile(r"^\s*([A-Z][^?.!:]{2,40}:)\s")
SET_SEPARATOR_RE = re.compile(r"[·•;]|,\s|<br\s*/?>", re.I)
# `&lt;` and its kind end in a semicolon that separates nothing.
ENTITY_RE = re.compile(r"&(?:[a-z][a-z0-9]*|#\d+|#x[0-9a-f]+);", re.I)
LIST_ITEM_RE = re.compile(r"<li\b[^>]*>", re.I)
ORDERED_LIST_RE = re.compile(r"<ol\b[^>]*>(.*?)</ol>", re.I | re.S)
# A deletion still open at a </li>. Anki parses cloze markers as text, not as HTML.
CLOZE_ACROSS_ITEMS_RE = re.compile(r"\{\{c\d+::(?:(?!\}\}).)*?</li>", re.I | re.S)
# One match per code block: a <pre><code> block matches once, at its outer <pre>.
CODE_SPAN_RE = re.compile(r"<(code|pre)\b[^>]*>(.*?)</\1>", re.I | re.S)
# Code laid out over several lines: a <pre> block, or a <code> span broken with <br>.
MULTILINE_CODE_RE = re.compile(
    r"<pre\b[^>]*>.*?</pre>|<code\b[^>]*>(?:(?!</code>).)*?(?:<br\s*/?>|\n)(?:(?!</code>).)*</code>",
    re.I | re.S,
)
# A "<" inside code that opens a tag other than the markup fields use: JSX, generics such as
# List<String>, placeholders such as <release>. The browser takes it for a tag and hides it.
RAW_TAG_IN_CODE_RE = re.compile(
    r"<(?!/?(?:code|pre|br|span|b|strong|i|em|u|s|sub|sup|kbd|font|div|p|ul|ol|li|a|img)\b|!--)/?[A-Za-z]"
)
# A Front that leaves the answer open: any correct example is right.
EXAMPLE_FRONT_RE = re.compile(
    r"\b(?:write|give|show|create)\s+(?:an?\s+|some\s+)?(?:examples?|samples?)\b"
    r"|\b(?:[ée]cri(?:s|vez|re)|donne[sz]?)\s+(?:un|des)\s+exemples?\b"
    r"|\bof your (?:own )?choice\b|\bde (?:votre|ton) choix\b",
    re.I,
)
CLOZE_OPEN_RE = re.compile(r"\{\{c\d+::")
# Past six lines a review takes about twice as long; past twelve about a minute, an exercise's cost.
CODE_LINES_WARN, CODE_LINES_MAX = 6, 12
# A task card ends with the parts it is graded on.
CHECK_LINE_RE = re.compile(r"\bCheck\s*:")
# The file an image shows, which Anki's duplicate check keeps when it strips the HTML.
MEDIA_SRC_RE = re.compile(r"""<img\b[^>]*?\bsrc=["']?([^"'\s>]+)""", re.I)

BACK_WARN, BACK_ERROR = 200, 400
FRONT_WARN = 160


def call(action: str, **params):
    payload = json.dumps({"action": action, "version": 6, "params": params}).encode()
    req = urllib.request.Request(ANKI_URL, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as fh:
        body = json.load(fh)
    if body.get("error"):
        raise RuntimeError(body["error"])
    return body["result"]


def connected() -> bool:
    try:
        call("version")
        return True
    except Exception:
        return False


def strip_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    text = text.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    return re.sub(r"\s+", " ", text).strip()


def normalise(text: str) -> str:
    text = strip_html(text).lower()
    text = "".join(c for c in unicodedata.normalize("NFD", text) if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9 ]", "", text)


def as_read(text: str) -> str:
    """Text as the reviewer reads it, to compare an answer with the context line: no HTML, case
    folded, without the full stop that ends a sentence. Unlike normalise(), it keeps symbols, so
    the path ~/.dbt/ stays apart from the topic dbt, and the command sqlfmt . from sqlfmt."""
    text = unicodedata.normalize("NFKC", strip_html(text)).casefold()
    return re.sub(r"(?<=\w)[.,;:!?]+$", "", text)


def duplicate_key(raw: str) -> str:
    """What Anki's duplicate check compares: the text without HTML, keeping media file names, so two
    image cards asking "What is this?" stay apart."""
    return " ".join([normalise(raw), *MEDIA_SRC_RE.findall(raw)]).strip()


def code_line_count(raw: str) -> int:
    """Lines of code in a field: every line of a <pre> block or of a <code> span broken with
    <br>, and each single-line <code> span when the field holds nothing but code. Identifiers set
    in <code> inside a sentence are not lines of code."""

    def lines(html: str) -> int:
        html = re.sub(r"<br\s*/?>", "\n", html, flags=re.I)
        return sum(1 for line in re.sub(r"<[^>]+>", "", html).split("\n") if line.strip())

    total = 0
    for block in re.findall(r"<pre\b[^>]*>(.*?)</pre>", raw, re.I | re.S):
        total += lines(block)
    rest = re.sub(r"<pre\b[^>]*>.*?</pre>", " ", raw, flags=re.I | re.S)
    spans = [match.group(2) for match in CODE_SPAN_RE.finditer(rest)]
    # A list of names in <li> items is a set, which the list check reports.
    only_code = not LIST_ITEM_RE.search(rest) and not strip_html(CODE_SPAN_RE.sub(" ", rest)).strip(" .,;:")
    for span in spans:
        if re.search(r"<br\s*/?>|\n", span, re.I) or only_code:
            total += lines(span)
    return total


def cloze_deletions(text: str) -> list[tuple[int, int, bool]]:
    """Each deletion as Anki reads it: (content start, content end, a stray "}" follows).

    "{{cN::" opens a deletion and the first "}}" closes the innermost open one, so code ending
    in "}" closes its deletion a brace early and leaves that brace outside it.
    """
    spans, stack, i = [], [], 0
    while i < len(text):
        opener = CLOZE_OPEN_RE.match(text, i)
        if opener:
            stack.append(opener.end())
            i = opener.end()
        elif text.startswith("}}", i) and stack:
            start = stack.pop()
            after = i + 2
            closes_outer = bool(stack) and text.startswith("}}", after)
            spans.append((start, i, text.startswith("}", after) and not closes_outer))
            i = after
        else:
            i += 1
    return spans


def inside_code(text: str, index: int) -> bool:
    before = text[:index]
    opened = len(re.findall(r"<(?:code|pre)\b", before, re.I))
    return opened > len(re.findall(r"</(?:code|pre)>", before, re.I))


# ---------------------------------------------------------------- check / inspect


@lru_cache(maxsize=None)
def note_types() -> dict[str, dict]:
    """The skill's note types by name, each as the arguments Anki's createModel takes."""
    with open(ASSETS / "note-types.json", encoding="utf-8") as fh:
        spec = json.load(fh)
    css = (ASSETS / spec["css"]).read_text(encoding="utf-8")
    return {note_type["modelName"]: dict(note_type, css=css) for note_type in spec["noteTypes"]}


def drift(spec: dict, model: dict) -> list[str]:
    """What keeps a note type in the collection from working as the skill's own. Styling is the
    user's to change, so only the fields, the kind of note type, the context line and the source
    line count."""
    have = [field["name"] for field in model["flds"]]
    problems = []
    for index, field in enumerate(spec["inOrderFields"]):
        if field in have:
            continue
        other = have[index] if index < len(have) and have[index] not in spec["inOrderFields"] else None
        problems.append("has %r where the skill expects %r" % (other, field) if other else "has no %r field" % field)
    if (model["type"] == 1) != spec["isCloze"]:
        problems.append("is a cloze type" if model["type"] == 1 else "is not a cloze type")
    if CONTEXT_FIELD in spec["inOrderFields"] and CONTEXT_FIELD in have:
        if not all("{{%s}}" % CONTEXT_FIELD in template["qfmt"] for template in model["tmpls"]):
            problems.append("does not show {{%s}} on every question" % CONTEXT_FIELD)
    if SOURCE_FIELD in spec["inOrderFields"] and SOURCE_FIELD in have:
        if not all("{{%s}}" % SOURCE_FIELD in template["afmt"] for template in model["tmpls"]):
            problems.append("does not show {{%s}} on every answer" % SOURCE_FIELD)
    return problems


def cmd_check(_args) -> int:
    if not connected():
        print("AnkiConnect is not reachable at " + ANKI_URL)
        print("Anki is probably closed. Launch it with:  open -a Anki")
        print("Then wait for port 8765 to answer before retrying.")
        return 1
    print("AnkiConnect: up (API version %s)" % call("version"))
    print("Profile:     %s" % call("getActiveProfile"))
    print("Decks:       %d" % len(call("deckNames")))
    print("Notes:       %d" % len(call("findNotes", query="deck:*")))

    names = set(call("modelNames"))
    present = [name for name in note_types() if name in names]
    models = {model["name"]: model for model in call("findModelsByName", modelNames=present)} if present else {}
    print("\nThe skill's note types:")
    for name, spec in note_types().items():
        if name not in models:
            print("  missing  %s  (to create it: anki_cards.py note-type %s)" % (name, shlex.quote(name)))
            continue
        problems = drift(spec, models[name])
        print("  %-7s  %s%s" % ("differs" if problems else "ok", name, ": " + "; ".join(problems) if problems else ""))
    return 0


def cmd_note_type(args) -> int:
    spec = note_types().get(args.name)
    if not spec:
        print("The skill has no note type %r. It has: %s." % (args.name, ", ".join(note_types())))
        return 2
    print(json.dumps(spec, indent=2, ensure_ascii=False))
    return 0


def cmd_inspect(args) -> int:
    if not connected():
        print("AnkiConnect is not reachable. Run 'check' first.")
        return 1
    deck = args.deck
    decks = call("deckNames")
    matches = [d for d in decks if d == deck or d.startswith(deck + "::")]
    if not matches:
        near = [d for d in decks if deck.lower() in d.lower()]
        print("No deck named %r." % deck)
        if near:
            print("Did you mean one of:")
            for d in near[:15]:
                print("  " + d)
        else:
            print("This deck does not exist yet, so it will be created on first add.")
        return 1

    query = '"deck:%s"' % deck
    ids = call("findNotes", query=query)
    print("Deck:  %s  (%d notes, %d subdecks)" % (deck, len(ids), len(matches) - 1))
    if not ids:
        print("Empty deck. Pick the note type from references/note-types.md.")
        return 0

    by_model: Counter = Counter()
    context_values: Counter = Counter()
    for start in range(0, len(ids), 100):
        for note in call("notesInfo", notes=ids[start : start + 100]):
            by_model[note["modelName"]] += 1
            value = strip_html(note["fields"].get(CONTEXT_FIELD, {}).get("value", ""))
            if value:
                context_values[value] += 1

    print("\nNote types in use:")
    for model, count in by_model.most_common():
        flag = "" if model in note_types() else "  <-- not one of the skill's note types"
        print("  %4d  %s%s" % (count, model, flag))
        try:
            print("        fields: %s" % ", ".join(call("modelFieldNames", modelName=model)))
        except RuntimeError:
            pass

    if context_values:
        print("\nExisting %s values in this deck (reuse one of these):" % CONTEXT_FIELD)
        for value, count in context_values.most_common(15):
            print("  %4d  %s" % (count, value))
    return 0


def cmd_topics(args) -> int:
    if not connected():
        print("AnkiConnect is not reachable. Run 'check' first.")
        return 1
    pattern = (args.like or "").lower()
    found: Counter = Counter()
    for model in call("modelNames"):
        if CONTEXT_FIELD not in call("modelFieldNames", modelName=model):
            continue
        ids = call("findNotes", query='note:"%s"' % model)
        for start in range(0, len(ids), 100):
            for note in call("notesInfo", notes=ids[start : start + 100]):
                value = strip_html(note["fields"][CONTEXT_FIELD]["value"])
                if value and (not pattern or pattern in value.lower()):
                    found[value] += 1
    if not found:
        print("No matching %s values." % CONTEXT_FIELD)
        return 0
    print("%s values%s:" % (CONTEXT_FIELD, " matching %r" % args.like if args.like else ""))
    for value, count in found.most_common(40):
        print("  %4d  %s" % (count, value))
    return 0


# ------------------------------------------------------------------------- lint


class Report:
    """Collects findings, grouping repeats so one systemic slip is one line."""

    def __init__(self) -> None:
        self.errors: defaultdict = defaultdict(list)
        self.warnings: defaultdict = defaultdict(list)

    def error(self, where: str, message: str) -> None:
        self.errors[message].append(where)

    def warn(self, where: str, message: str) -> None:
        self.warnings[message].append(where)

    @staticmethod
    def render(grouped: defaultdict, prefix: str, limit: int | None = 3) -> tuple[list[str], int]:
        lines, total = [], 0
        for message, wheres in grouped.items():
            total += len(wheres)
            if limit is not None and len(wheres) > limit:
                lines.append("%s%s  [%d notes: %s and %d more]" % (
                    prefix, message, len(wheres), ", ".join(wheres[:limit]), len(wheres) - limit))
            else:
                lines.append("%s%s  [%s]" % (prefix, message, ", ".join(wheres)))
        return lines, total


def load_batches(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    return data if isinstance(data, list) else [data]


def lint_text(where: str, label: str, raw: str, report: Report) -> None:
    if re.search(r"<(b|strong)\b", raw, re.I):
        report.error(where, "%s uses bold. Bold is not part of the house style." % label)
    if BOLD_LI_RE.search(raw):
        report.error(where, "%s uses a bold-header bullet list." % label)
    if HEADING_RE.search(raw):
        report.error(where, "%s contains a heading tag. Fields are not documents." % label)
    if EMOJI_RE.search(raw):
        report.error(where, "%s contains an emoji." % label)
    if "—" in raw or "–" in raw:
        report.error(where, "%s contains an em or en dash. Use a comma, period, or parentheses." % label)
    for ch, name in (("‘", "curly"), ("’", "curly"), ("“", "curly"), ("”", "curly")):
        if ch in raw:
            report.error(where, "%s contains a %s quote. Use straight quotes." % (label, name))
            break
    if FILLER_RE.search(strip_html(raw)):
        report.warn(where, "%s contains filler (\"note that\", \"basically\", and similar)." % label)
    if re.search(r"<br\s*/?>\s*<br\s*/?>", raw, re.I):
        report.warn(where, "%s has a blank line in it, which usually means two facts." % label)
    for match in CODE_SPAN_RE.finditer(raw):
        if RAW_TAG_IN_CODE_RE.search(match.group(2)):
            report.error(
                where,
                "%s has an unescaped < inside code, which Anki renders as an HTML tag and hides. "
                "Write &lt; instead." % label,
            )
            break


def lint_source(where: str, raw: str, report: Report) -> None:
    """A Source is a link whose text names the page, or plain text when there is no URL."""
    links = SOURCE_LINK_RE.findall(raw)
    if not links and re.fullmatch(r"https?://\S+", strip_html(raw), re.I):
        report.warn(
            where,
            "Source is a bare address, which the card shows as text you cannot open. Make it a "
            "link whose text is the page title.",
        )
    for href, text in links:
        if not re.match(r"https?://", href.strip(), re.I):
            report.error(where, "a Source link does not point to a web address (http or https).")
        label = strip_html(text)
        if not label or re.match(r"https?://", label, re.I):
            report.warn(
                where,
                "a Source link shows its address. Use the page title as the link text, so the "
                "source still says what it was if the link dies.",
            )


def client_tag(tag: str) -> str | None:
    """The client tag that a near miss such as client-acme or Client::Acme stands for."""
    match = re.match(r"^client(?:::|-|_)(.+)$", tag, re.I)
    return "client::" + slug(match.group(1)) if match else None


def visible(raw: str) -> str:
    """A field as the reviewer reads it. An HTML comment, which breaks up cloze syntax in code,
    disappears instead of leaving a space."""
    return strip_html(re.sub(r"<!--.*?-->", "", raw, flags=re.S))


def long_answer(raw: str) -> str | None:
    """Why one card's answer is too long to be quick, or None when it is short."""
    if FAST_BLOCK_RE.search(raw):
        return "an answer holds a list, a code block, a table or an image"
    text = visible(raw)
    if not text:
        return "an answer is empty"
    words = len(text.split())
    if words > FAST_ANSWER_WORDS:
        return "an answer runs to %d words" % words
    if len(text) > FAST_ANSWER_CHARS:
        return "an answer runs to %d characters" % len(text)
    return None


def slow_reason(model: str, fields: dict) -> str | None:
    """Why a note is not quick to review by its shape, or None when every card of it is: a short
    question and, on each card, an answer of a few words, with no list, code block, table or image
    on either side. The same fields always get the same answer."""
    def field(name: str) -> str:
        value = fields.get(name)
        return value if isinstance(value, str) else ""

    text = field("Text")
    if CLOZE_OPEN_RE.search(text):
        if FAST_BLOCK_RE.search(text):
            return "the cloze holds a list, a code block, a table or an image"
        sentence = visible(re.sub(r"\{\{c\d+::(.*?)\}\}", lambda match: match.group(1).split("::")[0], text, flags=re.S))
        if len(sentence) > FAST_CLOZE_CHARS:
            return "the cloze sentence runs to %d characters" % len(sentence)
        # One card per cloze index, and its answer is every deletion with that index.
        answers: defaultdict = defaultdict(list)
        for start, end, _ in cloze_deletions(text):
            opener = re.search(r"\{\{c(\d+)::$", text[:start])
            answers[opener.group(1) if opener else ""].append(text[start:end].split("::")[0])
        for parts in answers.values():
            reason = long_answer(" ".join(parts))
            if reason:
                return reason
        return None
    if "Front" not in fields:
        return "it has no question field"
    front = field("Front")
    if FAST_BLOCK_RE.search(front):
        return "the question holds a list, a code block, a table or an image"
    if len(visible(front)) > FAST_QUESTION_CHARS:
        return "the question runs to %d characters" % len(visible(front))
    if model == SHORTCUT_MODEL:
        return None
    if "Back" not in fields:
        return "it has no answer field"
    reason = long_answer(field("Back"))
    # A reversed note asks each side for the other, so its Front is an answer too.
    if not reason and "reverse" in model.lower():
        reason = long_answer(front)
    return reason


def speed_tags(model: str, fields: dict, tags: list) -> tuple[list, dict | None]:
    """The tags once speed::fast follows the rule, and the change that takes, if any."""
    quick = slow_reason(model, fields) is None
    if quick and FAST_TAG not in tags:
        return list(tags) + [FAST_TAG], {"add": [FAST_TAG]}
    if not quick and FAST_TAG in tags:
        return [tag for tag in tags if tag != FAST_TAG], {"remove": [FAST_TAG]}
    return list(tags), None


def lint_note(where: str, note: dict, model: str, model_fields: list[str] | None, report: Report) -> None:
    fields = note.get("fields") or {}
    if not isinstance(fields, dict) or not fields:
        report.error(where, "no fields.")
        return

    spec_fields = note_types().get(model, {}).get("inOrderFields", [])
    # A note type made before the skill had a Source field is reported once, below.
    source_missing = SOURCE_FIELD in spec_fields and model_fields is not None and SOURCE_FIELD not in model_fields
    if model_fields is not None:
        unknown = [k for k in fields if k not in model_fields and not (k == SOURCE_FIELD and source_missing)]
        for key in unknown:
            hint = ""
            if key == "Back Extra" and note_types().get(model, {}).get("isCloze"):
                hint = " This note type has no Back Extra field, and sending it rejects the whole batch."
            report.error(where, "field %r does not exist on %r.%s" % (key, model, hint))
        missing = [f for f in model_fields if f not in fields]
        if missing and model_fields:
            first = model_fields[0]
            if first in missing:
                report.error(where, "required field %r is missing." % first)

    for key, raw in fields.items():
        if not isinstance(raw, str):
            report.error(where, "field %r is not a string." % key)
            continue
        if not raw.strip() and key in (model_fields or [])[:1]:
            report.error(where, "field %r is empty." % key)
        lint_text(where, "field %r" % key, raw, report)

    if source_missing:
        report.error(
            where,
            "%r in this collection has no %s field, and AnkiConnect drops a field the note type "
            "lacks without an error. Add it first: note-types.md, \"Setting them up\"." % (model, SOURCE_FIELD),
        )
    elif SOURCE_FIELD in spec_fields:
        source = fields.get(SOURCE_FIELD)
        if not isinstance(source, str) or not strip_html(source):
            report.error(
                where,
                "no %s. Link the page the fact came from, with its title as the link text, or "
                "name the source in plain text when it has no URL." % SOURCE_FIELD,
            )
        else:
            lint_source(where, source, report)

    context_field = CONTEXT_FIELD if CONTEXT_FIELD in fields else None
    context = strip_html(fields.get(context_field, "")) if context_field else ""

    front_key = "Front" if "Front" in fields else ("Text" if "Text" in fields else None)
    front_raw = fields.get(front_key, "") if front_key else ""
    front = strip_html(front_raw)

    # The failure mode is the context used as a label prefix, not the context mentioned
    # naturally mid-sentence. "What does --frozen do in uv run?" is good writing;
    # "uv: what does --frozen do?" duplicates the rendered context line.
    if context and front and normalise(context):
        lead = re.match(r"^\s*%s\s*[:\-–,]\s*" % re.escape(context), front, re.I)
        if lead:
            report.error(
                where,
                "%s starts with the %s value as a label (%r). The note type already renders it "
                "above the question." % (front_key, context_field, context),
            )
        elif normalise(front) == normalise(context):
            report.error(where, "%s is just the %s value." % (front_key, context_field))
    # The note type shows the context value above the question on both sides of the card, so an
    # answer equal to it is read before it is recalled.
    context_key = as_read(context)
    if context_key:
        answers = [fields["Back"]] if isinstance(fields.get("Back"), str) else []
        text = fields.get("Text")
        if isinstance(text, str):
            answers += [text[start:end].split("::")[0] for start, end, _ in cloze_deletions(text)]
        if any(as_read(answer) == context_key for answer in answers):
            report.error(
                where,
                "an answer is the %s value, which the card shows above the question. Widen the %s "
                "to the subject the card belongs to." % (context_field, context_field),
            )
    if front and front_key == "Front":
        # Catches the topic prefix even on note types with no context field, which is
        # exactly where the habit comes from.
        prefix = TOPIC_PREFIX_RE.match(front_raw)
        if prefix and "<code" not in prefix.group(0):
            report.warn(
                where,
                "Front starts with %r, which looks like a topic label. Move it into the "
                "%s field and use a note type that has one."
                % (prefix.group(1).strip(), context_field or "Topic"),
            )
    # These read as questions, so they apply to a Front and not to a cloze sentence.
    if front and front_key == "Front":
        if BINARY_RE.match(front):
            report.error(where, "Front is a true-or-false card. Rephrase as an open question.")
        if re.match(r"^\s*(is|are|does|do|did|can|will|was|were|should)\b", front, re.I) and front.count("?") == 1:
            report.warn(where, "Front looks like a yes-or-no question. Rephrase as open.")
        if front.count("?") > 1:
            report.error(where, "Front contains more than one question mark. Split it.")
        # Ignore slashes inside numbers and code, where they are not conjunctions.
        prose = re.sub(r"<code>.*?</code>", " ", front_raw, flags=re.S)
        prose = re.sub(r"\d\s*/\s*\d", " ", strip_html(prose))
        if CONJUNCTION_RE.search(prose) and not CONJUNCTION_OK_RE.search(prose):
            report.warn(
                where,
                "Front contains a conjunction or slash, which often means two cards. "
                "Confirm it is one retrieval.",
            )
        if len(front) > FRONT_WARN:
            report.warn(where, "Front is %d characters. Tighten it." % len(front))

    if "Back" in fields:
        back = strip_html(fields["Back"])
        raw_back = fields["Back"]
        # Code is measured in lines below, so the character limits apply to the prose around it.
        prose = strip_html(MULTILINE_CODE_RE.sub(" ", raw_back))
        if len(prose) > BACK_ERROR:
            report.error(where, "Back has %d characters of prose. That is a bundle, not a card." % len(prose))
        elif len(prose) > BACK_WARN:
            report.warn(where, "Back has %d characters of prose. Check it is one fact." % len(prose))
        if back and front and normalise(back) and normalise(back) in normalise(front):
            report.error(where, "the answer appears inside the Front.")
        items = len(LIST_ITEM_RE.findall(raw_back))
        # Commas and semicolons inside code are syntax, not a list, and a Check: line lists what
        # the answer is graded on, not more answer.
        prose_back = CHECK_LINE_RE.split(ENTITY_RE.sub("", CODE_SPAN_RE.sub(" ", raw_back)))[0]
        if items >= 4 or (not items and len(SET_SEPARATOR_RE.findall(prose_back)) >= 3):
            report.warn(
                where,
                "Back lists four or more items. Asking for a whole set or sequence at once does "
                "not survive review. Split into one cloze card per item, or cut it.",
            )
        if re.search(r"<ol\b", raw_back, re.I) and items < 3:
            report.warn(
                where,
                "Back is an ordered list of fewer than three steps. Write them as one sentence "
                "joined with \"then\".",
            )
        code_lines = code_line_count(raw_back)
        has_check = bool(CHECK_LINE_RE.search(prose))
        if front_key == "Front" and EXAMPLE_FRONT_RE.search(front) and not has_check:
            report.warn(
                where,
                "Front asks for an example, and nothing on the card says what counts as right. "
                "End the Back with a Check: line naming what every correct answer contains, so "
                "any correct example passes, or name the task so that one answer is right.",
            )
        if code_lines > CODE_LINES_MAX:
            report.warn(
                where,
                "Back holds %d lines of code. Past twelve a review costs about a minute, the price "
                "of an exercise: cut it to the lines that make the pattern, or offer an exercise "
                "card that points to it." % code_lines,
            )
        elif code_lines > CODE_LINES_WARN and not has_check:
            report.warn(
                where,
                "Back holds %d lines of code. Past six lines a review takes about twice as long: "
                "keep it as a task card ending in a Check: line naming what every correct answer "
                "contains, or blank the line that matters in a code cloze." % code_lines,
            )

    if "Text" in fields:
        text = fields["Text"]
        indexes = sorted({int(n) for n in CLOZE_RE.findall(text)})
        if not indexes:
            report.error(where, "cloze note has no {{cN::...}} deletion in Text.")
        else:
            if text.count("{{") != text.count("}}"):
                report.error(where, "unbalanced cloze braces in Text.")
            if indexes[0] != 1:
                report.error(where, "cloze indexes start at c%d, not c1." % indexes[0])
            gaps = [i for i in range(1, indexes[-1] + 1) if i not in indexes]
            if gaps:
                report.error(where, "cloze indexes skip %s." % ", ".join("c%d" % g for g in gaps))
            if len(indexes) > 3:
                report.warn(where, "%d cloze indexes on one note. Consider splitting." % len(indexes))
            if strip_html(re.sub(r"\{\{c\d+::|\}\}", "", text)).strip() == strip_html(text).strip():
                pass
        if CLOZE_ACROSS_ITEMS_RE.search(text):
            report.error(
                where,
                "a cloze deletion runs across </li>, which Anki renders as broken HTML. "
                "Close each deletion inside its own <li>.",
            )
        hint_in_code = hint_elsewhere = stray_brace = False
        for start, end, stray in cloze_deletions(text):
            stray_brace = stray_brace or stray
            for colons in re.finditer("::", text[start:end]):
                at = start + colons.start()
                if re.search(r"\{\{c\d+$", text[:at]):
                    continue  # the "::" of a nested deletion's opener
                if inside_code(text, at):
                    hint_in_code = True
                else:
                    hint_elsewhere = True
        if hint_in_code:
            report.error(
                where,
                "a cloze deletion holds a :: inside code. Anki reads what follows as a hint, shown "
                "on the front and cut from the answer. Write :<!-- -->: instead.",
            )
        elif hint_elsewhere:
            report.warn(
                where,
                "a cloze deletion holds ::, which Anki reads as the start of a hint. Write "
                ":<!-- -->: unless the hint is intended.",
            )
        if stray_brace:
            report.error(
                where,
                "a cloze deletion ends in }, so Anki closes it a brace early and leaves the } "
                "outside. Write }<!-- -->}} instead.",
            )
        for inner in ORDERED_LIST_RE.findall(text):
            steps = [set(CLOZE_RE.findall(item)) for item in LIST_ITEM_RE.split(inner)[1:]]
            clozed = [s for s in steps if s]
            if len(clozed) >= 2 and len(set.union(*clozed)) == 1:
                report.warn(
                    where,
                    "every step of the ordered list shares one cloze index, so the card asks for "
                    "the whole sequence. Give each step its own index.",
                )

    tags = note.get("tags") or []
    if not isinstance(tags, list):
        report.error(where, "tags must be a list.")
        tags = []
    tags = [str(tag) for tag in tags]
    stray = []
    for tag in tags:
        if CLIENT_TAG_RE.match(tag) or tag == FAST_TAG:
            continue
        meant = client_tag(tag)
        if meant:
            report.error(where, "tag %r: write a client tag as %r." % (tag, meant))
        elif FAST_NEAR_MISS_RE.match(tag):
            report.error(where, "tag %r: the speed tag is %r, and only the rule in house-style.md sets it." % (tag, FAST_TAG))
        elif tag.lower() in ANKI_TAGS:
            report.error(where, "tag %r is one Anki adds itself. Never add it." % tag)
        else:
            stray.append(tag)
    if stray:
        # The tags go beside the note, so every note with stray tags shares one finding.
        report.error(
            "%s (%s)" % (where, ", ".join(stray)),
            "carries tags the skill does not write. It writes client::<name> on client work and %s "
            "where the rule marks a card quick. The subject goes in %s, where the fact came from in "
            "%s, and the kind of card is its note type." % (FAST_TAG, CONTEXT_FIELD, SOURCE_FIELD),
        )
    reason = slow_reason(model, {name: value for name, value in fields.items() if isinstance(value, str)})
    if reason is None and FAST_TAG not in tags:
        report.error(where, "the rule in house-style.md marks this card quick to review: add %r." % FAST_TAG)
    elif reason and FAST_TAG in tags:
        report.error(where, "carries %r, but the rule in house-style.md does not mark it quick (%s): remove it."
                     % (FAST_TAG, reason))


def cmd_lint(args) -> int:
    try:
        batches = load_batches(args.draft)
    except (OSError, json.JSONDecodeError) as exc:
        print("Cannot read %s: %s" % (args.draft, exc))
        return 2

    report = Report()
    have_anki = connected()
    if not have_anki:
        print("Note: Anki is closed, so field names and existing duplicates were not verified.\n")

    seen_fronts: dict[str, tuple[str, str]] = {}
    total = 0

    for batch_no, batch in enumerate(batches, 1):
        model = batch.get("modelName")
        deck = batch.get("deckName")
        notes = batch.get("notes") or []
        label = "batch %d" % batch_no
        if not model:
            report.error(label, "no modelName.")
        if not deck:
            report.error(label, "no deckName.")
        if model and model not in note_types():
            report.warn(
                label,
                "model %r is not one of the skill's note types (%s). Use it only when the user "
                "asked for it by name." % (model, ", ".join(note_types())),
            )
        if len(notes) > 100:
            report.error(label, "%d notes. addNotes takes at most 100 per call." % len(notes))

        model_fields = None
        if have_anki and model:
            try:
                model_fields = call("modelFieldNames", modelName=model)
            except RuntimeError:
                report.error(
                    label,
                    "model %r does not exist in the collection. Run 'check' to see which of the "
                    "skill's note types are missing." % model,
                )

        for i, note in enumerate(notes, 1):
            total += 1
            where = "%s note %d" % (label, i)
            lint_note(where, note, model or "", model_fields, report)

            fields = note.get("fields") or {}
            front_raw = fields.get("Front") or fields.get("Text") or ""
            context_value = fields.get(CONTEXT_FIELD, "")
            context = normalise(context_value) if isinstance(context_value, str) else ""
            key = duplicate_key(front_raw)
            if key:
                if key in seen_fronts:
                    other, other_context = seen_fronts[key]
                    if context != other_context:
                        report.error(
                            where,
                            "same Front as %s, told apart only by the context line. Put the name "
                            "that tells them apart in the question." % other,
                        )
                    else:
                        report.error(where, "duplicate Front, same as %s." % other)
                else:
                    for other_key, (other_where, _) in seen_fronts.items():
                        if similar(key, other_key):
                            report.warn(
                                where,
                                "Front is very close to %s. Sibling cards this similar interfere."
                                % other_where,
                            )
                            break
                    seen_fronts[key] = (where, context)

    print("Linted %d note(s) across %d batch(es)." % (total, len(batches)))
    error_lines, error_count = Report.render(report.errors, "  ERROR  ")
    warn_lines, warn_count = Report.render(report.warnings, "  WARN   ")
    if error_lines:
        print("\n%d error(s) in %d distinct kind(s):" % (error_count, len(error_lines)))
        for line in error_lines:
            print(line)
    if warn_lines:
        print("\n%d warning(s) in %d distinct kind(s):" % (warn_count, len(warn_lines)))
        for line in warn_lines:
            print(line)
    if not report.errors and not report.warnings:
        print("Clean. Mechanical checks only, so still run the self-audit in SKILL.md.")
    elif not report.errors:
        print("\nNo errors. Review each warning and decide, do not ignore them by default.")

    if report.errors:
        return 1
    if args.strict and report.warnings:
        return 1
    return 0


def similar(a: str, b: str) -> bool:
    """Token overlap high enough that two cards would interfere."""
    ta, tb = set(a.split()), set(b.split())
    if len(ta) < 4 or len(tb) < 4:
        return False
    overlap = len(ta & tb) / max(len(ta), len(tb))
    return overlap >= 0.8


# ------------------------------------------------------------------------ inbox

INBOX_DECK = "Inbox"
IN_INBOX = '"deck:%s"' % INBOX_DECK
# A note is learnt once every card of it reaches Anki's mature interval. It then leaves the Inbox
# for the current deck that holds the most cards with its Topic.
LEARNT_DAYS = 21
# Where a learnt note can go: not the Inbox, not an archive, not a filtered deck.
HOMES_SEARCH = "-%s -%s -deck:filtered" % (IN_INBOX, ARCHIVE_SEARCH)


def slug(text: str) -> str:
    ascii_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")


def excerpt(raw: str, width: int = 70) -> str:
    text = strip_html(raw)
    return text if len(text) <= width else text[: width - 3].rstrip() + "..."


def count(n: int, noun: str) -> str:
    return "%d %s%s" % (n, noun, "" if n == 1 else "s")


def cards_info(ids: list) -> list[dict]:
    """cardsInfo in batches, skipping the empty entries AnkiConnect returns for stale ids."""
    found: list[dict] = []
    for start in range(0, len(ids), 500):
        found += [card for card in call("cardsInfo", cards=ids[start : start + 500]) if card]
    return found


def topic_of(fields: dict) -> str:
    """The Topic as the reviewer reads it, from the fields notesInfo or cardsInfo returns."""
    value = fields.get(CONTEXT_FIELD)
    if isinstance(value, dict):
        value = value.get("value")
    return strip_html(value or "")


def learnt(cards: list[dict]) -> bool:
    """Every card that is not suspended has an interval of LEARNT_DAYS or more. Intervals come from
    the grades, not from answer times, so a review left open or answered on the move leaves them
    alone."""
    live = [card for card in cards if card.get("queue") != -1]
    return bool(live) and all(card.get("interval", 0) >= LEARNT_DAYS for card in live)


def topic_homes() -> tuple[dict, Counter]:
    """The cards a learnt note could join: case-folded Topic -> the decks holding cards with it,
    and every such deck's card count."""
    homes: defaultdict = defaultdict(Counter)
    held: Counter = Counter()
    for card in cards_info(call("findCards", query=HOMES_SEARCH)):
        held[card["deckName"]] += 1
        topic = topic_of(card["fields"])
        if topic:
            homes[topic.casefold()][card["deckName"]] += 1
    return homes, held


def home_of(topic: str, homes: dict) -> tuple[str | None, str]:
    """The deck a learnt note with this Topic moves to, or None, and why, in words about the Topic."""
    if not topic:
        return None, "the note has no %s to find a deck by" % CONTEXT_FIELD
    decks = homes.get(topic.casefold())
    if not decks:
        return None, "no current deck has it"
    ranked = decks.most_common(2)
    if len(ranked) == 2 and ranked[0][1] == ranked[1][1]:
        return None, "its cards are split evenly between %s and %s" % (ranked[0][0], ranked[1][0])
    return ranked[0][0], "most cards with it are in %s (%d)" % ranked[0]


def client_label(members: list[dict]) -> str:
    """Which client tag a project deck's notes carry: a client project's cards all carry one."""
    clients = sorted({tag for note in members for tag in note["tags"] if CLIENT_TAG_RE.match(tag)})
    tagged = sum(1 for note in members if any(CLIENT_TAG_RE.match(tag) for tag in note["tags"]))
    if not tagged:
        return "no client tag"
    if tagged == len(members) and len(clients) == 1:
        return "all tagged " + clients[0]
    return "%d tagged %s, %d without a client tag" % (tagged, " or ".join(clients), len(members) - tagged)


def cmd_inbox(_args) -> int:
    if not connected():
        print("AnkiConnect is not reachable. Run 'check' first.")
        return 1
    cards = cards_info(call("findCards", query=IN_INBOX))
    if not cards:
        print("%s is empty. Nothing to file." % INBOX_DECK)
        return 0
    due = set(call("findCards", query=IN_INBOX + " is:due"))
    overdue = call("findCards", query=IN_INBOX + " prop:due<-7")
    notes = call("notesInfo", notes=sorted({card["note"] for card in cards}))
    by_note: defaultdict = defaultdict(list)
    for card in cards:
        by_note[card["note"]].append(card)

    homes, held = topic_homes()
    filtered = {card["deckName"] for card in cards_info(call("findCards", query="deck:filtered"))}
    deck_names = sorted(call("deckNames"))
    current = [
        deck
        for deck in deck_names
        if deck != INBOX_DECK
        and not deck.startswith((ARCHIVE_PREFIX, INBOX_DECK + "::"))
        and deck not in filtered
        and (deck != "Default" or held[deck])
    ]

    today = datetime.date.today()
    added = {note["noteId"]: datetime.date.fromtimestamp(note["noteId"] / 1000) for note in notes}
    studied = [card for card in cards if card["type"] != 0]
    oldest = min(added.values())
    done = [note for note in notes if learnt(by_note[note["noteId"]])]
    movable = sum(1 for note in done if home_of(topic_of(note["fields"]), homes)[0])
    print("%s: %s, %s. %d new, %d studied, %d due now, %d of them more than a week overdue." % (
        INBOX_DECK, count(len(notes), "note"), count(len(cards), "card"),
        len(cards) - len(studied), len(studied), len(due), len(overdue)))
    print("Oldest note added %s, %s ago." % (oldest, count((today - oldest).days, "day")))
    print("Learnt, every card at %d days or more: %s, %d with a deck to move to." % (
        LEARNT_DAYS, count(len(done), "note"), movable))
    print("Current decks: %s." % (", ".join("%s (%s)" % (d, count(held[d], "card")) for d in current) or "none"))

    subdecks: defaultdict = defaultdict(list)
    for note in notes:
        deck = by_note[note["noteId"]][0]["deckName"]
        if deck != INBOX_DECK:
            subdecks[deck].append(note)
    for deck, members in sorted(subdecks.items()):
        print("Subdeck %s: %s, %s." % (deck, count(len(members), "note"), client_label(members)))
    for deck in deck_names:
        if deck.startswith(INBOX_DECK + "::") and not any(s == deck or s.startswith(deck + "::") for s in subdecks):
            print("Subdeck %s: empty, for the user to delete." % deck)

    groups: defaultdict = defaultdict(list)
    for note in notes:
        groups[topic_of(note["fields"]) if CONTEXT_FIELD in note["fields"] else None].append(note)
    report = Report()
    for topic, members in sorted(groups.items(), key=lambda item: (-len(item[1]), str(item[0]))):
        if topic is None:
            print("\nNo %s field (%s):" % (CONTEXT_FIELD, count(len(members), "note")))
        else:
            print('\n%s "%s" (%s): %s.' % (CONTEXT_FIELD, topic, count(len(members), "note"), home_of(topic, homes)[1]))
        for note in sorted(members, key=lambda n: n["noteId"]):
            mine = by_note[note["noteId"]]
            if learnt(mine):
                state = "learnt"
            elif all(card["type"] == 0 for card in mine):
                state = "new"
            else:
                state = "studied, due" if any(card["cardId"] in due for card in mine) else "studied"
            order = sorted(note["fields"], key=lambda f: note["fields"][f]["order"])
            age = (today - added[note["noteId"]]).days
            print("  %d  %-12s  added %3dd ago  %s" % (
                note["noteId"], state, age, excerpt(note["fields"][order[0]]["value"])))
            fields = {name: value["value"] for name, value in note["fields"].items()}
            lint_note("note %d" % note["noteId"], {"fields": fields, "tags": note["tags"]},
                      note["modelName"], order, report)

    lines = (Report.render(report.errors, "  ERROR  ", limit=None)[0]
             + Report.render(report.warnings, "  WARN   ", limit=None)[0])
    if lines:
        print("\nLint findings on these notes:")
        for line in lines:
            print(line)
    return 0


# ----------------------------------------------------------------- repair queue

# Mark Note, the * key while reviewing, adds this tag to ask for a repair. It comes off when the
# proposal is decided, through the MCP tools, since this script never writes to the collection.
REPAIR_TAG = "marked"
KINDS = ("failing", "slow", "sourced", "random", "inbox")
ACTIONS = ("keep", "rewrite", "split", "prerequisite", "differentiate", "fix-fact", "suspend", "delete", "move", "retag")
# The actions that change a note's own fields, and those that add notes.
FIELD_ACTIONS = {"rewrite", "differentiate", "fix-fact"}
NOTE_ACTIONS = {"split", "prerequisite"}
# The actions a rule decides rather than a diagnosis: moving a learnt note out of the Inbox, and
# making speed::fast follow its rule. Only the inbox check proposes them, ready to queue.
RULE_ACTIONS = {"move", "retag"}
VERDICTS = ("applied", "rejected")
PROPOSAL_KEYS = ("kind", "noteId", "action", "diagnosis", "signal", "fields", "newNotes", "resource", "toDeck", "tags", "model")
# Days a check leaves a note alone after closing a proposal of its own for it.
COOLDOWN_DAYS = {"failing": 30, "slow": 90, "sourced": 180, "random": 90, "inbox": 90}
# Days an applied fix gets to show its effect: no check picks the note before then, and the report
# compares this many days of answers before the proposal and after the fix.
SETTLE_DAYS = 30
# A card first answered within NEW_DAYS is new, and one failed NEW_AGAINS times since is struggling.
NEW_DAYS, NEW_AGAINS = 60, 3
# A studied card that has lapsed this often keeps failing.
MATURE_LAPSES = 2
# Slow and random draw from the cards studied this recently, and a median takes this many answers.
STUDIED_DAYS, MIN_ANSWERS = 90, 3
# In the review log: the Again button, and an answer given while the card was in review, the only
# kind whose time compares from card to card.
AGAIN, REVIEW_ANSWER = 1, 1
CLIENT_SEARCH = "tag:client::*"
DAY_MS = 86_400_000


def now_utc() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)


def parse_stamp(text: str) -> datetime.datetime:
    return datetime.datetime.fromisoformat(text)


def queue_file(path: str | None) -> Path:
    """--queue, or anki-flashcards/queue.jsonl under the XDG state directory. The queue holds card
    text, so it lives outside every repository."""
    if path:
        return Path(path).expanduser()
    state = os.environ.get("XDG_STATE_HOME") or str(Path.home() / ".local" / "state")
    return Path(state) / "anki-flashcards" / "queue.jsonl"


def read_queue(path: Path) -> list[dict]:
    """Every record, oldest first. A line that is not JSON is reported and skipped, so one bad
    write never hides the rest of the queue."""
    if not path.exists():
        return []
    records = []
    with open(path, encoding="utf-8") as fh:
        for number, line in enumerate(fh, 1):
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                print("%s line %d is not JSON, skipped." % (path, number), file=sys.stderr)
    return records


def append_queue(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write("".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records))


def proposal_states(records: list[dict]) -> list[dict]:
    """Each proposal with its status, pending, kept, applied or rejected, and when it closed."""
    verdicts = {record["id"]: record for record in records if record.get("type") == "decision"}
    states = []
    for record in records:
        if record.get("type") != "proposal":
            continue
        state = dict(record, status="pending", closedAt=None)
        verdict = verdicts.get(record["id"])
        if record.get("action") == "keep":
            state.update(status="kept", closedAt=record["at"])
        elif verdict:
            state.update(status=verdict["status"], closedAt=verdict["at"], reason=verdict.get("reason", ""))
        states.append(state)
    return states


def action_group(action: str | None) -> str:
    """A rule action rests on its own; every diagnosed action counts as a fix."""
    return action if action in RULE_ACTIONS else "fix"


def held_back(states: list[dict], kind: str, now: datetime.datetime, group: str | None = None) -> tuple[set, set]:
    """Notes a check of this kind leaves alone, as (pending, resting). A pending note waits for its
    verdict. A resting one had a proposal of this kind closed within the kind's cool-down, or a fix
    applied within SETTLE_DAYS, which needs reviews before anyone can tell whether it worked. With a
    group, only proposals in that group of actions count, so a kept diagnosis never holds back a
    move, and a move or a retag, which fixes nothing, never holds back a check."""
    pending, resting = set(), set()
    for state in states:
        if state["status"] == "pending":
            pending.add(state["noteId"])
            continue
        age = (now - parse_stamp(state["closedAt"])).days
        mine = state["kind"] == kind and (group is None or action_group(state.get("action")) == group)
        settling = (group in (None, "fix") and state["status"] == "applied"
                    and state.get("action") not in RULE_ACTIONS and age < SETTLE_DAYS)
        if (mine and age < COOLDOWN_DAYS[kind]) or settling:
            resting.add(state["noteId"])
    return pending, resting


def find(query: str, no_client: bool, action: str = "findCards") -> list[int]:
    return call(action, query=query + (" -" + CLIENT_SEARCH if no_client else ""))


def review_logs(card_ids: list[int]) -> dict[int, list[dict]]:
    """Each card's answers, oldest first. Entries with no button pressed, such as a reschedule, are
    left out."""
    logs: dict[int, list[dict]] = {}
    for start in range(0, len(card_ids), 200):
        for card, entries in call("getReviewsOfCards", cards=card_ids[start : start + 200]).items():
            logs[int(card)] = sorted((entry for entry in entries if entry.get("ease")), key=lambda entry: entry["id"])
    return logs


def day_of(ms: int) -> str:
    return datetime.date.fromtimestamp(ms / 1000).isoformat()


def failing_notes(cards: list[dict], logs: dict, marked: set, now_ms: int) -> dict[int, tuple]:
    """Notes with a card that keeps failing, or marked for repair: note id -> (rank, signal)."""
    found: dict[int, tuple] = {}
    for card in cards:
        answers = logs.get(card["cardId"], [])
        agains = sum(1 for entry in answers[1:] if entry["ease"] == AGAIN)
        last = max((entry["id"] for entry in answers if entry["ease"] == AGAIN), default=0)
        new = bool(answers) and now_ms - answers[0]["id"] <= NEW_DAYS * DAY_MS
        if new and agains >= NEW_AGAINS:
            rank, signal = (agains, last), "failed %d times since first shown on %s" % (agains, day_of(answers[0]["id"]))
        elif card["lapses"] >= MATURE_LAPSES and last:
            rank, signal = (card["lapses"], last), "lapsed %d times, last failed on %s" % (card["lapses"], day_of(last))
        elif card["note"] in marked:
            rank, signal = (0, last), ""
        else:
            continue
        if card["note"] in marked:
            rank, signal = (1,) + rank, "marked for repair" + ("; " + signal if signal else "")
        else:
            rank = (0,) + rank
        if card["note"] not in found or rank > found[card["note"]][0]:
            found[card["note"]] = (rank, signal)
    return found


def slow_notes(cards: list[dict], logs: dict, seconds: float | None) -> dict[int, tuple]:
    """Notes with a card in the slowest tenth by median answer time in review, or at --seconds and
    slower: note id -> (rank, signal)."""
    timed = []
    for card in cards:
        times = [e["time"] for e in logs.get(card["cardId"], []) if e["type"] == REVIEW_ANSWER and e["time"] > 0]
        if len(times) >= MIN_ANSWERS:
            timed.append((statistics.median(times) / 1000, len(times), card))
    if not timed:
        return {}
    medians = sorted(median for median, _, _ in timed)
    threshold = seconds if seconds is not None else medians[int(0.9 * (len(medians) - 1))]
    found: dict[int, tuple] = {}
    for median, answers, card in timed:
        if median < threshold:
            continue
        signal = "median answer %.0f s over %d reviews; this run looked at %.0f s and slower" % (median, answers, threshold)
        if card["note"] not in found or (median,) > found[card["note"]][0]:
            found[card["note"]] = ((median,), signal)
    return found


def notes_by_id(note_ids: list[int]) -> dict[int, dict]:
    found = {}
    for start in range(0, len(note_ids), 100):
        for note in call("notesInfo", notes=note_ids[start : start + 100]):
            if note:
                found[note["noteId"]] = note
    return found


def ordered_fields(note: dict) -> dict[str, str]:
    return {name: value["value"] for name, value in sorted(note["fields"].items(), key=lambda item: item[1]["order"])}


def describe(kind: str, note_ids: list[int], signals: dict[int, str]) -> list[dict]:
    """Each candidate with its note as it stands, in the order given."""
    if not note_ids:
        return []
    notes = notes_by_id(note_ids)
    by_note: defaultdict = defaultdict(list)
    for card in cards_info(call("findCards", query="nid:" + ",".join(map(str, note_ids)))):
        by_note[card["note"]].append(card)
    found = []
    for note_id in note_ids:
        note = notes.get(note_id)
        if not note:
            continue
        cards = sorted(by_note[note_id], key=lambda card: card.get("ord", 0))
        fields = ordered_fields(note)
        found.append({
            "kind": kind,
            "noteId": note_id,
            "signal": signals[note_id],
            "deck": cards[0]["deckName"] if cards else None,
            "modelName": note["modelName"],
            "topic": strip_html(fields.get(CONTEXT_FIELD, "")) or None,
            "fields": fields,
            "tags": note["tags"],
            "cardIds": [card["cardId"] for card in cards],
            "lapses": max((card["lapses"] for card in cards), default=0),
            "reviews": max((card["reps"] for card in cards), default=0),
        })
    return found


def inbox_check(args, path: Path, now: datetime.datetime, states: list[dict]) -> int:
    """The inbox check. Inbox notes with a lint error go to the agent to diagnose, like any check's
    candidates. Two kinds of proposal come from rules and are printed ready for `queue add` as they
    are: speed::fast made to follow its rule on any note, and each learnt Inbox note moved to the deck
    its Topic lives in. A note gets one proposal a run: a diagnosis first, then a retag, then a move."""
    pending, rest_fix = held_back(states, "inbox", now, "fix")
    rest_retag = held_back(states, "inbox", now, "retag")[1]
    rest_move = held_back(states, "inbox", now, "move")[1]
    by_note: defaultdict = defaultdict(list)
    for card in cards_info(find(IN_INBOX, args.no_client)):
        by_note[card["note"]].append(card)
    notes = notes_by_id(find("deck:*", args.no_client, "findNotes"))
    taken = set(pending)

    # Anki's own tags, and the speed tag, which the rule below sets, need no diagnosis.
    signals = {}
    for note_id in sorted(by_note):
        note = notes.get(note_id)
        if not note or note_id in taken or note_id in rest_fix:
            continue
        fields = ordered_fields(note)
        tags = speed_tags(note["modelName"], fields, note["tags"])[0]
        errors = sorted(message for message in lint_findings(note["modelName"], list(fields), fields, tags)[0]
                        if "Anki adds itself" not in message)
        if errors:
            signals[note_id] = "lint: " + " ".join(errors)
    eligible = list(signals)[: args.max]
    taken.update(eligible)

    proposals = []
    for note_id, note in sorted(notes.items()):
        if note_id in taken or note_id in rest_retag:
            continue
        fields = ordered_fields(note)
        change = speed_tags(note["modelName"], fields, note["tags"])[1]
        if not change:
            continue
        reason = slow_reason(note["modelName"], fields)
        proposals.append({
            "kind": "inbox", "noteId": note_id, "action": "retag", "tags": change,
            "signal": "the speed rule %s" % ("marks it quick" if reason is None else "does not mark it quick: " + reason),
            "diagnosis": "The rule in house-style.md marks it quick to review, so it gets %s." % FAST_TAG if reason is None
            else "The rule no longer marks it quick (%s), so %s comes off." % (reason, FAST_TAG),
        })
        taken.add(note_id)

    homes = topic_homes()[0]
    for note_id in sorted(by_note):
        note = notes.get(note_id)
        if not note or note_id in taken or note_id in rest_move or not learnt(by_note[note_id]):
            continue
        topic = topic_of(note["fields"])
        deck, why = home_of(topic, homes)
        about = '%s "%s": %s' % (CONTEXT_FIELD, topic, why) if topic else why
        shortest = min(card["interval"] for card in by_note[note_id] if card.get("queue") != -1)
        proposals.append({
            "kind": "inbox", "noteId": note_id, "action": "move", "toDeck": deck,
            "signal": "learnt: every card's interval is %d days or more, the shortest %d" % (LEARNT_DAYS, shortest),
            "diagnosis": "Learnt, and %s, so it moves there." % about if deck
            else "Learnt, but %s. Name a deck for it, or keep it with its project." % about,
        })
        taken.add(note_id)

    candidates = describe("inbox", eligible, signals)
    print(json.dumps({"kind": "inbox", "at": now.isoformat(), "queue": str(path), "proposals": proposals,
                      "candidates": candidates}, ensure_ascii=False, indent=1))
    moves = [proposal for proposal in proposals if proposal["action"] == "move"]
    print("inbox: %s, %d to a deck the rule found; %s; %s to diagnose of %d with lint errors." % (
        count(len(moves), "move"), sum(1 for move in moves if move["toDeck"]),
        count(len(proposals) - len(moves), "retag"), count(len(candidates), "candidate"), len(signals)),
        file=sys.stderr)
    return 0


def cmd_candidates(args) -> int:
    if not connected():
        print("AnkiConnect is not reachable at %s. Record the missed run: anki_cards.py queue skip --kind %s "
              "--reason \"AnkiConnect unreachable\"" % (ANKI_URL, args.kind), file=sys.stderr)
        return 1
    path = queue_file(args.queue)
    now = now_utc()
    states = proposal_states(read_queue(path))
    if args.kind == "inbox":
        return inbox_check(args, path, now, states)
    pending, resting = held_back(states, args.kind, now)
    if args.kind in ("failing", "slow"):
        if args.kind == "failing":
            marked_cards = set(find("tag:%s -is:suspended" % REPAIR_TAG, args.no_client))
            cards = cards_info(sorted(set(find("rated:%d:1 -is:suspended" % args.days, args.no_client)) | marked_cards))
            marked = {card["note"] for card in cards if card["cardId"] in marked_cards}
            ranked = failing_notes(cards, review_logs([card["cardId"] for card in cards]), marked, int(now.timestamp() * 1000))
        else:
            marked = set()
            cards = cards_info(find("rated:%d -is:suspended" % STUDIED_DAYS, args.no_client))
            ranked = slow_notes(cards, review_logs([card["cardId"] for card in cards]), args.seconds)
        # A note the user marked waits only for its pending proposal: marking it again asks again.
        eligible = [note for note in ranked if note not in pending and (note in marked or note not in resting)]
        eligible.sort(key=lambda note: ranked[note][0], reverse=True)
        held, available = len(ranked) - len(eligible), len(eligible)
        signals = {note: ranked[note][1] for note in eligible}
    else:
        if args.kind == "sourced":
            query, signal = '"%s:_*" -is:suspended' % SOURCE_FIELD, "has a %s to check the card against" % SOURCE_FIELD
        else:
            query, signal = "rated:%d -is:suspended" % STUDIED_DAYS, "drawn at random from the notes studied in the last %d days" % STUDIED_DAYS
        notes = find(query, args.no_client, "findNotes")
        pool = [note for note in notes if note not in pending and note not in resting]
        eligible = random.sample(pool, min(args.max, len(pool)))
        held, available = len(notes) - len(pool), len(pool)
        signals = {note: signal for note in eligible}
    candidates = describe(args.kind, eligible[: args.max], signals)
    print(json.dumps({"kind": args.kind, "at": now.isoformat(), "queue": str(path), "candidates": candidates},
                     ensure_ascii=False, indent=1))
    print("%s: %s of %d eligible, %d held back by the queue." % (
        args.kind, count(len(candidates), "candidate"), available, held), file=sys.stderr)
    return 0


@lru_cache(maxsize=None)
def field_names(model: str) -> tuple[str, ...]:
    return tuple(call("modelFieldNames", modelName=model))


def lint_findings(model: str, names: list[str], fields: dict, tags: list) -> tuple[set, set]:
    report = Report()
    lint_note("", {"fields": fields, "tags": tags}, model, names, report)
    return set(report.errors), set(report.warnings)


def check_field_change(where: str, note: dict, fields, errors: list, warnings: list) -> dict | None:
    """A field change may not bring a lint error the note did not have. Old gaps, such as a Source
    nobody can name any more, are the user's to see, not a reason to refuse the fix. Returns the
    speed::fast change the new fields call for, which is applied with them."""
    if not isinstance(fields, dict) or not fields:
        errors.append("%s: give the new field values in fields." % where)
        return None
    before = ordered_fields(note)
    unknown = [name for name in fields if name not in before]
    if unknown:
        errors.append("%s: %s not a field of %r." % (where, ", ".join(map(repr, unknown)), note["modelName"]))
        return None
    after = dict(before)
    after.update(fields)
    if after == before:
        errors.append("%s: the fields are unchanged." % where)
        return None
    after_tags, change = speed_tags(note["modelName"], after, note["tags"])
    old_errors, old_warnings = lint_findings(note["modelName"], list(before), before, note["tags"])
    new_errors, new_warnings = lint_findings(note["modelName"], list(before), after, after_tags)
    errors += ["%s: %s" % (where, message) for message in sorted(new_errors - old_errors)]
    warnings += ["%s: %s" % (where, message) for message in sorted(new_warnings - old_warnings)]
    return change


def check_move(where: str, note: dict, to_deck, errors: list) -> None:
    """A move takes a learnt note out of the Inbox: to a current deck, or to none yet, when the user
    names one at approval."""
    if to_deck is not None and (not isinstance(to_deck, str) or not to_deck.strip()):
        errors.append("%s: toDeck is a deck name, or null for the user to name one." % where)
        return
    if to_deck and (to_deck.startswith(ARCHIVE_PREFIX) or to_deck == INBOX_DECK or to_deck.startswith(INBOX_DECK + "::")):
        errors.append("%s: %s is an archive or the Inbox, where a learnt note never goes." % (where, to_deck))
    if not learnt(cards_info(note.get("cards") or [])):
        errors.append("%s: not learnt yet, a card's interval is under %d days." % (where, LEARNT_DAYS))


def check_retag(where: str, note: dict, tags, errors: list) -> None:
    """A retag makes speed::fast follow its rule, and changes nothing else."""
    fields = ordered_fields(note)
    change = speed_tags(note["modelName"], fields, note["tags"])[1]
    if not change:
        errors.append("%s: %s already follows its rule on this note." % (where, FAST_TAG))
    elif tags != change:
        errors.append("%s: the rule's tag change is %s, not %s." % (where, json.dumps(change), json.dumps(tags)))


def check_new_notes(where: str, note: dict, action: str, proposal: dict, errors: list, warnings: list) -> None:
    """New notes are linted as drafts. A split may carry its note's old gaps, such as a missing
    Source; a prerequisite is a new fact and needs everything a new card needs."""
    new_notes = proposal.get("newNotes")
    resource = proposal.get("resource")
    if action == "prerequisite" and not new_notes and isinstance(resource, str) and resource.strip():
        return
    if not isinstance(new_notes, list) or not new_notes:
        errors.append("%s: a %s needs newNotes%s." % (where, action, ", or a resource to read" if action == "prerequisite" else ""))
        return
    inherited: set = set()
    if action == "split":
        current = ordered_fields(note)
        inherited, _ = lint_findings(note["modelName"], list(current), current, speed_tags(note["modelName"], current, [])[0])
    for number, new in enumerate(new_notes, 1):
        label = "%s, new note %d" % (where, number)
        if not isinstance(new, dict) or not new.get("deckName") or not new.get("modelName"):
            errors.append("%s: needs deckName, modelName and fields." % label)
            continue
        if new["deckName"].startswith(ARCHIVE_PREFIX):
            errors.append("%s: %s is archived. New notes go to %s or a current deck." % (label, new["deckName"], INBOX_DECK))
        try:
            names = field_names(new["modelName"])
        except RuntimeError:
            errors.append("%s: the note type %r does not exist." % (label, new["modelName"]))
            continue
        new_errors, new_warnings = lint_findings(new["modelName"], list(names), new.get("fields") or {}, new.get("tags") or [])
        errors += ["%s: %s" % (label, message) for message in sorted(new_errors - inherited)]
        warnings += ["%s: %s" % (label, message) for message in sorted(new_warnings)]


def cmd_queue_add(args) -> int:
    try:
        text = sys.stdin.read() if args.file == "-" else Path(args.file).read_text(encoding="utf-8")
        data = json.loads(text)
    except (OSError, json.JSONDecodeError) as exc:
        print("Cannot read %s: %s" % (args.file, exc))
        return 2
    batch = data if isinstance(data, list) else [data]
    if not connected():
        print("AnkiConnect is not reachable. A proposal is checked against its note as it stands, so add it "
              "while Anki is open.")
        return 1
    path = queue_file(args.queue)
    pending = {state["noteId"]: state["id"] for state in proposal_states(read_queue(path)) if state["status"] == "pending"}
    notes = notes_by_id([p["noteId"] for p in batch if isinstance(p, dict) and isinstance(p.get("noteId"), int)])
    now = now_utc()
    errors: list[str] = []
    warnings: list[str] = []
    records: list[dict] = []
    seen: set = set()
    for number, proposal in enumerate(batch, 1):
        where = "proposal %d" % number
        if not isinstance(proposal, dict):
            errors.append("%s is not a JSON object." % where)
            continue
        note = notes.get(proposal.get("noteId"))
        if not note:
            errors.append("%s: noteId %r is not a note in the collection." % (where, proposal.get("noteId")))
            continue
        note_id, kind, action = note["noteId"], proposal.get("kind"), proposal.get("action")
        where = "proposal %d (note %d)" % (number, note_id)
        if kind not in KINDS:
            errors.append("%s: kind must be one of %s." % (where, ", ".join(KINDS)))
        if action not in ACTIONS:
            errors.append("%s: action must be one of %s." % (where, ", ".join(ACTIONS)))
        if not isinstance(proposal.get("diagnosis"), str) or not proposal["diagnosis"].strip():
            errors.append("%s: no diagnosis. Say what is wrong, or why the card is fine as it is." % where)
        if note_id in pending:
            errors.append("%s: already pending as %s." % (where, pending[note_id]))
        if note_id in seen:
            errors.append("%s: a second proposal for this note in one batch." % where)
        seen.add(note_id)
        tag_change = None
        if action in FIELD_ACTIONS:
            tag_change = check_field_change(where, note, proposal.get("fields"), errors, warnings)
        elif action in NOTE_ACTIONS:
            check_new_notes(where, note, action, proposal, errors, warnings)
        elif action == "move":
            check_move(where, note, proposal.get("toDeck"), errors)
        elif action == "retag":
            check_retag(where, note, proposal.get("tags"), errors)
        if action in RULE_ACTIONS and kind != "inbox":
            errors.append("%s: a %s comes from the inbox check, which decides it by rule." % (where, action))
        record = {"type": "proposal", "id": "%s-%d-%s" % (kind, note_id, now.strftime("%Y%m%d%H%M%S")), "at": now.isoformat()}
        record.update((key, proposal[key]) for key in PROPOSAL_KEYS if key in proposal)
        # A field fix carries the speed::fast change its new fields call for, applied with it.
        if action in FIELD_ACTIONS:
            record.pop("tags", None)
            if tag_change:
                record["tags"] = tag_change
        record["topic"] = strip_html(ordered_fields(note).get(CONTEXT_FIELD, "")) or None
        record["cardIds"] = note.get("cards") or []
        records.append(record)
    for line in warnings:
        print("WARN   " + line)
    if errors:
        for line in errors:
            print("ERROR  " + line)
        print("Nothing queued. Fix the errors and add the whole batch again.")
        return 1
    append_queue(path, records)
    kept = sum(1 for record in records if record.get("action") == "keep")
    print("Queued %s in %s: %d to approve, %d kept as they are." % (
        count(len(records), "proposal"), path, len(records) - kept, kept))
    return 0


def announce_reports(path: Path, records: list[dict]) -> None:
    """Point at the reports saved since the last verdict, which the user has not seen yet."""
    folder = path.parent / "reports"
    if not folder.is_dir():
        return
    last = max((parse_stamp(record["at"]) for record in records if record.get("type") == "decision"), default=None)
    for report in sorted(folder.glob("*.md")):
        saved = datetime.datetime.fromtimestamp(report.stat().st_mtime, datetime.timezone.utc)
        if last is None or saved > last:
            print("Report saved %s since the last verdict, show it first: %s" % (saved.date(), report))


def cmd_queue_list(args) -> int:
    path = queue_file(args.queue)
    records = read_queue(path)
    statuses = {"pending": {"pending"}, "decided": set(VERDICTS), "kept": {"kept"}}.get(args.status, {"pending", "kept", *VERDICTS})
    topic = (args.topic or "").casefold()
    shown = [
        state for state in proposal_states(records)
        if state["status"] in statuses
        and (not args.kind or state["kind"] == args.kind)
        and topic in (state.get("topic") or "").casefold()
    ]
    if args.json:
        print(json.dumps(shown, ensure_ascii=False, indent=1))
        return 0
    if args.status == "pending":
        announce_reports(path, records)
    if not shown:
        print("No %s proposals in %s." % (args.status, path))
        return 0
    for state in shown:
        print("%s  %s  note %d%s" % (state["id"], state["action"], state["noteId"], "  " + state["topic"] if state.get("topic") else ""))
        print("    " + state.get("diagnosis", ""))
        if state.get("action") == "move":
            print("    to %s" % (state.get("toDeck") or "a deck the user names"))
        if state.get("tags"):
            print("    tags: %s" % "; ".join("%s %s" % (verb, ", ".join(values)) for verb, values in state["tags"].items()))
        if state["status"] in VERDICTS:
            print("    %s%s" % (state["status"], ": " + state["reason"] if state.get("reason") else ""))
    print("\n%s. The proposed fields and notes are in --json." % count(len(shown), "proposal"))
    return 0


def cmd_queue_decide(args) -> int:
    path = queue_file(args.queue)
    states = {state["id"]: state for state in proposal_states(read_queue(path))}
    errors = []
    for proposal_id in args.ids:
        state = states.get(proposal_id)
        if not state:
            errors.append("%s is not in %s." % (proposal_id, path))
        elif state["status"] != "pending":
            errors.append("%s is already %s." % (proposal_id, state["status"]))
    reason = (args.reason or "").strip()
    if args.status == "rejected" and not reason:
        errors.append("A rejection needs --reason, in the user's words. Later runs read it to learn what they want.")
    if errors:
        for line in errors:
            print("ERROR  " + line)
        return 1
    at = now_utc().isoformat()
    append_queue(path, [{"type": "decision", "id": proposal_id, "at": at, "status": args.status, "reason": reason}
                        for proposal_id in args.ids])
    print("Recorded %s as %s." % (count(len(args.ids), "proposal"), args.status))
    note_ids = sorted({states[proposal_id]["noteId"] for proposal_id in args.ids})
    if not connected():
        print("Anki is closed, so the %r tag was not checked. Once it is open, remove it from %s with "
              "mcp__anki__removeTags." % (REPAIR_TAG, ", ".join(map(str, note_ids))))
        return 0
    marked = [note["noteId"] for note in notes_by_id(note_ids).values() if REPAIR_TAG in note["tags"]]
    if marked:
        print("Remove the %r tag from %s with mcp__anki__removeTags." % (REPAIR_TAG, ", ".join(map(str, marked))))
    return 0


def cmd_queue_skip(args) -> int:
    path = queue_file(args.queue)
    append_queue(path, [{"type": "skip", "at": now_utc().isoformat(), "kind": args.kind, "reason": args.reason}])
    print("Recorded a %s run that did not happen, in %s." % (args.kind, path))
    return 0


def share(part: int, whole: int) -> str:
    return "%d of %d (%d%%)" % (part, whole, round(100 * part / whole)) if whole else "-"


def fix_effects(states: list[dict], now: datetime.datetime) -> list[str]:
    """Again presses per answer in the SETTLE_DAYS before each proposal and after its fix, for the
    fixes that changed a note's fields and have had that long to show."""
    window = datetime.timedelta(days=SETTLE_DAYS)
    settled = [
        state for state in states
        if state["status"] == "applied" and state.get("action") in FIELD_ACTIONS and state.get("cardIds")
        and now - parse_stamp(state["closedAt"]) >= window
    ]
    if not settled:
        return ["No field fix has had %d days to show its effect yet." % SETTLE_DAYS]
    if not connected():
        return ["Anki is closed, so what the applied fixes changed was not measured."]
    logs = review_logs(sorted({card for state in settled for card in state["cardIds"]}))
    lines = ["| Check | Fixes | Again before | Again after |", "| --- | --- | --- | --- |"]
    for kind in KINDS:
        mine = [state for state in settled if state["kind"] == kind]
        if not mine:
            continue
        tally = {"before": [0, 0], "after": [0, 0]}
        for state in mine:
            proposed, fixed = parse_stamp(state["at"]), parse_stamp(state["closedAt"])
            spans = {"before": (proposed - window, proposed), "after": (fixed, fixed + window)}
            for card in state["cardIds"]:
                for entry in logs.get(card, []):
                    moment = datetime.datetime.fromtimestamp(entry["id"] / 1000, datetime.timezone.utc)
                    for side, (start, end) in spans.items():
                        if start <= moment < end:
                            tally[side][0] += entry["ease"] == AGAIN
                            tally[side][1] += 1
        lines.append("| %s | %d | %s | %s |" % (kind, len(mine), share(*tally["before"]), share(*tally["after"])))
    return lines


def cmd_queue_report(args) -> int:
    path = queue_file(args.queue)
    records = read_queue(path)
    states = proposal_states(records)
    skips = [record for record in records if record.get("type") == "skip"]
    now = now_utc()
    since = now - datetime.timedelta(days=args.days)
    lines = [
        "# Repair queue, %s" % now.date(),
        "",
        "The last %d days of %s." % (args.days, path),
        "",
        "| Check | Checked | Needed a change | Accepted | Pending | Runs without Anki | Last run |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for kind in KINDS:
        recent = [state for state in states if state["kind"] == kind and parse_stamp(state["at"]) >= since]
        changes = [state for state in recent if state["action"] != "keep"]
        decided = [state for state in changes if state["status"] in VERDICTS]
        applied = sum(1 for state in decided if state["status"] == "applied")
        waiting = sum(1 for state in changes if state["status"] == "pending")
        missed = sum(1 for record in skips if record.get("kind") == kind and parse_stamp(record["at"]) >= since)
        last = max([state["at"] for state in states if state["kind"] == kind]
                   + [record["at"] for record in skips if record.get("kind") == kind], default="")
        lines.append("| %s | %d | %s | %s | %d | %d | %s |" % (
            kind, len(recent), share(len(changes), len(recent)), share(applied, len(decided)), waiting, missed,
            last[:10] or "never"))
    lines += ["", "## What the fixes changed", ""] + fix_effects(states, now)
    text = "\n".join(lines)
    print(text)
    if args.save:
        out = path.parent / "reports" / ("%s.md" % now.date().isoformat())
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text + "\n", encoding="utf-8")
        print("\nSaved to %s." % out)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("check", help="is AnkiConnect up, and are the skill's note types there").set_defaults(func=cmd_check)

    p_note_type = sub.add_parser("note-type", help="createModel arguments for one of the skill's note types")
    p_note_type.add_argument("name")
    p_note_type.set_defaults(func=cmd_note_type)

    p_inspect = sub.add_parser("inspect", help="note types and context values used by a deck")
    p_inspect.add_argument("deck")
    p_inspect.set_defaults(func=cmd_inspect)

    p_topics = sub.add_parser("topics", help="existing Topic values")
    p_topics.add_argument("--like", help="substring filter")
    p_topics.set_defaults(func=cmd_topics)

    p_lint = sub.add_parser("lint", help="check a draft JSON file")
    p_lint.add_argument("draft")
    p_lint.add_argument("--strict", action="store_true", help="exit non-zero on warnings too")
    p_lint.set_defaults(func=cmd_lint)

    sub.add_parser("inbox", help="what waits in the Inbox, and where it could go").set_defaults(func=cmd_inbox)

    p_candidates = sub.add_parser("candidates", help="notes worth a look, from their reviews or the Inbox, as JSON")
    p_candidates.add_argument("kind", choices=KINDS)
    p_candidates.add_argument("--max", type=int, default=20, help="at most this many notes to diagnose (default 20)")
    p_candidates.add_argument("--days", type=int, default=7, help="failing: failures of the last N days (default 7)")
    p_candidates.add_argument("--seconds", type=float, help="slow: this median answer time and slower, not the slowest tenth")
    p_candidates.add_argument("--no-client", action="store_true", help="leave out notes tagged client::<name>")
    p_candidates.add_argument("--queue", help="queue file (default %s)" % queue_file(None))
    p_candidates.set_defaults(func=cmd_candidates)

    p_queue = sub.add_parser("queue", help="the repair queue: proposals, verdicts, missed runs and the report")
    queue_sub = p_queue.add_subparsers(dest="queue_command", required=True)
    where = argparse.ArgumentParser(add_help=False)
    where.add_argument("--queue", help="queue file (default %s)" % queue_file(None))

    q_add = queue_sub.add_parser("add", parents=[where], help="queue proposals from a JSON file, or - for stdin")
    q_add.add_argument("file")
    q_add.set_defaults(func=cmd_queue_add)

    q_list = queue_sub.add_parser("list", parents=[where], help="proposals by status")
    q_list.add_argument("--status", choices=("pending", "decided", "kept", "all"), default="pending")
    q_list.add_argument("--kind", choices=KINDS)
    q_list.add_argument("--topic", help="Topic substring, to read the verdicts given on a subject")
    q_list.add_argument("--json", action="store_true", help="whole records, with the proposed fields and notes")
    q_list.set_defaults(func=cmd_queue_list)

    q_decide = queue_sub.add_parser("decide", parents=[where], help="record the user's verdict on proposals")
    q_decide.add_argument("ids", nargs="+")
    q_decide.add_argument("--status", choices=VERDICTS, required=True)
    q_decide.add_argument("--reason", help="why, in the user's words; a rejection needs one")
    q_decide.set_defaults(func=cmd_queue_decide)

    q_skip = queue_sub.add_parser("skip", parents=[where], help="record a run that could not reach Anki")
    q_skip.add_argument("--kind", choices=KINDS, required=True)
    q_skip.add_argument("--reason", required=True)
    q_skip.set_defaults(func=cmd_queue_skip)

    q_report = queue_sub.add_parser("report", parents=[where], help="what each check found, and what the fixes changed")
    q_report.add_argument("--days", type=int, default=30, help="the period of the table (default 30)")
    q_report.add_argument("--save", action="store_true", help="also write it to reports/ beside the queue file")
    q_report.set_defaults(func=cmd_queue_report)

    args = parser.parse_args()
    try:
        return args.func(args)
    except urllib.error.URLError:
        print("Cannot reach AnkiConnect at %s. Is Anki running?" % ANKI_URL)
        return 1
    except RuntimeError as exc:
        print("AnkiConnect error: %s" % exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
