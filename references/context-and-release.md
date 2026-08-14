# Context and release checklist

Use this checklist before translating a film or episode.

## Release matching

1. Search the OpenSubtitles website: https://www.opensubtitles.org/.
2. Start with the complete video filename.
3. Confirm title, season, episode, and release group.
4. Compare source, resolution, codec, and WEB-DL or WEBRip markers.
5. Compare runtime or the final cue timestamp when available.
6. Reject candidates that are forced-only, SDH-only, commentary, or from a different cut unless the user explicitly asks for them.
7. Search for both the default English source and a possible Russian alternative for the same release.
8. If a Russian alternative exists, show its URL and the exact `translator` field value; if absent, report that the translator is not specified.
9. If two plausible candidates disagree in cue timing or dialogue, ask the user before translation.

The release group is useful evidence, not proof by itself. A subtitle that merely contains the same episode number is not an exact match.

## Context research

Collect only context that can change a translation decision:

- who is speaking and how they address one another;
- names, aliases, ranks, organizations, locations, and fictional terminology;
- events from the immediately preceding episode or season;
- idioms, jokes, quotations, song references, and culture-specific allusions;
- the register of each main character.

Prefer official or primary material for facts. Use recaps and fan discussions to disambiguate dialogue, not as unquestioned authority. Note uncertainty rather than inventing a definitive interpretation.

## Translation QA

Before saving the sidecar:

- verify that every source cue has exactly one translated cue;
- compare timecodes byte-for-byte after newline normalization;
- compare the number of text lines in every cue;
- compare markup and positioning tags;
- search for accidental English fragments, empty translated cues, and inconsistent glossary terms;
- read several early, middle, and late cues in context, especially jokes, arguments, names, and scene transitions.
