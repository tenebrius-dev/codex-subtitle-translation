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
2. open or search `https://www.opensubtitles.org/` directly in a browser and determine subtitle availability from the page's live result rows, then verify English subtitles for each exact release;
3. research the film or series context before translating;
4. translate into Russian with the source line distribution and SRT structure unchanged;
5. validate and save each finished subtitle beside its video using the exact video basename.

Do not ask the user to repeat these steps or to mention `$codex-subtitle-translation`. The skill is configured for implicit invocation. If any Russian OpenSubtitles candidate exists, a user decision is mandatory before selecting it or starting a new translation: show the candidate information and wait for an explicit `продолжить` or `остановиться`.

The default target language is Russian. The default source language is English when an English release subtitle is available. A request that supplies a subtitle file or URL overrides the search step, but the source must still be checked against the video release.

## Workflow

### 1. Identify the input

- If the user gives a video file, process that file.
- If the user gives a folder, first inspect the folder's root. If the root contains one or more recognized video files, process those files. If the root contains no recognized video files, recursively inspect the entire descendant tree and process every recognized video file found. Sort the final list naturally by season and episode, then by path.
- Do not stop at the first nested folder and do not require the user to list subfolders manually. Ignore hidden/system directories unless the user explicitly names one.
- Recognize common video extensions: `.mkv`, `.mp4`, `.avi`, `.mov`, `.m4v`, `.webm`, `.ts`, and `.m2ts`.
- Parse the exact release name from the video filename. Do not reduce the task to only a title and episode number.
- Check for existing sidecar subtitles, but do not assume that a nearby file matches the release without checking its metadata and structure.

### 2. Find the source subtitle deterministically on OpenSubtitles

Use the live OpenSubtitles page at https://www.opensubtitles.org/; search-engine results, cached pages, season pages with stale counts, and web-fetch errors are not evidence that subtitles do or do not exist.

If the user supplies an OpenSubtitles URL, open that exact URL in the browser first. Follow an ordinary redirect to `opensubtitles.com` when the legacy domain redirects, and record the final page URL. Do not replace a supplied URL with a search-engine query. If no URL is supplied, search the complete video filename first, then title, season/episode, resolution, source, codec, and release group.

Treat subtitle availability as established only after inspecting the live DOM of the result page:

- verify the page heading contains the title, season, and episode;
- read the visible result count and enumerate every subtitle row;
- collect each row's subtitle ID/detail URL, language code (`eng`, `rus`, etc.), displayed release text, release flags, uploader, and file format;
- use the language-code links and row metadata, not only visually truncated language labels;
- open the detail page for every plausible English or Russian candidate before selecting it.

On each detail page, record the full subtitle filename, language, subtitle type (full dialogue, SDH, forced, commentary), runtime or final cue time, FPS, uploader, translator field, and release metadata. For the translator field, inspect the live DOM for `a.none[title="Translator"]` (including whitespace/newlines inside the element), read its visible `textContent`, and trim only surrounding whitespace. For example, `<a class="none" title="Translator">\n    (AppleTV)\n</a>` must be recorded exactly as `(AppleTV)`. Do not infer the translator from the uploader, comments, or filename; report `translator не указан` only when the Translator element is absent or visibly empty. Download only from the verified detail page and compare the downloaded subtitle's structure and final cue timestamp with the candidate metadata.

Compare the English candidate against the exact video filename using title, season/episode, source, resolution, codec, release group, runtime, FPS, cut, and cue timing. Treat a release group as evidence, not proof. A candidate with only the same title and episode is not an exact match.

Report one of these explicit availability states:

- `найдено, релиз совпадает` — a verified detail page and subtitle file match the requested release;
- `найдено, релиз не совпадает` — subtitles exist, but no candidate matches the requested release; include the exact filename(s);
- `не найдено` — the live OpenSubtitles result page and all relevant language/release filters were inspected and contain no candidate;
- `невозможно проверить` — the page is blocked by login, CAPTCHA, network failure, or another access problem; never convert this state into `не найдено`.

If no English candidate is clearly suitable, stop before translating and ask which verified candidate to use. Never silently substitute a subtitle from another release.

Check Russian candidates alongside the English search. First select and verify the English release source. If one or more Russian candidates exist, pause before downloading, selecting, or translating anything. Show every candidate separately with its OpenSubtitles detail URL, exact subtitle filename, language, subtitle type, release name, runtime/final cue time when available, uploader, and the `translator` field exactly as displayed (`translator не указан` only when the Translator element is absent or empty). Then ask whether to `продолжить` or `остановиться`, and wait for the explicit decision. Do not treat silence, an ambiguous reply, or an unrelated message as permission to continue.

After the user explicitly says `продолжить`, compare each Russian candidate only with the selected English candidate, not directly with the video release. Run `scripts/compare_srt_compatibility.py ENGLISH.srt RUSSIAN.srt`; require equal cue count, identical cue-number sequence, and identical timecodes for deterministic samples from the first three cues, the middle three cues, and the last three cues. The number of text lines inside a cue is not part of this release-compatibility decision. If a candidate's release metadata and compatibility test match the English candidate, use that Russian file automatically even when both differ from the video filename. If they do not match, do not use it; report its existence, exact filename, URL, and failed comparison, then use the English file for a new translation. If the user says `остановиться`, stop without selecting a Russian file, translating, or creating the final output.

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
- The English subtitle is the default reference source. When a Russian candidate exists, report it and wait for explicit `продолжить` or `остановиться` before any selection or translation. After `продолжить`, compare a Russian candidate with the selected English release, not directly with the video release. Use it only when its release metadata and `scripts/compare_srt_compatibility.py` checks match the English file; otherwise report its existence, exact filename/URL, and failed comparison, then translate from English.
- If OpenSubtitles is unavailable or access is blocked, report `невозможно проверить` and ask the user to provide a source subtitle; do not report `не найдено` and do not silently use a random subtitle from another release.
- Do not extract, inspect, or use embedded subtitle tracks from the video. The source must come from OpenSubtitles or from a subtitle file/URL explicitly supplied by the user.
- If the source is not SRT, convert it to a working SRT only while preserving cue order, timings, line distribution, and markup, then validate the translated SRT against that normalized source.
- Never edit, rename, move, or re-encode the video as part of this workflow.
- A translation is not complete until the file exists beside the video and the structural check passes.

## Resources

- Use `scripts/validate_srt.py` for deterministic structural checks.
- Use `scripts/compare_srt_compatibility.py` before accepting a Russian candidate as the equivalent of the selected English release.
- Use `references/context-and-release.md` for the compact research and release-matching checklist.
