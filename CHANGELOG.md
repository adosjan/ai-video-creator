# Changelog

Все заметные изменения проекта **AI Video Creator** будут отражаться в этом файле.

Формат основан на принципах [Keep a Changelog](https://keepachangelog.com/) и [Semantic Versioning](https://semver.org/).

## [1.0.0] - 2026-02-06

### Добавлено

- **Полный пайплайн генерации видео**: анализ YouTube → генерация скрипта → подготовка промпта под изображение → озвучка → генерация thumbnail → сборка финального `.mp4`.
- **Анализ исходного YouTube-видео**:
  - извлечение метаданных через `yt-dlp` (заголовок, описание, длительность, просмотры, теги и т.д.)
  - загрузка транскрипта через `youtube-transcript-api` (с фолбэками при отсутствии нужного языка)
  - простая структурная аналитика (ключевые темы, наличие intro/outro, примерная длительность речи).
- **Генерация скриптов** через Google Gemini (`script_generator.py`) с настройкой ключа через `.env` (`GEMINI_API_KEY`/`gemini_api_key`).
- **Генерация изображений**:
  - DALL‑E 3 через официальный OpenAI API (`dalle_generator.py`)
  - полуавтоматический режим Midjourney: генерация промпта и пошаговая инструкция для Discord (ручное сохранение изображения в `temp/`).
- **Озвучка (TTS)**:
  - OpenAI TTS в сценарии полного видео (`openai_tts.py`, `create_full_video.py`)
  - интеграция ElevenLabs TTS в оркестраторе (`elevenlabs_tts.py`, `main.py`).
- **Монтаж и экспорт**:
  - сборка видео из изображения(й) + аудио в `mp4` через MoviePy/FFmpeg (`video_editor.py`, `create_full_video.py`)
  - опциональное добавление фоновой музыки и микширование (при наличии FFmpeg) через `pydub`.
- **Генератор thumbnail** с режимами оформления (например, `clickbait`/`professional`/`educational`) (`thumbnail_generator.py`).
- **Точки входа/скрипты запуска** для разных сценариев:
  - `main.py` (интерактивный режим + оркестратор)
  - `create_full_video.py` (полный workflow)
  - `create_video_quick.py`, `create_video_no_audio.py`, `create_video_no_tts.py`, `create_video_with_dalle.py`, `create_video.py` (варианты упрощённых прогонов).
- **Документация и справочные материалы**: `README.md`, `README_RU.md`, `QUICKSTART.md`, `MUSIC_SOURCES.md`, `IMAGE_GENERATION_OPTIONS.md`.
- **Шаблон окружения**: `.env.example`.

### Известные ограничения

- **Midjourney по умолчанию требует ручного шага** (сохранение изображения из Discord в `temp/`); автоматизация требует отдельной настройки.
- **Фоновая музыка** зависит от наличия FFmpeg в системе (в противном случае видео будет собираться без микширования музыки).