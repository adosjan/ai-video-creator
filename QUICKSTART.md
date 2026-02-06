# 🚀 Быстрый старт - AI Video Creator

## 📋 Что вам понадобится

### Обязательные API ключи:
1. **OpenAI API Key** - для генерации скриптов
2. **ElevenLabs API Key + Voice ID** - для озвучки
3. **Midjourney подписка** (через Discord) - для создания изображений

### Опционально:
- YouTube API credentials - для автозагрузки видео

## 🔧 Установка за 5 минут

### Шаг 1: Установите Python зависимости

```bash
cd ai-video-creator
pip install -r requirements.txt
```

### Шаг 2: Установите FFmpeg

**Windows:**
1. Скачайте FFmpeg: https://ffmpeg.org/download.html
2. Распакуйте и добавьте в PATH

**Или через Chocolatey:**
```bash
choco install ffmpeg
```

### Шаг 3: Настройте .env файл

Скопируйте `.env.example` в `.env`:
```bash
copy .env.example .env
```

Откройте `.env` и заполните:

```env
# OpenAI (обязательно)
OPENAI_API_KEY=sk-your-key-here

# ElevenLabs (обязательно)
ELEVENLABS_API_KEY=your-elevenlabs-key
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM

# Discord/Midjourney (опционально, для автоматизации)
DISCORD_BOT_TOKEN=your-bot-token
MIDJOURNEY_SERVER_ID=your-server-id
MIDJOURNEY_CHANNEL_ID=your-channel-id
```

## 🎬 Как получить API ключи

### OpenAI API Key
1. Перейдите на https://platform.openai.com
2. Зарегистрируйтесь/войдите
3. Перейдите в API Keys
4. Создайте новый ключ
5. Пополните баланс ($10 минимум)

### ElevenLabs API Key и Voice ID
1. Перейдите на https://elevenlabs.io
2. Зарегистрируйтесь и выберите план (Starter минимум)
3. В настройках скопируйте API Key
4. Перейдите в VoiceLab
5. Выберите голос и скопируйте Voice ID

### Midjourney через Discord
**Вариант 1: Ручной режим (рекомендуется для начала)**
- Просто имейте активную подписку Midjourney
- Система сгенерирует промпт, вы вручную создадите картинку

**Вариант 2: Автоматический (требует настройки)**
1. Создайте Discord бота: https://discord.com/developers
2. Добавьте бота на свой сервер
3. Пригласите Midjourney бота на тот же сервер
4. Заполните DISCORD_BOT_TOKEN, SERVER_ID, CHANNEL_ID в .env

## ✅ Проверка установки

Запустите:
```bash
python main.py
```

Если увидите сообщение "All systems ready!" - всё настроено правильно!

## 🎥 Создание первого видео

### Вариант 1: Интерактивный режим

```bash
python main.py
```

Следуйте инструкциям на экране.

### Вариант 2: Из кода

Создайте файл `test.py`:

```python
from main import VideoCreator

# Инициализация
creator = VideoCreator(
    video_length="short",      # "short", "medium", "long"
    thumbnail_style="clickbait" # "clickbait", "professional", "educational"
)

# Создание видео из YouTube URL
result = creator.create_from_url(
    url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"
)

if result['success']:
    print(f"✅ Видео создано: {result['video_path']}")
    print(f"🖼️ Обложка: {result['thumbnail_path']}")
else:
    print(f"❌ Ошибка: {result['error']}")
```

Запустите:
```bash
python test.py
```

## 📊 Процесс создания видео

Система автоматически:

1. 📊 **Анализирует** исходное YouTube видео
2. 🤖 **Генерирует** уникальный скрипт на основе темы
3. 🎤 **Озвучивает** скрипт через ElevenLabs
4. 🎨 **Создаёт** промпт для Midjourney
5. 🖼️ **Генерирует** обложку с текстом
6. 🎬 **Монтирует** финальное видео

## ⏱️ Сколько времени занимает?

- **Ручной режим:** ~5-10 минут
  - Анализ: 30 сек
  - Генерация скрипта: 30 сек
  - Озвучка: 1-2 мин
  - Midjourney (ручное): 2-3 мин
  - Монтаж: 1-2 мин

- **Автоматический режим:** ~3-5 минут

## 💰 Примерная стоимость за видео

- OpenAI (GPT-4o): ~$0.10-0.30
- ElevenLabs: зависит от плана (~$0.05-0.15)
- Midjourney: входит в подписку ($10-$30/месяц)

**Итого: ~$0.15-0.45 за видео** (без учета подписок)

## 🎯 Примеры использования

### YouTube Shorts (60 сек)
```python
creator = VideoCreator(video_length="short")
result = creator.create_from_url(url)
```

### Средние видео (5 минут)
```python
creator = VideoCreator(video_length="medium")
result = creator.create_from_url(url)
```

### Пакетное создание
```python
urls = [
    "https://youtube.com/watch?v=...",
    "https://youtube.com/watch?v=...",
    "https://youtube.com/watch?v=..."
]

results = creator.create_batch(urls)

for i, result in enumerate(results):
    if result['success']:
        print(f"✅ Видео {i+1}: {result['video_path']}")
```

### Кастомные инструкции
```python
result = creator.create_from_url(
    url="https://youtube.com/...",
    custom_prompt="Make it more dramatic and add statistics"
)
```

## 🐛 Устранение проблем

### "No module named 'moviepy'"
```bash
pip install moviepy
```

### "FFmpeg not found"
Установите FFmpeg и добавьте в PATH

### "OpenAI API key is required"
Проверьте, что `.env` файл существует и содержит `OPENAI_API_KEY`

### "Could not get transcript"
Видео не имеет субтитров на английском. Система всё равно попытается создать контент на основе метаданных.

### Видео не монтируется
Проверьте, что FFmpeg установлен:
```bash
ffmpeg -version
```

## 📁 Где найти результаты?

Все файлы сохраняются в:
- **Видео:** `output/`
- **Временные файлы:** `temp/`

Структура:
```
output/
├── video_20240203_153045.mp4
├── video_20240203_153045_thumbnail.jpg
temp/
├── video_20240203_153045_audio.mp3
├── video_20240203_153045_background.png
```

## 🎓 Следующие шаги

1. **Протестируйте** систему на нескольких видео
2. **Экспериментируйте** с разными стилями и длинами
3. **Настройте** автоматизацию Midjourney (опционально)
4. **Добавьте** YouTube API для автозагрузки
5. **Масштабируйте** - создавайте видео пакетами

## 💡 Советы для лучших результатов

1. **Выбирайте популярные видео** с хорошими субтитрами
2. **Используйте конкретные ниши** - не generic темы
3. **Проверяйте результат** перед публикацией
4. **Добавляйте свою изюминку** через custom_prompt
5. **Тестируйте разные голоса** в ElevenLabs

## ⚖️ Важно о легальности

✅ **Правильно:**
- Брать тему и создавать свой контент
- Добавлять новые примеры и перспективу
- Делать трансформативный контент

❌ **Неправильно:**
- Копировать скрипт слово в слово
- Использовать чужие видео/изображения
- Публиковать без проверки

## 🤝 Нужна помощь?

1. Проверьте README.md
2. Прочитайте код модулей (хорошо документирован)
3. Проверьте примеры в каждом файле

---

**Готовы создавать вирусные видео? Удачи! 🚀**
