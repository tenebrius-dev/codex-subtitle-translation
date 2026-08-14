---
name: codex-subtitle-translation
description: Use automatically when the user asks in Russian or English to make, translate, or prepare Russian subtitles for a local movie, episode, video file, or folder. Find and verify the English source for the exact release, research context, preserve the original SRT cue count, timings, formatting, and line distribution, and save the result beside the video.
---

# Subtitle Translation

## Purpose

This skill handles a repeatable workflow for translating subtitles into Russian. It accepts either one video file or a folder, researches the title and episode context, finds or verifies an English subtitle for the exact release, translates it, validates the SRT structure, and saves the result next to the video.

The default output for `movie.mkv` is `movie.srt`. Keep the video filename exactly as it is, including release tags, brackets, capitalization, and punctuation. Do not add `.ru`, `.rus`, `.translated`, or other suffixes.

## Automatic invocation

Treat a short request with a local path as a complete instruction. For example:

```text
Сделай русские субтитры серии /path/to/series-folder
```

This request automatically means:

1. find the video files in the given file or folder; if a folder has no video files directly in its root, scan all nested folders recursively;
2. search `https://www.opensubtitles.org/` and find/verify English subtitles for each exact release;
3. research the film or series context before translating;
4. translate into Russian with the source line distribution and SRT structure unchanged;
5. validate and save each finished subtitle beside its video using the exact video basename.

Do not ask the user to repeat these steps or to mention `$codex-subtitle-translation`. The skill is configured for implicit invocation. Ask a question only when a real decision cannot be established safely, such as two subtitle candidates matching different cuts or an existing Russian sidecar that would be overwritten.

The default target language is Russian. The default source language is English when an English release subtitle is available. A request that supplies a subtitle file or URL overrides the search step, but the source must still be checked against the video release.

## Workflow

### 1. Identify the input

- If the user gives a video file, process that file.
- If the user gives a folder, first inspect the folder's root. If the root contains one or more recognized video files, process those files. If the root contains no recognized video files, recursively inspect the entire descendant tree and process every recognized video file found. Sort the final list naturally by season and episode, then by path.
- Do not stop at the first nested folder and do not require the user to list subfolders manually. Ignore hidden/system directories unless the user explicitly names one.
- Recognize common video extensions: `.mkv`, `.mp4`, `.avi`, `.mov`, `.m4v`, `.webm`, `.ts`, and `.m2ts`.
- Parse the exact release name from the video filename. Do not reduce the task to only a title and episode number.
- Check for existing sidecar subtitles, but do not assume that a nearby file matches the release without checking its metadata and structure.

### 2. Find the source subtitle

Use the OpenSubtitles website at https://www.opensubtitles.org/ for subtitle search. By default, look for an English subtitle that matches the exact release named by the user. Search using the full filename first, then title, season/episode, resolution, source, codec, and release group as needed.

At the same time, check whether OpenSubtitles has a Russian subtitle for the same title and release. A Russian subtitle is an alternative to the new translation, not a silent replacement for it.

For every candidate, verify as many of these signals as are available:

- title, season, and episode;
- WEB-DL or WEBRip source and resolution;
- release group and codec;
- runtime or cue timing near the end of the file;
- language and whether it is a full dialogue subtitle rather than SDH-only or forced-only.

If the user gives a particular subtitle file or URL, use it as the source and verify it instead of searching for a replacement. If no candidate is clearly for the requested release, stop before translating and ask the user which candidate to use. Never silently substitute a subtitle from another release.

When a website requires an interactive session or presents several downloads, use the available browser and report the selected source URL in the completion summary. Do not claim an exact match based only on a similar title.

If a Russian candidate is found, offer it to the user before translating. Show:

- the OpenSubtitles URL;
- the language and subtitle type;
- the evidence that it matches the requested release;
- the value of the `translator` field exactly as displayed on OpenSubtitles. If the field is empty or missing, say `translator не указан`.

If several Russian candidates are found, list each one separately. Ask whether to use one of the existing Russian subtitles or proceed with a new translation. Use an existing Russian file only after the user chooses it and after checking that it belongs to the requested release. Never silently use an existing Russian subtitle.

### 3. Research context before translating

Research enough context to resolve names, relationships, slang, recurring terminology, and tone. Use a compact mix of reliable and practical sources:

- official synopsis or episode description;
- episode guides or reputable recaps;
- interviews or production material when a reference is obscure;
- fan discussions and Reddit when they clarify idiom, continuity, or a disputed interpretation.

For a series, include the immediately preceding episode or season context when it affects the dialogue. Record a short working note in `.subtitle-work/context/` when the information will be useful for later episodes. Keep source links and distinguish confirmed facts from interpretation. Do not pretend to have watched the episode when only written sources were consulted.

Before the first episode of a title, establish a glossary: character names, place names, organizations, invented terms, ranks, recurring jokes, and preferred forms of address. Reuse it across episodes and update it when the new episode establishes a better reading.

### 4. Translate without changing subtitle geometry

Treat the source SRT as a fixed timed document. Translation may change the text only.

- Keep every cue number and every timecode exactly unchanged.
- Keep the same number of subtitle text lines inside each cue. Do not merge or split lines.
- Keep cue order, blank cue separation, and the source newline convention where practical.
- Preserve markup and positioning tags such as `<i>`, `<b>`, `<u>`, font tags, and `\\an8`. Move a tag only when Russian grammar requires it, but preserve the same tag sequence and meaning.
- Preserve speaker dashes, sound-effect conventions, song styling, capitalization where it carries meaning, and on-screen text markers.
- Translate naturally into Russian, retaining character voice, register, humor, profanity level, and subtext. Do not translate names or technical terms inconsistently.
- Avoid adding explanations, translator notes, or extra lines.
- If a Russian phrase is too long, rewrite it naturally within the existing line count; do not alter timings or create an extra line.

Work in manageable chunks, but always compare the completed file with the complete source before delivery.

### 5. Validate and save each completed episode

Run the bundled validator against the English source and the Russian result:

```text
python3 <subtitle-translation-skill>/scripts/validate_srt.py SOURCE.srt OUTPUT.srt
```

The check must pass for cue count, cue numbers, timecodes, text-line count, preserved markup tags, and non-empty translated cues. Fix all structural errors before reporting completion.

Save the final file next to its video, using the video basename with `.srt`:

```text
/path/title.release.mkv
/path/title.release.srt
```

Do not overwrite an existing result silently if it may contain a different translation. If replacement is clearly requested, validate the replacement before moving it into the final path. For a batch, finish and save each episode immediately after its own validation rather than waiting for the whole season.

### 6. Report the result

For each video, report briefly:

- the chosen English subtitle and why it matches the release;
- any Russian subtitle candidate found on https://www.opensubtitles.org/, including its URL and `translator` field;
- the context sources or notes used;
- the exact Russian output path;
- validator result;
- any unresolved ambiguity or manual review point.

## Decision rules

- Exact release match is more important than a convenient download. Ask when the evidence conflicts.
- The English subtitle is the default translation source. A found Russian subtitle may be used only if the user explicitly chooses it after seeing its OpenSubtitles URL and `translator` value.
- If OpenSubtitles is unavailable, report that and ask the user to provide a source subtitle; do not silently use a random subtitle from another release.
- If the source is not SRT, convert it to a working SRT only while preserving cue order, timings, line distribution, and markup, then validate the translated SRT against that normalized source.
- Never edit, rename, move, or re-encode the video as part of this workflow.
- A translation is not complete until the file exists beside the video and the structural check passes.

## Resources

- Use `scripts/validate_srt.py` for deterministic structural checks.
- Use `references/context-and-release.md` for the compact research and release-matching checklist.
