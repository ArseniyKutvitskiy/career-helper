# Публикация «Карьерного помощника»

После этой инструкции приложение будет доступно по своему HTTPS-адресу из любого браузера. Рекомендуемая связка:

- **Vercel** — интерфейс React;
- **Render** — Django API;
- **Neon Postgres** — постоянная база с аккаунтами и историей.

> Почему не SQLite: на бесплатном Render локальные файлы удаляются при перезапуске. Postgres сохраняет историю независимо от перезапусков сервера.

## 1. Проверка на компьютере

Откройте терминал в VS Code и выполните:

```powershell
cd D:\Проект\backend
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Во втором терминале:

```powershell
cd D:\Проект\frontend
npm install
npm run build
```

Не публикуйте файлы `backend/.env` и `frontend/.env`: в них находятся секреты.

## 2. Загрузите код на GitHub

1. Создайте аккаунт на [GitHub](https://github.com/) и нажмите **New repository**.
2. Назовите репозиторий, например `career-helper`. Выберите **Private**, чтобы исходный код был виден только вам.
3. В терминале VS Code выполните команды ниже, заменив URL на URL созданного репозитория:

```powershell
cd D:\Проект
git init
git add .
git commit -m "Первая версия Карьерного помощника"
git branch -M main
git remote add origin https://github.com/ВАШ-ЛОГИН/career-helper.git
git push -u origin main
```

При первом `git push` GitHub может открыть окно входа в аккаунт — войдите и разрешите доступ.

## 3. Создайте постоянную базу Neon

1. Зарегистрируйтесь на [Neon](https://neon.com/).
2. Нажмите **Create project**, выберите Postgres и ближайший регион.
3. На странице проекта откройте **Connect** и скопируйте строку подключения. Она начинается с `postgresql://`.
4. Сохраните её: это значение `DATABASE_URL`. Не публикуйте строку в чатах, скриншотах или GitHub.

У Neon есть бесплатный план для небольших личных проектов; база может останавливаться при простое и запускаться при новом запросе. [Условия Neon Free](https://neon.com/pricing)

## 4. Опубликуйте Django API на Render

1. Зарегистрируйтесь на [Render](https://render.com/) через GitHub.
2. Нажмите **New → Web Service** и выберите репозиторий `career-helper`.
3. Заполните форму:

| Поле | Значение |
| --- | --- |
| Name | `career-helper-api` |
| Language | Python 3 |
| Branch | `main` |
| Root Directory | `backend` |
| Build Command | `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate` |
| Start Command | `gunicorn config.wsgi:application` |
| Instance Type | Free |

4. В разделе **Environment** добавьте переменные:

| Ключ | Значение |
| --- | --- |
| `GEMINI_API_KEY` | Ваш ключ из Google AI Studio |
| `DJANGO_SECRET_KEY` | Длинная случайная строка (Render может сгенерировать её) |
| `DEBUG` | `False` |
| `DATABASE_URL` | Строка подключения Neon из шага 3 |
| `CORS_ALLOWED_ORIGINS` | Пока `http://localhost:5173` |

5. Нажмите **Create Web Service** и дождитесь статуса **Live**.
6. Скопируйте адрес API, например: `https://career-helper-api.onrender.com`.

Бесплатный сервер Render засыпает после 15 минут без запросов; первое открытие после паузы может занять около минуты. Это нормальное ограничение Free-плана. [Ограничения Render Free](https://render.com/docs/free)

## 5. Опубликуйте интерфейс на Vercel

1. Зарегистрируйтесь на [Vercel](https://vercel.com/) через GitHub.
2. Нажмите **Add New → Project** и импортируйте репозиторий `career-helper`.
3. В настройках проекта задайте:
   - **Root Directory:** `frontend`
   - **Framework Preset:** Vite
4. Откройте **Environment Variables** и добавьте:

```
VITE_API_URL=https://career-helper-api.onrender.com/api
```

Замените домен на адрес из Render. Нажмите **Deploy**.

5. После публикации скопируйте адрес Vercel, например `https://career-helper.vercel.app`.

Vercel передаёт в Vite только переменные, начинающиеся с `VITE_`, поэтому используется именно `VITE_API_URL`. [Документация Vercel для Vite](https://vercel.com/docs/frameworks/frontend/vite)

## 6. Свяжите сайты

Вернитесь в Render → ваш API → **Environment** и измените:

```
CORS_ALLOWED_ORIGINS=https://career-helper.vercel.app
```

Подставьте ваш настоящий Vercel-адрес, сохраните и выберите **Save, rebuild, and deploy**.

После успешного деплоя откройте Vercel-адрес. Создайте тестовый профиль и проведите одну тренировку — история должна появиться во вкладке «Прогресс».

## 7. Обновление сайта

После изменения файлов на компьютере:

```powershell
cd D:\Проект
git add .
git commit -m "Описание изменения"
git push
```

Render и Vercel автоматически опубликуют новую версию.

## 8. Свой домен (необязательно)

Купите домен у любого регистратора, затем добавьте его в настройках проекта Vercel. Vercel покажет DNS-записи, которые нужно добавить у регистратора. HTTPS-сертификат будет выпущен автоматически.

## Финальная проверка

- `GEMINI_API_KEY` есть только в Environment Render, а не в GitHub.
- `DEBUG=False` на Render.
- `VITE_API_URL` содержит `https://.../api`.
- `CORS_ALLOWED_ORIGINS` содержит точный HTTPS-адрес Vercel без косой черты в конце.
- `DATABASE_URL` указывает на Neon, а не на SQLite.

