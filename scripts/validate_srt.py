#!/usr/bin/env python3
"""Validate that a translated SRT keeps the source subtitle structure."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


TIMECODE_RE = re.compile(
    r"^(\d{2,}):(\d{2}):(\d{2}),(\d{3}) --> "
    r"(\d{2,}):(\d{2}):(\d{2}),(\d{3})(?:\s+.*)?$"
)
TAG_RE = re.compile(r"(?:</?[^>]+>|\{\\[^}]+\})")


@dataclass(frozen=True)
class Cue:
    number: str
    timing: str
    text: tuple[str, ...]
    tags: tuple[str, ...]


def read_srt(path: Path) -> str:
    data = path.read_bytes()
    try:
        return data.decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
    except UnicodeDecodeError as exc:
        raise ValueError(f"{path}: файл не является корректным UTF-8 ({exc})") from exc


def timestamp_value(hours: str, minutes: str, seconds: str, millis: str) -> int:
    if int(minutes) > 59 or int(seconds) > 59 or int(millis) > 999:
        raise ValueError("некорректный компонент времени")
    return ((int(hours) * 60 + int(minutes)) * 60 + int(seconds)) * 1000 + int(millis)


def parse_srt(path: Path) -> list[Cue]:
    text = read_srt(path).strip("\n")
    if not text:
        raise ValueError(f"{path}: файл пуст")

    cues: list[Cue] = []
    for block_index, block in enumerate(re.split(r"\n{2,}", text), start=1):
        lines = block.split("\n")
        if len(lines) < 3:
            raise ValueError(f"{path}: блок {block_index} слишком короткий")
        number = lines[0].strip()
        if not number.isdigit():
            raise ValueError(f"{path}: блок {block_index}: номер cue не является числом")
        timing = lines[1].strip()
        match = TIMECODE_RE.fullmatch(timing)
        if not match:
            raise ValueError(f"{path}: cue {number}: некорректный timecode")
        try:
            start = timestamp_value(*match.groups()[:4])
            end = timestamp_value(*match.groups()[4:8])
        except ValueError as exc:
            raise ValueError(f"{path}: cue {number}: {exc}") from exc
        if start > end:
            raise ValueError(f"{path}: cue {number}: начало позже конца")
        subtitle_lines = tuple(lines[2:])
        if not any(line.strip() for line in subtitle_lines):
            raise ValueError(f"{path}: cue {number}: пустой текст")
        tags = tuple(TAG_RE.findall("\n".join(subtitle_lines)))
        cues.append(Cue(number, timing, subtitle_lines, tags))
    return cues


def validate(source_path: Path, output_path: Path) -> list[str]:
    errors: list[str] = []
    try:
        source = parse_srt(source_path)
    except ValueError as exc:
        return [str(exc)]
    try:
        output = parse_srt(output_path)
    except ValueError as exc:
        return [str(exc)]

    if len(source) != len(output):
        errors.append(f"количество cue: источник {len(source)}, перевод {len(output)}")

    for index, (source_cue, output_cue) in enumerate(zip(source, output), start=1):
        label = f"cue {index}"
        if source_cue.number != output_cue.number:
            errors.append(f"{label}: номер источника {source_cue.number}, перевода {output_cue.number}")
        if source_cue.timing != output_cue.timing:
            errors.append(f"{label} {source_cue.number}: изменён timecode")
        if len(source_cue.text) != len(output_cue.text):
            errors.append(
                f"{label} {source_cue.number}: строк источника {len(source_cue.text)}, "
                f"перевода {len(output_cue.text)}"
            )
        if source_cue.tags != output_cue.tags:
            errors.append(f"{label} {source_cue.number}: изменены markup/positioning tags")
        if any(line.strip() for line in source_cue.text) and not any(
            line.strip() for line in output_cue.text
        ):
            errors.append(f"{label} {source_cue.number}: перевод пуст")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Проверить сохранность структуры SRT после перевода."
    )
    parser.add_argument("source", type=Path, help="английский или другой исходный SRT")
    parser.add_argument("output", type=Path, help="переведённый SRT")
    args = parser.parse_args()

    errors = validate(args.source, args.output)
    if errors:
        print("SRT validation: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"SRT validation: PASS ({len(parse_srt(args.source))} cue)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
