# Codex Subtitle Translation

## Русский

Навык Codex для контекстного перевода субтитров на русский язык.

Он работает с одним видеофайлом или папкой с фильмом/сериалом и выполняет полный сценарий:

1. находит видеофайл или список серий;
2. ищет английские субтитры на OpenSubtitles под точный релиз;
3. проверяет название, сезон, серию, разрешение, источник, кодек, release group и тайминги;
4. изучает контекст фильма или сериала, персонажей и терминологию;
5. переводит субтитры на русский язык;
6. сохраняет номера реплик, таймкоды, количество строк и оформление SRT;
7. проверяет готовый файл;
8. сохраняет результат рядом с видео с тем же именем.

Если в указанной папке нет видеофайлов в корне, навык автоматически проверяет все вложенные папки и обрабатывает найденные там видеофайлы. Перечислять подпапки вручную не нужно.

### Быстрый запуск

Достаточно написать в Codex:

```text
Сделай русские субтитры для серии /path/to/series-folder
```

Или для одного файла:

```text
Сделай русские субтитры для /path/to/movie.mkv
```

Повторять инструкцию и явно указывать `$codex-subtitle-translation` не обязательно: навык настроен на автоматический запуск по такому запросу.

Для принудительного запуска можно написать:

```text
Используй $codex-subtitle-translation.
Сделай русские субтитры для /path/to/series-folder
```

### Имена файлов

Для видео:

```text
/path/Example.Movie.2025.1080p.WEB-DL.mkv
```

результат сохраняется как:

```text
/path/Example.Movie.2025.1080p.WEB-DL.srt
```

Имя релиза сохраняется полностью. Суффиксы `.ru`, `.rus`, `.translated` и подобные не добавляются.

### Важные правила

- Если найдено несколько разных релизов, навык запрашивает уточнение.
- Субтитры от другого релиза не подставляются молча.
- Если в корне указанной папки нет видеофайлов, проверяется всё дерево вложенных папок.
- При обработке папки каждая серия сохраняется сразу после перевода и проверки.
- Видео не переименовывается, не перемещается и не перекодируется.
- Если пользователь передаёт готовый SRT или ссылку, он используется как исходник после проверки соответствия видео.

### Ручная проверка SRT

Встроенный скрипт проверяет количество реплик, номера, таймкоды, количество строк и теги оформления:

```bash
python3 ~/.codex/skills/codex-subtitle-translation/scripts/validate_srt.py \
  "/path/source.en.srt" \
  "/path/translated.srt"
```

Скрипт не требует сторонних Python-библиотек.

### Установка из GitHub

```bash
git clone https://github.com/tenebrius-dev/codex-subtitle-translation.git \
  ~/.codex/skills/codex-subtitle-translation
```

После установки перезапустите Codex или начните новый запрос, чтобы навык появился в списке доступных навыков.

## English

Codex skill for context-aware translation of subtitles into Russian.

It accepts a single video file or a movie/series folder and performs the complete workflow:

1. finds the video file or episode list;
2. searches OpenSubtitles for English subtitles matching the exact release;
3. verifies the title, season, episode, resolution, source, codec, release group, and timing;
4. researches the film or series context, characters, and terminology;
5. translates the subtitles into Russian;
6. preserves cue numbers, timecodes, line count, and SRT formatting;
7. validates the completed file;
8. saves the result next to the video using the same basename.

If the specified folder has no video files directly in its root, the skill automatically scans all nested folders and processes the video files it finds. You do not need to list subfolders manually.

### Quick start

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

### Output naming

For:

```text
/path/Example.Movie.2025.1080p.WEB-DL.mkv
```

the output is:

```text
/path/Example.Movie.2025.1080p.WEB-DL.srt
```

The complete release name is preserved. No `.ru`, `.rus`, `.translated`, or similar suffix is added.

### Key rules

- If multiple candidates belong to different releases, the skill asks for clarification.
- A subtitle from another release is never silently substituted.
- If the folder root has no video files, the entire nested directory tree is scanned.
- When processing a folder, each episode is saved immediately after translation and validation.
- Video files are never renamed, moved, or re-encoded.
- A supplied SRT file or URL is used as the source after checking that it matches the video.

### Manual SRT validation

The bundled script checks cue count, cue numbers, timecodes, text-line count, and formatting tags:

```bash
python3 ~/.codex/skills/codex-subtitle-translation/scripts/validate_srt.py \
  "/path/source.en.srt" \
  "/path/translated.srt"
```

The script has no third-party Python dependencies.

### Install from GitHub

```bash
git clone https://github.com/tenebrius-dev/codex-subtitle-translation.git \
  ~/.codex/skills/codex-subtitle-translation
```

Restart Codex or start a new request after installation so the skill can be discovered.
