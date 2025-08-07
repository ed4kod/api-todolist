
# Telegram TodoList Bot

Простой Telegram-бот для управления списком задач (todo list) с использованием Python, aiogram и async SQLAlchemy.

---

## Установка и запуск

1. Клонируйте репозиторий
```bash
  git clone https://github.com/yourusername/telegram-todolist-bot.git
```
2. Создайте и активируйте виртуальное окружение (рекомендуется)
```bash
  python -m venv .venv
  source .venv/bin/activate  # Linux / macOS
  .venv\Scripts\activate     # Windows
```
3. Установите зависимости
```bash
  pip install -r requirements.txt
```
4. Выполните миграции Alembic для создания нужных таблиц в базе данных:
```bash
  alembic upgrade head
```
5. Создайте .env файл или настройте переменные окружения с токеном бота и настройками базы данных (можете переименовать env.example в .env):
```bash
  cp env.example .env
```
   В файле `.env` укажите ваш токен бота и URL базы данных:
```bash
  TELEGRAM_BOT_TOKEN=ваш_токен_бота
  DATABASE_URL=sqlite+aiosqlite:///./tasks.db
```
6. Запустите бота
```bash
  python main.py
```