#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Check preregistration ordering from an extract_evidence.py manifest.

The skill's central promise is that predictions are written before
cause-outcome relationships are inspected. A ledger emitted only in the final
report cannot demonstrate that, so this checker reads the transcript manifest
(TSV from ``extract_evidence.py manifest``) and establishes the ordering
facts: the ordinal of the first *executed* Write/Edit whose target matches
--ledger-pattern, and every earlier tool_use that must be classified.

It deliberately does not judge whether a pre-write data touch was orientation
(schema, row counts, coverage -- permitted before preregistration) or analysis
(a cause-outcome relationship -- forbidden). That line is semantic, so the
checker lists the touches verbatim and the scorer classifies each in the
evidence artifact. Data touches count on attempt, not execution: an errored
read still exposed intent to look.

Fail-closed behaviors:

- The manifest read itself is guarded: an unreadable or undecodable file is
  UNVERIFIABLE (exit 2), never a traceback.
- Manifest integrity is checked before any ordering claim: duplicate
  ordinals, ordinals below 1, malformed lines, and statuses outside
  {ok, error, no-result} each fail closed (exit 2) with a parse message.
- A pre-write row whose target is ``-`` (extract_evidence.py could not
  extract one) is ALWAYS listed for classification, regardless of
  --data-pattern: an invisible target cannot be cleared by a pattern that
  never saw it. Read the row's real input from the events stream.
- A pre-write Bash row that runs an interpreter or a script file
  (``python analysis.py``, ``uv run x.py``, ``bash s.sh``, ``./x.py``) is
  ALWAYS listed too, regardless of --data-pattern: the data it read may be
  named only inside the script, not on its command line, so the pattern
  cannot see it (the ``-`` case, one indirection deeper). Detection
  (``looks_like_script_execution``) is a conservative fail-toward-listing
  heuristic, not a shell parser; its documented gaps (task runners like
  ``make``/``npm run``, bare extensionless PATH executables) still require
  reading the events stream. This listing rule applies to the SAME-BATCH scan
  as well, so a timestamp-tied script write cannot slip through as CLEAN.
- If no executed Write/Edit matches --ledger-pattern, Bash rows (any status)
  whose command matches the pattern are surfaced as possible Bash-mediated
  ledger writes (``cat > ledger.md`` and the like); the run stays
  UNVERIFIABLE (exit 2) and those candidates must be verified from the
  events stream and scored manually.

Content check: finding the write proves *when* a ledger file was touched, not
*what* it contained. Whenever a ledger write is found the checker prints a
CONTENT-CHECK REQUIRED line: the scorer must confirm from the events stream
that this first write already carries the hypothesis table and predictions --
a placeholder written early and filled in after analysis is a reconstruction,
not a preregistration.

Stated limitation: ordinals are JSONL serialization order, which is this
instrument's ordering authority, but tool calls issued in parallel within one
assistant turn have no true mutual order. Such rows are only heuristically
flagged: post-write rows sharing the ledger write's exact timestamp that are
data-relevant — matching --data-pattern, carrying target ``-``, or (for Bash)
running an interpreter/script — are printed under a SAME-BATCH heading and
force exit code >= 1, because serialization order cannot prove the ledger file
existed before they ran. Classify them from the events stream.

Exit codes:
  0  ledger write found, nothing to classify
  1  ledger write found; pre-write touches and/or same-batch rows listed for
     classification
  2  UNVERIFIABLE: unreadable manifest, integrity failure, invalid pattern,
     or no executed ledger write -- the preregistration assertion fails
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import NamedTuple

WRITE_TOOLS = frozenset({"Write", "Edit", "NotebookEdit"})
VALID_STATUSES = frozenset({"ok", "error", "no-result"})
EXPECTED_COLUMNS = 5
UNEXTRACTED_NOTE = " (target not extracted — read it from the events stream)"
SCRIPT_EXEC_NOTE = (
    " (runs an interpreter/script — the data it read may be named only inside "
    "the script, not on this command line; read it from the events stream)"
)

# Statement separators that start a fresh command position within one Bash
# ``command`` string. ``\\n`` matches the literal two-char sequence
# extract_evidence.py's _flatten() leaves where a real newline was, so a
# multi-statement command does not hide a later interpreter behind an earlier
# innocuous head. The backtick splits a legacy command substitution
# (``echo `python x.py```). Kept intentionally simple: this is a heuristic, not
# a shell parser.
_SEPARATORS = re.compile(r"\\n|\|\||&&|[;|&()\n{}`]")
# A leading ``NAME=value`` env assignment, stripped before reading the head.
_ASSIGNMENT = re.compile(r"^[A-Za-z_]\w*=")
# Prefix words that precede the real command whose data access we care about;
# stripped so ``env python s.py`` / ``timeout 5 python s.py`` / ``if python …``
# are seen. Covers exec wrappers, resource/timing prefixes, and the shell
# control-flow words that can head a flattened compound command.
_WRAPPERS = frozenset(
    {
        "env",
        "time",
        "timeout",
        "nice",
        "nohup",
        "setsid",
        "stdbuf",
        "watch",
        "caffeinate",
        "sudo",
        "xargs",
        "command",
        "exec",
        "if",
        "elif",
        "else",
        "then",
        "do",
        "while",
        "until",
        "!",
    }
)
# Interpreters/runners that run a script, notebook, or inline program given as
# an argument. ``jupyter``/``nbconvert``/``papermill`` execute notebooks — a
# canonical hidden-data path for a data-analysis skill.
_INTERPRETERS = frozenset(
    {
        "python",
        "ipython",
        "bash",
        "sh",
        "zsh",
        "dash",
        "node",
        "deno",
        "ts-node",
        "ruby",
        "perl",
        "php",
        "rscript",
        "r",
        "julia",
        "lua",
        "pypy",
        "jupyter",
        "nbconvert",
        "papermill",
    }
)
# File extensions that mark a token as an executable script.
_SCRIPT_EXTS = (
    ".py",
    ".sh",
    ".bash",
    ".zsh",
    ".rb",
    ".pl",
    ".js",
    ".mjs",
    ".cjs",
    ".ts",
    ".r",
    ".jl",
    ".lua",
    ".ipynb",
)
# A version/point-release suffix on an interpreter name (python3, python3.12).
_VERSION_SUFFIX = re.compile(r"\d+(?:\.\d+)*$")


def _looks_like_script_path(token: str) -> bool:
    """A token that names an executable script file (``./run.sh``, ``scripts/x.py``)."""
    lowered = token.lower()
    if lowered.endswith(_SCRIPT_EXTS):
        return True
    # An explicit path to a local executable (``./run``) — extensionless but run
    # directly. Bare PATH executables (``run``) are indistinguishable from
    # ordinary commands and are left as a documented heuristic gap.
    return token.startswith(("./", "../", "/"))


def _token_runs_code(token: str, following: list[str]) -> bool:
    """A single command-position token that runs an interpreter or a script."""
    base = token.rsplit("/", 1)[-1].lower()
    stem = _VERSION_SUFFIX.sub("", base)  # python3.12 -> python
    if base in _INTERPRETERS or stem in _INTERPRETERS:
        return True
    if base == "uvx":
        return True
    if base == "uv" and "run" in following:  # `uv [--global-flags] run script.py`
        return True
    if base in {"source", "."} and following:
        return True
    return _looks_like_script_path(token)


def looks_like_script_execution(command: str) -> bool:
    """Heuristic: does this Bash command run an interpreter or a script file?

    check_prereg lists such pre-write / same-batch rows for mandatory manual
    classification even when the command line never names the fixture, because
    the data access can be buried inside the executed script (#76). It is
    deliberately conservative and fail-toward-listing: it errs toward listing a
    row rather than silently clearing it, but it does not attempt to prove a
    command cannot touch data.

    Method: split the command into statement segments at shell separators, drop
    leading ``NAME=value`` assignments and wrapper words (``env``, ``sudo``,
    ``time``, …), then inspect the segment's head token. A head that is an
    interpreter (``python``, ``python3.12``, ``/usr/bin/ruby``, ``Rscript``,
    ``ipython``, ``julia``, ``R``, ``lua``), a notebook runner
    (``jupyter``/``nbconvert``/``papermill``), a ``uv run`` / ``uvx`` invocation,
    a ``source``/``.`` of a file, or a script path (``./x.py``) counts. Because
    only the head is inspected, ``grep python README`` and ``cat > analysis.py``
    do not match. When a prefix was stripped (a wrapper or a ``NAME=value``
    assignment), its own options, option-args, or quote-split fragments can sit
    before the wrapped command (``env -i python x.py``, ``nice -n 5 python x.py``,
    ``FOO="a b" python x.py``), so the whole remaining segment is scanned.

    Being fail-toward-listing, it over-lists in known-safe ways: a prefixed
    non-executor (``sudo grep python f``), an absolute-path system utility
    (``/bin/ls`` — the ``/``-prefix rule flags any absolute command), and a
    command whose quotes hid a separator. All are harmless (the scorer clears
    them); silent under-listing is the only real failure.

    Documented heuristic gaps — the checker returns False, so classify these
    from the events stream when a pre-write Bash row is otherwise unexplained:
    task runners (``make``, ``just``, ``conda run``, ``npm``/``npx``/``yarn``/
    ``pnpm run``); database CLIs that read data inline (``sqlite3 db 'SELECT …'``,
    ``duckdb``); ``-f``-driven mini-language scripts (``awk -f p.awk``,
    ``sed -f p.sed``); the Windows ``py`` launcher; and bare extensionless PATH
    executables.
    """
    for segment in _SEPARATORS.split(command):
        tokens = segment.split()
        i = 0
        saw_prefix = False
        while i < len(tokens) and (_ASSIGNMENT.match(tokens[i]) or tokens[i] in _WRAPPERS):
            saw_prefix = True
            i += 1
        rest = tokens[i:]
        if not rest:
            continue
        if _token_runs_code(rest[0], rest[1:]):
            return True
        # A stripped prefix (wrapper or assignment) carries its own options,
        # option-args, or quote-split fragments before the wrapped command, so
        # the head after stripping may not be it (``env -i python x.py``,
        # ``nice -n 5 python x.py``, ``FOO="a b" python x.py``). Scan the
        # remainder only when a prefix was seen, to keep ``grep python`` a miss.
        # This may over-list a prefixed non-executor (``sudo grep python f``),
        # acceptable under fail-toward-listing.
        if saw_prefix and any(_token_runs_code(t, rest[j + 1 :]) for j, t in enumerate(rest)):
            return True
    return False


def classification_note(row: Row, data: re.Pattern[str]) -> str | None:
    """Why this row needs manual classification, or None if it does not.

    Returns the printable note suffix so the two scans in ``report_ordering``
    stay in lockstep: the unextracted-target note for an invisible target, ``""``
    for a direct --data-pattern match (listed plainly), the script-exec note for
    a Bash row that runs an interpreter/script (whose data access can hide inside
    the script — #76), or None when the row is not data-relevant.
    """
    if row.target == "-":
        return UNEXTRACTED_NOTE
    if data.search(row.target):
        return ""
    if row.tool == "Bash" and looks_like_script_execution(row.target):
        return SCRIPT_EXEC_NOTE
    return None


class Row(NamedTuple):
    """One manifest line: a tool_use in serialization order."""

    ordinal: int
    timestamp: str
    tool: str
    status: str
    target: str


def parse_manifest(text: str) -> tuple[list[Row], list[str]]:
    """Manifest rows plus parse failures; any failure means fail closed."""
    rows: list[Row] = []
    fails: list[str] = []
    seen_ordinals: set[int] = set()
    for n, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        cells = line.split("\t")
        if len(cells) != EXPECTED_COLUMNS:
            fails.append(f"parse: line {n} has {len(cells)} column(s), expected {EXPECTED_COLUMNS}")
            continue
        try:
            ordinal = int(cells[0])
        except ValueError:
            fails.append(f"parse: line {n} ordinal {cells[0]!r} is not an integer")
            continue
        if ordinal < 1:
            fails.append(f"parse: line {n} ordinal {ordinal} is below 1; ordinals are 1-based")
            continue
        if ordinal in seen_ordinals:
            fails.append(f"parse: line {n} duplicates ordinal {ordinal}; ordering is ambiguous")
            continue
        seen_ordinals.add(ordinal)
        if cells[3] not in VALID_STATUSES:
            fails.append(
                f"parse: line {n} status {cells[3]!r} is not one of "
                f"{', '.join(sorted(VALID_STATUSES))}"
            )
            continue
        rows.append(Row(ordinal, cells[1], cells[2], cells[3], cells[4]))
    if not rows and not fails:
        fails.append("parse: manifest has no data rows")
    return rows, fails


def first_ledger_write(rows: list[Row], pattern: re.Pattern[str]) -> Row | None:
    """The first executed Write/Edit whose target matches the ledger pattern.

    Only a paired ok result proves execution (extract_evidence.py's contract),
    so an errored or unpaired write attempt is not a preregistration.
    """
    for row in sorted(rows, key=lambda r: r.ordinal):
        if row.tool in WRITE_TOOLS and row.status == "ok" and pattern.search(row.target):
            return row
    return None


def no_ledger_message(rows: list[Row], pattern: re.Pattern[str], raw_pattern: str) -> str:
    """UNVERIFIABLE message, naming any Bash rows that look like ledger writes."""
    message = (
        f"UNVERIFIABLE: no executed Write/Edit matches --ledger-pattern "
        f"{raw_pattern!r}; preregistration ordering cannot be "
        f"established from this transcript"
    )
    bash_candidates = sorted(
        (r for r in rows if r.tool == "Bash" and pattern.search(r.target)),
        key=lambda r: r.ordinal,
    )
    if bash_candidates:
        ordinals = ",".join(str(r.ordinal) for r in bash_candidates)
        message += (
            f"; possible Bash-mediated ledger write(s) at ordinal(s) {ordinals} "
            f"— verify from the events stream and score manually"
        )
    return message


def report_ordering(rows: list[Row], ledger: Row, data: re.Pattern[str]) -> int:
    """Print the ordering facts for a found ledger write; return the exit code."""
    print(f"PREREG_WRITE: ordinal {ledger.ordinal} ({ledger.tool} -> {ledger.target})")
    print(
        f"CONTENT-CHECK REQUIRED: confirm from the events stream "
        f"(extract_evidence.py events <transcript> --ordinal {ledger.ordinal}) "
        f"that this write already carries the hypothesis table and predictions "
        f"— a placeholder written early and filled after analysis is a "
        f"reconstruction, not a preregistration."
    )
    earlier: list[tuple[Row, str]] = []
    for r in sorted(rows, key=lambda x: x.ordinal):
        if r.ordinal >= ledger.ordinal:
            continue
        note = classification_note(r, data)
        if note is not None:
            earlier.append((r, note))
    same_batch: list[tuple[Row, str]] = []
    for r in sorted(rows, key=lambda x: x.ordinal):
        if r.ordinal <= ledger.ordinal or r.timestamp != ledger.timestamp:
            continue
        note = classification_note(r, data)
        if note is not None:
            same_batch.append((r, note))
    if not earlier and not same_batch:
        print("CLEAN: no data-matching tool_use precedes the ledger write")
        return 0
    if earlier:
        print(
            f"CLASSIFY: {len(earlier)} tool_use(s) precede the ledger write; "
            f"classify each as orientation or analysis in the evidence artifact:"
        )
        for r, note in earlier:
            print(f"  - ordinal {r.ordinal}: {r.tool} [{r.status}] {r.target}{note}")
    if same_batch:
        print(
            f"SAME-BATCH: {len(same_batch)} tool_use(s) share the ledger "
            f"write's timestamp; serialization order cannot prove the ledger "
            f"file existed before they ran — classify from the events stream:"
        )
        for r, note in same_batch:
            print(f"  - ordinal {r.ordinal}: {r.tool} [{r.status}] {r.target}{note}")
    return 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("manifest", type=Path)
    ap.add_argument("--ledger-pattern", required=True)
    ap.add_argument("--data-pattern", required=True)
    a = ap.parse_args()
    try:
        ledger_pattern = re.compile(a.ledger_pattern)
        data = re.compile(a.data_pattern)
    except re.error as exc:
        print(f"UNVERIFIABLE: invalid pattern {exc.pattern!r}: {exc}")
        return 2
    try:
        text = a.manifest.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        print(f"UNVERIFIABLE: cannot read manifest {a.manifest}: {exc}")
        return 2
    rows, fails = parse_manifest(text)
    if fails:
        print("UNVERIFIABLE:")
        for f in fails:
            print(f"  - {f}")
        return 2
    ledger = first_ledger_write(rows, ledger_pattern)
    if ledger is None:
        print(no_ledger_message(rows, ledger_pattern, a.ledger_pattern))
        return 2
    return report_ordering(rows, ledger, data)


if __name__ == "__main__":
    raise SystemExit(main())
