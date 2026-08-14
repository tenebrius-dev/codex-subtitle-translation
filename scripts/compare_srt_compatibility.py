#!/usr/bin/env python3
"""Check whether two subtitle files are structurally compatible releases."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from validate_srt import parse_srt


def sample_indices(count: int) -> list[int]:
    """Return deterministic samples from the beginning, middle, and end."""
    candidates = {0, 1, 2, count // 2 - 1, count // 2, count // 2 + 1, count - 3, count - 2, count - 1}
    return sorted(index for index in candidates if 0 <= index < count)


def compare(source_path: Path, candidate_path: Path) -> list[str]:
    try:
        source = parse_srt(source_path)
    except ValueError as exc:
        return [str(exc)]
    try:
        candidate = parse_srt(candidate_path)
    except ValueError as exc:
        return [str(exc)]

    errors: list[str] = []
    if len(source) != len(candidate):
        errors.append(f"cue count differs: English {len(source)}, candidate {len(candidate)}")
        return errors

    for index, (source_cue, candidate_cue) in enumerate(zip(source, candidate), start=1):
        if source_cue.number != candidate_cue.number:
            errors.append(
                f"cue number differs at position {index}: English {source_cue.number}, "
                f"candidate {candidate_cue.number}"
            )
            break
    for index in sample_indices(len(source)):
        source_cue = source[index]
        candidate_cue = candidate[index]
        if source_cue.timing != candidate_cue.timing:
            errors.append(
                f"sample timing differs at cue {source_cue.number}: English "
                f"{source_cue.timing}, candidate {candidate_cue.timing}"
            )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare an English subtitle with a Russian candidate release."
    )
    parser.add_argument("english", type=Path, help="selected English SRT")
    parser.add_argument("candidate", type=Path, help="Russian candidate SRT")
    args = parser.parse_args()

    errors = compare(args.english, args.candidate)
    if errors:
        print("SRT release compatibility: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    cue_count = len(parse_srt(args.english))
    sampled = ", ".join(str(index + 1) for index in sample_indices(cue_count))
    print(f"SRT release compatibility: PASS ({cue_count} cue; sampled timings: {sampled})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
