# 🎬 AI Video Creator

Автоматическая система создания YouTube видео на основе анализа успешных каналов.

## 🚀 Возможности

- 📊 **Анализ YouTube видео** - извлечение транскриптов и метаданных
- 🤖 **AI генерация скриптов** - создание уникального контента на основе темы
- 🎤 **ElevenLabs озвучка** - профессиональная озвучка на английском
- 🎨 **Midjourney обложки** - автоматическая генерация thumbnails
- 🎬 **Автомонтаж** - сборка финального видео
- 📤 **Загрузка на YouTube** - автоматическая публикация

## 📦 Установка

### 1. Клонируйте репозиторий или создайте проект

```bash
cd ai-video-creator
```

### 2. Создайте виртуальное окружение

```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

### 3. Установите зависимости

```bash
pip install -r requirements.txt
```

### 4. Настройте переменные окружения

Скопируйте `.env.example` в `.env` и заполните свои API ключи:

```bash
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac
```

Откройте `.env` и заполните:
- `OPENAI_API_KEY` - ваш ключ OpenAI
- `ELEVENLABS_API_KEY` - ваш ключ ElevenLabs
- `ELEVENLABS_VOICE_ID` - ID голоса из ElevenLabs
- `DISCORD_BOT_TOKEN` - токен Discord бота для Midjourney
- `MIDJOURNEY_SERVER_ID` - ID сервера Discord
- `MIDJOURNEY_CHANNEL_ID` - ID канала для Midjourney

## 🎯 Использование

### Базовый пример:

```python
from main import create_video_from_url

# Укажите URL успешного видео для анализа
video_url = "https://www.youtube.com/watch?v=example"

# Система автоматически:
# 1. Проанализирует видео
# 2. Создаст уникальный скрипт
# 3. Сгенерирует озвучку
# 4. Создаст обложку
# 5. Смонтирует видео
result = create_video_from_url(video_url)

print(f"✅ Видео создано: {result['video_path']}")
print(f"✅ Обложка создана: {result['thumbnail_path']}")
```

### Продвинутое использование:

```python
from main import VideoCreator

creator = VideoCreator(
    video_length="short",      # short, medium, long
    thumbnail_style="clickbait", # clickbait, professional, educational
    voice_id="your_voice_id"    # ElevenLabs voice ID
)

# Создать видео
result = creator.create_from_url(
    url="https://www.youtube.com/watch?v=example",
    custom_prompt="Make it more engaging and add statistics"
)
```

## 📁 Структура проекта

```
ai-video-creator/
├── config.py                 # Конфигурация и настройки
├── youtube_analyzer.py       # Анализ YouTube видео
├── script_generator.py       # AI генерация скриптов
├── midjourney_bot.py         # Интеграция с Midjourney
├── elevenlabs_tts.py         # Генерация озвучки
├── thumbnail_generator.py    # Создание обложек
├── video_editor.py           # Монтаж видео
├── youtube_uploader.py       # Загрузка на YouTube
├── main.py                   # Главный оркестратор
├── requirements.txt          # Зависимости
├── .env.example             # Шаблон переменных окружения
└── README.md                # Документация
```

## ⚠️ Важные замечания

### Легальность и этика:

1. **НЕ копируйте контент** - система создает УНИКАЛЬНЫЙ контент на основе темы
2. **Добавляйте ценность** - ваши видео должны быть трансформативными
3. **Проверяйте перед публикацией** - всегда просматривайте результат
4. **Соблюдайте авторские права** - не используйте чужие изображения/видео
5. **YouTube политика** - соблюдайте правила YouTube

### Технические требования:

- Python 3.8+
- FFmpeg установлен в системе
- Стабильное интернет соединение (для API)
- ~5-10 минут на создание одного видео

## 🔑 Получение API ключей

### OpenAI:
1. Зарегистрируйтесь на https://platform.openai.com
2. Создайте API ключ в настройках
3. Пополните баланс ($5-10 минимум)

### ElevenLabs:
1. Зарегистрируйтесь на https://elevenlabs.io
2. Выберите подписку (Starter или выше)
3. Скопируйте API ключ из Settings
4. Выберите голос и скопируйте Voice ID

### Discord/Midjourney:
1. Создайте Discord бота: https://discord.com/developers
2. Добавьте бота на свой сервер
3. Пригласите Midjourney бота на тот же сервер
4. Скопируйте Server ID и Channel ID

## 📈 Примеры использования

### YouTube Shorts (до 60 сек):
```python
creator = VideoCreator(video_length="short")
creator.create_from_url("https://youtube.com/...")
```

### Средние видео (5-10 мин):
```python
creator = VideoCreator(video_length="medium")
creator.create_from_url("https://youtube.com/...")
```

### Пакетное создание:
```python
urls = [
    "https://youtube.com/watch?v=...",
    "https://youtube.com/watch?v=...",
]

for url in urls:
    result = creator.create_from_url(url)
    print(f"✅ Создано: {result['title']}")
```

## 🤝 Поддержка

Если возникли вопросы или проблемы, проверьте:
1. Все ли API ключи правильно настроены в `.env`
2. Установлен ли FFmpeg в системе
3. Достаточно ли баланса на API аккаунтах

## 📝 Лицензия

MIT License - используйте ответственно!

## ⚡ Roadmap

- [ ] Поддержка нескольких языков
- [ ] Интеграция с Stable Diffusion (альтернатива Midjourney)
- [ ] Автоматическое SEO (теги, описание)
- [ ] A/B тестирование обложек
- [ ] Аналитика и отчеты
- [ ] Планировщик публикаций

---

**Сделано с ❤️ для создателей контента**
