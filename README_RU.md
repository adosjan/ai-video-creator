# AI Video Creator - Полное руководство

## Что умеет система

**Полностью автоматическое создание YouTube видео:**

1. ✅ Анализирует YouTube видео
2. ✅ Генерирует уникальный скрипт (не копирует!)
3. ✅ Создает AI изображения (DALL-E или Midjourney)
4. ✅ Озвучивает текст (OpenAI TTS или ElevenLabs)
5. ✅ Добавляет фоновую музыку
6. ✅ Собирает финальное видео
7. ✅ Создает thumbnail для YouTube

**Результат:** Готовое видео для загрузки на YouTube!

---

## Быстрый старт

### 1. Создать полное видео (с голосом и музыкой)

```bash
python create_full_video.py
```

**Что нужно:**
- Ссылка на YouTube видео (скрипт спросит)
- Музыка (опционально, скрипт спросит путь)

**Что получите:**
- Готовое видео `.mp4`
- Thumbnail `.jpg`
- Все файлы в папке `output/`

---

## Все доступные скрипты

### 🎯 create_full_video.py - **ОСНОВНОЙ СКРИПТ**
**Что делает:** Создает полное видео с голосом и музыкой

```bash
python create_full_video.py
```

**Включает:**
- ✅ Анализ YouTube
- ✅ Генерация скрипта (GPT-4o)
- ✅ AI изображение (DALL-E 3)
- ✅ Озвучка (OpenAI TTS)
- ✅ Фоновая музыка (опционально)
- ✅ Финальное видео

**Стоимость:** ~$0.10 за видео

---

### 🖼️ create_video_with_dalle.py
**Что делает:** Создает видео с DALL-E (без звука)

```bash
python create_video_with_dalle.py
```

**Для тестирования изображений DALL-E**

---

### 🎨 create_video_no_audio.py
**Что делает:** Создает видео с простым фоном (без AI изображений)

```bash
python create_video_no_audio.py
```

**Для быстрого тестирования системы**

---

## Настройка

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. API ключи в файле .env

Откройте `.env` и заполните:

```env
# OpenAI API (ОБЯЗАТЕЛЬНО - для скрипта и TTS)
OPENAI_API_KEY=ваш_ключ_здесь

# ElevenLabs (ОПЦИОНАЛЬНО - если хотите лучше голос)
ELEVENLABS_API_KEY=ваш_ключ_здесь
ELEVENLABS_VOICE_ID=id_голоса
```

**Где взять ключи:**
- OpenAI: https://platform.openai.com/api-keys
- ElevenLabs: https://elevenlabs.io/app/settings/api-keys

---

## Выбор источника изображений

### Вариант 1: DALL-E (автоматический) - Рекомендуется

**Преимущества:**
- ✅ Полная автоматизация
- ✅ Официальный API
- ✅ Быстро (30-60 секунд)
- ✅ Не нужна регистрация в других сервисах

**Стоимость:** $0.08 за HD изображение

**Как использовать:**
```python
# В create_full_video.py уже настроено
use_dalle=True  # по умолчанию
```

---

### Вариант 2: Midjourney (полуавтоматический)

**Преимущества:**
- ✅ Лучшее качество изображений
- ✅ Художественный стиль
- ✅ У вас уже есть подписка

**Недостатки:**
- ⏱️ Требует 1-2 минуты ручной работы

**Как использовать:**
```python
# В create_full_video.py измените:
use_dalle=False  # использовать Midjourney

# Скрипт покажет промпт, вы:
# 1. Копируете в Discord
# 2. Создаете изображение
# 3. Сохраняете в папку temp/
# 4. Нажимаете Enter в скрипте
```

---

## Выбор голоса (TTS)

### Вариант 1: OpenAI TTS (работает сейчас)

**Голоса:**
- `onyx` - глубокий мужской (по умолчанию)
- `echo` - мужской
- `fable` - британский мужской
- `alloy` - нейтральный
- `nova` - женский
- `shimmer` - мягкий женский

**Стоимость:** $0.015 за 1000 символов (~$0.02 за короткое видео)

**Качество:** Очень высокое, естественное звучание

**Настройка в openai_tts.py:**
```python
self.default_voice = "onyx"  # измените здесь
```

---

### Вариант 2: ElevenLabs (когда заработает)

**Преимущества:**
- Еще более естественный голос
- Больше эмоций
- У вас есть подписка

**Проблема:** Ваш API ключ пока не работает

**Когда заработает:**
Откройте `create_full_video.py` и замените:
```python
from openai_tts import OpenAITTS
tts = OpenAITTS()
```

На:
```python
from elevenlabs_tts import ElevenLabsTTS
tts = ElevenLabsTTS()
```

---

## Добавление фоновой музыки

### Шаг 1: Скачать музыку

**Бесплатные источники:**
1. **YouTube Audio Library** - https://www.youtube.com/audiolibrary
   - Лучший выбор!
   - Полностью бесплатно
   - Для коммерческого использования

2. **Pixabay** - https://pixabay.com/music/

3. **Incompetech** - https://incompetech.com/music/

Подробнее: см. файл `MUSIC_SOURCES.md`

### Шаг 2: Создать папку music

```bash
mkdir music
```

Сохраняйте всю музыку туда

### Шаг 3: Использовать в скрипте

**Вариант A: Скрипт спросит сам**
```bash
python create_full_video.py
# Скрипт спросит: "Music path:"
# Введите: music/background.mp3
```

**Вариант B: В коде**
```python
create_full_video(
    youtube_url="...",
    background_music_path="music/background.mp3",
    music_volume=0.15  # 15% громкости (не заглушает голос)
)
```

---

## Примеры использования

### Пример 1: Базовое видео с DALL-E

```bash
python create_full_video.py
# YouTube URL: https://www.youtube.com/watch?v=...
# Music path: [Enter для пропуска]
```

Результат: видео с AI изображением и голосом (без музыки)

---

### Пример 2: Полное видео с музыкой

```bash
python create_full_video.py
# YouTube URL: https://www.youtube.com/watch?v=...
# Music path: music/background.mp3
```

Результат: видео с изображением, голосом и музыкой

---

### Пример 3: С Midjourney

Измените в `create_full_video.py`:
```python
use_dalle=False
```

Запустите:
```bash
python create_full_video.py
```

Система покажет промпт → создайте в Discord → нажмите Enter

---

## Структура проекта

```
ai-video-creator/
├── create_full_video.py          # ГЛАВНЫЙ СКРИПТ
├── create_video_with_dalle.py    # Тест DALL-E
├── create_video_no_audio.py      # Быстрый тест
│
├── youtube_analyzer.py            # Анализ YouTube
├── script_generator.py            # Генерация скрипта (GPT-4o)
├── dalle_generator.py             # DALL-E изображения
├── openai_tts.py                  # OpenAI TTS голос
├── elevenlabs_tts.py              # ElevenLabs голос
├── thumbnail_generator.py         # Создание thumbnail
├── video_editor.py                # Сборка видео
│
├── config.py                      # Настройки
├── .env                           # API ключи
├── requirements.txt               # Зависимости
│
├── output/                        # Готовые видео
├── temp/                          # Временные файлы
├── music/                         # Фоновая музыка
│
└── README_RU.md                   # Это руководство
```

---

## Стоимость создания одного видео

### С DALL-E (автоматически):
- GPT-4o скрипт: $0.01
- DALL-E 3 HD: $0.08
- OpenAI TTS: $0.02
- **ИТОГО: ~$0.11 за видео**

### С Midjourney (полуавтоматически):
- GPT-4o скрипт: $0.01
- Midjourney: ваша подписка ($10-60/месяц)
- OpenAI TTS: $0.02
- **ИТОГО: ~$0.03 + подписка**

---

## Частые вопросы

### Q: ElevenLabs не работает?
A: Используйте OpenAI TTS - качество тоже отличное! Система уже настроена на него.

### Q: Где взять музыку?
A: YouTube Audio Library (бесплатно) - см. MUSIC_SOURCES.md

### Q: DALL-E или Midjourney?
A:
- DALL-E для автоматизации
- Midjourney для лучшего качества (1-2 мин работы)

### Q: Сколько стоит создать 30 видео?
A:
- С DALL-E: ~$3.30
- С Midjourney: ~$0.90 + подписка MJ

### Q: Можно использовать свои изображения?
A: Да! Положите в папку temp/ с правильным именем

### Q: Как изменить голос?
A: Откройте openai_tts.py, измените self.default_voice

### Q: Видео получаются уникальные?
A: Да! GPT-4o создает новый контент, не копирует

---

## Что дальше?

### 1. Протестируйте систему
```bash
python create_full_video.py
```

### 2. Скачайте музыку
- YouTube Audio Library
- Сохраните в папку music/

### 3. Создайте первое видео
- Выберите интересное YouTube видео
- Запустите скрипт
- Получите готовое видео!

### 4. Загрузите на YouTube
- Используйте видео из output/
- Используйте thumbnail из output/
- Копируйте title и description из вывода скрипта

---

## Поддержка

Если что-то не работает:
1. Проверьте .env файл (API ключи)
2. Проверьте requirements.txt (зависимости)
3. Проверьте вывод ошибок в консоли

**Система готова к использованию! Создавайте видео!** 🎬
