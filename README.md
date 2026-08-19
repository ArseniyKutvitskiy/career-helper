# Карьерный помощник

Веб-приложение для подготовки к собеседованиям. Пользователь выбирает роль и формат интервью, отвечает на вопрос, а Gemini даёт оценку и объясняет материал понятным языком.

## Стек

- **Frontend:** React, Vite, CSS, PWA.
- **Backend:** Python, Django, Django REST Framework.
- **ИИ:** Gemini API через официальную библиотеку `google-genai`.
- **Данные:** SQLite локально, PostgreSQL (Neon) в опубликованной версии.
- **Хостинг:** Render Static Site + Render Web Service.

## Структура проекта

```text
backend/
├── config/                 # Общие настройки Django и маршруты проекта
├── interviews/             # Логика тренировок и API
│   ├── models.py            # Модель сессии: вопрос, ответ, оценка, пользователь
│   ├── services.py          # Запросы к Gemini, промпты и проверка JSON-ответа
│   ├── views.py             # API-обработчики HTTP-запросов
│   ├── urls.py              # Адреса API
│   └── migrations/          # История изменений структуры базы данных
├── manage.py                # Команды Django: запуск, миграции, проверка
└── requirements.txt         # Python-зависимости

frontend/
├── src/
│   ├── App.jsx              # Экраны и состояние пользовательского интерфейса
│   ├── api.js               # Все запросы браузера к Django API
│   ├── main.jsx             # Точка входа React и регистрация PWA
│   ├── styles.css           # Основное оформление интерфейса
│   └── mentor.css           # Оформление понятной обратной связи ИИ
├── public/                  # Иконка, manifest и service worker для PWA
├── index.html               # HTML-оболочка React-приложения
└── package.json             # JavaScript-зависимости и команды Vite
```

## Как работает один ответ

1. React отправляет роль, описание вакансии и режим в `POST /api/questions/`.
2. Django в `views.py` вызывает `generate_question()` из `services.py`.
3. `services.py` формирует промпт, обращается к Gemini и требует структурированный JSON.
4. Django сохраняет вопрос в базе, а React показывает его пользователю.
5. После ответа React отправляет текст в `POST /api/sessions/<id>/answer/`.
6. Gemini возвращает оценку, объяснение, список терминов и совет; Django сохраняет результат и передаёт его интерфейсу.

## Запуск локально

Подробные инструкции по запуску и публикации находятся в [DEPLOY.md](DEPLOY.md).
