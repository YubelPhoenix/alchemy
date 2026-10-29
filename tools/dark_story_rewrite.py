#!/usr/bin/env python3
"""Apply and validate the dark-story dialogue rewrite.

Every file in tools/dark_story/*.tsv holds rows of  ID <TAB> CONTEXT <TAB> TEXT.
TEXT is exactly what goes between the quotes of the English catalogue: a literal
\\n starts a display line and {page_break} starts a new page. The script edits
only games/tbs/text/en.po in the build workspace and refuses to continue unless
every row passes these checks:

  * the numeric id still has the expected message context (guards against drift)
  * no page has more than three display lines, and no line is wider than the
    text box (27 characters; a dynamic name is counted as eight)
  * the ending control ({end_wait}, {end_now}...) and any text-effect controls
    of the original line are kept
"""
from pathlib import Path
import re
import sys

PO_PATH = Path("games/tbs/text/en.po")
DATA_DIR = Path("tools/dark_story")
MAX_WIDTH = 27
MAX_LINES = 3

CONTROL_RE = re.compile(r"\{[^{}]+\}")
ACTOR_RE = re.compile(r"\{actor_name:\d+\}")
END_RE = re.compile(r"\{end_[^{}]*\}\s*$")
STYLE_RE = re.compile(r"\{(?:text_effect:\d+|reset_text_style)\}")


def visible_width(line: str) -> int:
    # A dynamic character name can be longer than its token; reserve eight.
    return len(CONTROL_RE.sub("", ACTOR_RE.sub("XXXXXXXX", line)))


def load_replacements() -> dict[str, tuple[str, str]]:
    rows: dict[str, tuple[str, str]] = {}
    files = sorted(DATA_DIR.glob("*.tsv"))
    if not files:
        raise SystemExit(f"No dialogue files found in {DATA_DIR}/.")
    for file in files:
        for number, line in enumerate(file.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip() or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) != 3 or not re.fullmatch(r"[0-9]{5}", parts[0]):
                raise SystemExit(f"{file}:{number}: expected ID<TAB>CONTEXT<TAB>TEXT.")
            msgid, context, text = parts
            if msgid in rows:
                raise SystemExit(f"{file}:{number}: duplicate dialogue ID {msgid}.")
            rows[msgid] = (context, text)
    return rows


def decode_msgstr(entry: str) -> str:
    lines = entry.splitlines()
    start = next((i for i, line in enumerate(lines) if line.startswith("msgstr ")), None)
    if start is None:
        raise SystemExit("A catalogue entry has no msgstr.")
    encoded = []
    first = lines[start][len("msgstr "):]
    if first:
        encoded.append(first)
    for line in lines[start + 1:]:
        if not line.startswith('"'):
            break
        encoded.append(line)
    return "".join(part[1:-1] for part in encoded if part.startswith('"'))


def validate(msgid: str, original: str, new: str) -> None:
    if not new.strip():
        raise SystemExit(f"Dialogue {msgid} is empty.")
    original_end = END_RE.search(original)
    new_end = END_RE.search(new)
    if (original_end.group(0).strip() if original_end else "") != (new_end.group(0).strip() if new_end else ""):
        raise SystemExit(f"Dialogue {msgid} changed its ending control code.")
    if STYLE_RE.findall(original) != STYLE_RE.findall(new):
        raise SystemExit(f"Dialogue {msgid} changed its text-effect control codes.")
    for page_no, page in enumerate(new.split("{page_break}"), start=1):
        lines = page.split(r"\n")
        while lines and not lines[0]:
            lines.pop(0)
        while lines and not lines[-1]:
            lines.pop()
        if len(lines) > MAX_LINES:
            raise SystemExit(f"Dialogue {msgid}, page {page_no}: {len(lines)} display lines (maximum {MAX_LINES}).")
        for line_no, line in enumerate(lines, start=1):
            width = visible_width(line)
            if width > MAX_WIDTH:
                raise SystemExit(
                    f"Dialogue {msgid}, page {page_no}, line {line_no}: "
                    f"{width} visible characters (maximum {MAX_WIDTH}): {line}"
                )


def main() -> None:
    replacements = load_replacements()
    text = PO_PATH.read_text(encoding="utf-8")
    entries = re.split(r"(\n\s*\n)", text)
    done = set()
    for index, entry in enumerate(entries):
        match = re.search(r'^msgctxt "(.*?)"\nmsgid "([0-9]{5})"$', entry, re.MULTILINE)
        if not match or match.group(2) not in replacements:
            continue
        context, msgid = match.groups()
        expected_context, new = replacements[msgid]
        if context != expected_context:
            raise SystemExit(f"Dialogue {msgid} has context {context}; expected {expected_context}.")
        validate(msgid, decode_msgstr(entry), new)
        lines = entry.splitlines()
        msgstr_index = next(i for i, line in enumerate(lines) if line.startswith("msgstr "))
        display_lines = new.split(r"\n")
        encoded = ['msgstr ""']
        for i, display_line in enumerate(display_lines):
            suffix = r"\n" if i < len(display_lines) - 1 else ""
            encoded.append('"' + display_line + suffix + '"')
        entries[index] = "\n".join(lines[:msgstr_index] + encoded)
        done.add(msgid)
    missing = sorted(set(replacements) - done)
    if missing:
        raise SystemExit("Dialogue IDs not found in the catalogue: " + ", ".join(missing))
    PO_PATH.write_text("".join(entries), encoding="utf-8")
    print(f"Rewrote and validated {len(done)} dialogue entries.")


if __name__ == "__main__":
    sys.dont_write_bytecode = True
    main()
