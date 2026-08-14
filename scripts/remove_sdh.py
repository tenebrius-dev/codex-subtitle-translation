#!/usr/bin/env python3
"""Create an SDH backup and remove common sound descriptions from SRT files."""

from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile
from pathlib import Path

from validate_srt import Cue, parse_srt


VIDEO_EXTENSIONS = {
    ".avi",
    ".m2ts",
    ".m4v",
    ".mkv",
    ".mov",
    ".mp4",
    ".ts",
    ".webm",
}
BRACKET_RE = re.compile(r"\[[^\]\r\n]*\]")
MARKUP_RE = re.compile(r"</?[^>]+>|\{\\[^}]+\}")
BRACKET_ONLY_RE = re.compile(r"(?:\s*\[[^\]\r\n]*\]\s*)+", re.DOTALL)


def read_bytes_and_format(path: Path) -> tuple[bytes, str, bool]:
    original = path.read_bytes()
    try:
        text = original.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError(f"{path}: файл не является корректным UTF-8 ({exc})") from exc

    if "\r\n" in text:
        newline = "\r\n"
    elif "\r" in text:
        newline = "\r"
    else:
        newline = "\n"
    return original, newline, original.startswith(b"\xef\xbb\xbf")


def plain_text(text: str) -> str:
    return MARKUP_RE.sub("", text)


def is_bracket_only(text: str) -> bool:
    without_markup = plain_text(text)
    return bool(without_markup.strip()) and bool(BRACKET_ONLY_RE.fullmatch(without_markup))


def is_single_music_note(text: str) -> bool:
    return re.sub(r"\s+", "", plain_text(text)) == "♪"


def clean_cues(cues: list[Cue]) -> tuple[list[tuple[str, list[str]]], dict[str, int]]:
    cleaned: list[tuple[str, list[str]]] = []
    stats = {
        "bracket_cues": 0,
        "music_cues": 0,
        "empty_cues": 0,
        "bracket_blocks": 0,
    }

    for cue in cues:
        source_text = "\n".join(cue.text)
        stats["bracket_blocks"] += len(BRACKET_RE.findall(source_text))

        if is_bracket_only(source_text):
            stats["bracket_cues"] += 1
            continue
        if is_single_music_note(source_text):
            stats["music_cues"] += 1
            continue

        text_lines: list[str] = []
        for line in cue.text:
            line = BRACKET_RE.sub("", line)
            line = re.sub(r"[ \t]{2,}", " ", line).strip()
            if line:
                text_lines.append(line)

        if not text_lines or is_single_music_note("\n".join(text_lines)):
            stats["empty_cues"] += 1
            continue
        cleaned.append((cue.timing, text_lines))

    return cleaned, stats


def serialize(cues: list[tuple[str, list[str]]], newline: str, bom: bool) -> bytes:
    blocks: list[str] = []
    for number, (timing, text_lines) in enumerate(cues, start=1):
        blocks.append("\n".join([str(number), timing, *text_lines]))
    text = "\n\n".join(blocks) + ("\n" if blocks else "")
    encoded = text.replace("\n", newline).encode("utf-8")
    return (b"\xef\xbb\xbf" if bom else b"") + encoded


def backup_path(path: Path) -> Path:
    return path.with_name(f"{path.stem}.SDH{path.suffix}")


def process_file(path: Path) -> str:
    original, newline, bom = read_bytes_and_format(path)
    cues = parse_srt(path)
    destination = backup_path(path)

    if destination.exists():
        if destination.read_bytes() != original:
            raise ValueError(f"{path}: backup already exists but differs: {destination}")
    else:
        destination.write_bytes(original)

    cleaned, stats = clean_cues(cues)
    output = serialize(cleaned, newline, bom)

    temporary: Path | None = None
    try:
        fd, temporary_name = tempfile.mkstemp(
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
        )
        os.close(fd)
        temporary = Path(temporary_name)
        temporary.write_bytes(output)
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()

    removed = stats["bracket_cues"] + stats["music_cues"] + stats["empty_cues"]
    return (
        f"{path}: cleaned; backup={destination.name}; "
        f"removed_cues={removed}; bracket_blocks={stats['bracket_blocks']}; "
        f"remaining_cues={len(cleaned)}"
    )


def is_backup(path: Path) -> bool:
    return ".SDH." in path.name or path.name.endswith(".SDH.srt")


def collect_inputs(path: Path) -> list[Path]:
    if path.is_file():
        if path.suffix.lower() == ".srt":
            return [path]
        if path.suffix.lower() in VIDEO_EXTENSIONS:
            candidate = path.with_suffix(".srt")
            if not candidate.exists():
                raise ValueError(f"{path}: рядом нет SRT-файла {candidate.name}")
            return [candidate]
        raise ValueError(f"{path}: ожидается SRT, видеофайл или папка")

    if path.is_dir():
        files: list[Path] = []
        for candidate in sorted(path.rglob("*.srt")):
            relative_parts = candidate.relative_to(path).parts
            if any(part.startswith(".") for part in relative_parts):
                continue
            if not is_backup(candidate):
                files.append(candidate)
        if not files:
            raise ValueError(f"{path}: SRT-файлы не найдены")
        return files

    raise ValueError(f"{path}: путь не существует")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Сохранить SDH-копию и убрать звуковые описания из SRT."
    )
    parser.add_argument("input", type=Path, help="SRT, видеофайл или папка")
    args = parser.parse_args()

    try:
        inputs = collect_inputs(args.input)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    failures = 0
    for path in inputs:
        try:
            print(process_file(path))
        except (OSError, ValueError) as exc:
            failures += 1
            print(f"ERROR: {exc}", file=sys.stderr)

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
