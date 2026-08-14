# Codex Subtitle Translation

[Русский](README.md) | [English](README.en.md)

Codex skill for context-aware translation of subtitles into Russian.

## Features

The skill works with a single video file or a movie/series folder and:

1. finds the video file or episode list;
2. searches [opensubtitles.org](https://www.opensubtitles.org/) for English subtitles matching the exact release;
3. verifies the title, season, episode, resolution, source, codec, release group, and timing;
4. researches the film or series context, characters, and terminology;
5. translates the subtitles into Russian;
6. preserves cue numbers, timecodes, text-line count, and SRT formatting;
7. validates the completed file;
8. saves the result next to the video using the same basename.

If the specified folder has no video files directly in its root, the skill automatically scans all nested folders and processes the video files it finds. You do not need to list subfolders manually.

At the same time, the skill checks [opensubtitles.org](https://www.opensubtitles.org/) for existing Russian subtitles matching the same release. If any are found, it offers each one before translating and shows its URL and the `translator` field value. If the field is empty, it reports `translator not specified`. Existing Russian subtitles are never selected automatically.

## Quick start

Simply ask Codex:

```text
Make Russian subtitles for /path/to/series-folder
```

Or for one movie:

```text
Make Russian subtitles for /path/to/movie.mkv
```

You do not need to repeat the workflow or explicitly mention `$codex-subtitle-translation`; the skill is configured for automatic invocation from this kind of request.

For an explicit invocation:

```text
Use $codex-subtitle-translation.
Make Russian subtitles for /path/to/series-folder
```

## Output naming

For:

```text
/path/Example.Movie.2025.1080p.WEB-DL.mkv
```

the output is:

```text
/path/Example.Movie.2025.1080p.WEB-DL.srt
```

The complete release name is preserved. No `.ru`, `.rus`, `.translated`, or similar suffix is added.

## Rules

- If multiple candidates belong to different releases, the skill asks for clarification.
- A subtitle from another release is never silently substituted.
- Found Russian subtitles are offered with their URL and `translator` field value.
- If the folder root has no video files, the entire nested directory tree is scanned.
- When processing a folder, each episode is saved immediately after translation and validation.
- Video files are never renamed, moved, or re-encoded.
- A supplied SRT file or URL is used as the source after checking that it matches the video.

## Manual SRT validation

The bundled script checks cue count, cue numbers, timecodes, text-line count, and formatting tags:

```bash
python3 ~/.codex/skills/codex-subtitle-translation/scripts/validate_srt.py \
  "/path/source.en.srt" \
  "/path/translated.srt"
```

The script has no third-party Python dependencies.

## Install from GitHub

```bash
git clone https://github.com/tenebrius-dev/codex-subtitle-translation.git \
  ~/.codex/skills/codex-subtitle-translation
```

Restart Codex or start a new request after installation so the skill can be discovered.
