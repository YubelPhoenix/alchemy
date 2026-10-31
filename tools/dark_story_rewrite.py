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
# Tokens the engine fills in at run time. Dropping or changing one breaks the
# line (a missing name, an item without its article), so they must survive.
RUNTIME_RE = re.compile(
    r"\{(?:actor_name:\d+|argument_actor_name(?::\d+)?|protagonist_name"
    r"|article_class(?::\d+)?|possessive_suffix(?::\d+)?)\}"
)


def visible_width(line: str) -> int:
    # A dynamic character name can be longer than its token; reserve eight.
    line = ACTOR_RE.sub("XXXXXXXX", line).replace("{protagonist_name}", "XXXXXXXX")
    return len(CONTROL_RE.sub("", line))


def load_replacements(only=None) -> dict[str, tuple[str, str]]:
    rows: dict[str, tuple[str, str]] = {}
    files = [Path(f) for f in only] if only else sorted(DATA_DIR.glob("*.tsv"))
    if not files:
        raise SystemExit(f"No dialogue files found in {DATA_DIR}/.")
    for file in files:
        for number, line in enumerate(file.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip() or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) != 3 or not re.fullmatch(r"[0-9]{5}|N[0-9]{2,3}", parts[0]):
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
    if sorted(RUNTIME_RE.findall(original)) != sorted(RUNTIME_RE.findall(new)):
        raise SystemExit(
            f"Dialogue {msgid} changed its run-time tokens (names, articles): "
            f"{sorted(RUNTIME_RE.findall(original))} -> {sorted(RUNTIME_RE.findall(new))}"
        )
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
    args = sys.argv[1:]
    check_only = "--check" in args
    replacements = load_replacements([a for a in args if a != "--check"] or None)
    text = PO_PATH.read_text(encoding="utf-8")
    entries = re.split(r"(\n\s*\n)", text)
    done = set()
    new_rows = {k: v for k, v in replacements.items() if k.startswith("N")}
    for msgid, (context, new) in sorted(new_rows.items()):
        validate(msgid, new, new)
        done.add(msgid)
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
    if new_rows and not check_only:
        # New messages go in front of the catalogue's final null entry, which
        # moves up to the next free number.
        last = max(i for i, e in enumerate(entries) if "alchemy-null" in e)
        first_id = int(re.search(r'msgid "([0-9]{5})"', entries[last]).group(1))
        added = []
        for offset, (key, (context, new)) in enumerate(sorted(new_rows.items(), key=lambda kv: int(kv[0][1:]))):
            body = ['msgstr ""']
            display_lines = new.split(r"\n")
            for i, display_line in enumerate(display_lines):
                suffix = r"\n" if i < len(display_lines) - 1 else ""
                body.append('"' + display_line + suffix + '"')
            added.append(f'msgctxt "{context}"\nmsgid "{first_id + offset:05d}"\n' + "\n".join(body))
        terminator = re.sub(r'msgid "[0-9]{5}"', f'msgid "{first_id + len(added):05d}"', entries[last])
        entries[last:last + 1] = ["\n\n".join(added), "\n\n", terminator]
    if check_only:
        print(f"Checked {len(done)} dialogue entries; en.po untouched.")
        return
    PO_PATH.write_text("".join(entries), encoding="utf-8")
    print(f"Rewrote and validated {len(done)} dialogue entries.")


if __name__ == "__main__":
    sys.dont_write_bytecode = True
    main()
