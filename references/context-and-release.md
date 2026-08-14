# Context and release checklist

Use this checklist before translating a film or episode.

## Release matching

1. If the user supplies an OpenSubtitles URL, open that exact URL in a browser first; follow an ordinary redirect to `opensubtitles.com` and record the final URL.
2. Do not use search-engine results, cached pages, stale season counts, or web-fetch errors as proof of presence or absence.
3. Verify the live page heading, title, season, episode, visible result count, and every result row.
4. Extract subtitle ID/detail URL and language from the row's links, including `sublanguageid-eng` and `sublanguageid-rus`.
5. Open every plausible candidate's detail page and record the full filename, language, subtitle type, runtime/final cue timestamp, FPS, uploader, translator, and release metadata. Read the translator from the live DOM selector `a.none[title="Translator"]`; trim surrounding whitespace/newlines but preserve the displayed value, e.g. `(AppleTV)`. Do not infer it from uploader, comments, or filename. Use `translator не указан` only when that element is absent or empty.
6. Compare the requested video release and the selected English candidate by title, episode, source, resolution, codec, release group, runtime, FPS, cut, and cue timing.
7. Use these availability states: `найдено, релиз совпадает`; `найдено, релиз не совпадает` with exact filename(s); `не найдено` only after direct live-page/filter inspection; or `невозможно проверить` when access is blocked.
8. Search English and Russian candidates together. If any Russian candidate exists, stop before selecting, downloading, or translating; show every candidate's detail URL, exact filename, language, type, release name, runtime/final cue time, uploader, and exact `translator` field read from `a.none[title="Translator"]`, then wait for explicit `продолжить` or `остановиться`.
9. After `продолжить`, compare each Russian candidate only with the selected English release, not directly with the video release. Run `scripts/compare_srt_compatibility.py` and require equal cue count, identical cue-number sequence, and matching timings for the first three, middle three, and last three cues. Do not require equal text-line count for this release-compatibility decision. If all checks pass, use the Russian subtitle automatically even when both differ from the video; otherwise report its exact filename, URL, and failed comparison and translate from English.
10. If the user says `остановиться`, stop without selecting a Russian file, translating, or creating the final output. If the translator field is absent, say `translator не указан`.
11. Do not extract or use embedded subtitle tracks from the video.

The release group is useful evidence, not proof by itself. A subtitle that merely contains the same episode number is not an exact match. If the page cannot be inspected, report `невозможно проверить`, not `не найдено`.

## Embedded subtitle override

When the user says `используй субтитры из файла видео`, bypass OpenSubtitles and inspect the video's embedded tracks with MKVToolNix:

```bash
mkvmerge -i "VIDEO.mkv"
mkvextract "VIDEO.mkv" tracks TRACK_ID:"VIDEO.eng.srt"
```

Use an English full-dialogue text track. If there are several plausible English tracks, ask the user to choose by track ID/title/format. `S_TEXT/UTF8` and `S_TEXT/ASCII` tracks can be extracted directly as SRT; ASS/SSA requires conversion after extraction, while PGS and VobSub are image subtitles and require OCR before a text SRT can exist. Validate the resulting `VIDEO.eng.srt` before using it as the translation source. Keep the full video basename and add only `.eng` before `.srt`.

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
