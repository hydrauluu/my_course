# Python Engineering Course Platform

Образовательная платформа для курса «Python Engineering Course» — 14 лекций по глубокому погружению в Python.

## Технологический стек

| Компонент | Технология |
|---|---|
| Frontend | React 18 + TypeScript + Tailwind CSS + shadcn/ui |
| Backend | FastAPI (Python 3.12+) |
| Database | PostgreSQL 16 |
| Queue | Celery + Redis |
| AI-ревью | Claude API (Anthropic) |
| Auth | GitHub OAuth 2.0 |
| Design | Cafe Design System (#5D4432, #F9F7F5) |

## Быстрый старт

```bash
# 1. Клонировать репозиторий
git clone <repo-url> && cd python-course-platform

# 2. Настроить переменные окружения
cp .env.example .env
# Отредактировать .env: GitHub OAuth credentials, Claude API key

# 3. Запустить через Docker Compose
docker compose up -d

# 4. Открыть в браузере
open http://localhost:5173
```

## Локальная разработка без Docker

### Backend

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Запустить PostgreSQL и Redis локально, затем:
python -m app.seed          # Заполнить БД лекциями
uvicorn app.main:app --reload --port 8000

# В отдельном терминале — Celery worker:
celery -A app.celery_worker.celery_app worker --loglevel=info --pool=solo
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# Открыть http://localhost:5173
```

## Структура проекта

```
├── backend/
│   ├── app/
│   │   ├── models/          # SQLAlchemy модели
│   │   ├── routers/         # API endpoints
│   │   ├── schemas/         # Pydantic схемы
│   │   ├── services/        # Бизнес-логика
│   │   ├── main.py          # FastAPI app
│   │   ├── seed.py          # Сид лекций
│   │   └── celery_worker.py # Celery задачи
│   ├── alembic/             # Миграции
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/      # UI компоненты (shadcn/ui)
│   │   ├── pages/           # Страницы
│   │   ├── hooks/           # React хуки
│   │   └── services/        # API клиент
│   ├── tailwind.config.js   # Cafe дизайн-токены
│   └── Dockerfile
├── docker-compose.yml
└── .env.example
```

## API Endpoints (MVP)

| Метод | Путь | Описание |
|---|---|---|
| POST | /api/auth/github/login | Вход через GitHub OAuth |
| GET | /api/auth/me | Текущий пользователь |
| GET | /api/lectures | Список лекций |
| GET | /api/lectures/blocks | Лекции по блокам |
| GET | /api/lectures/number/{n} | Лекция по номеру |
| GET | /api/assignments | ДЗ студента |
| GET | /api/assignments/{id} | Детально ДЗ + ревью |
| POST | /api/assignments/{id}/review | Запуск AI-ревью |
| POST | /api/webhooks/github | Webhook от GitHub |
| GET | /api/dashboard/student | Дашборд студента |

## Этапы разработки

- [x] **MVP** — Авторизация, лекции, GitHub webhook, AI-ревью, дашборд студента
- [ ] **Аналитика** — Шкала 0-3, срезы, график динамики, дашборд преподавателя
- [ ] **Полный функционал** — Редактор лекций, экспорт данных, финальное задание, уведомления
