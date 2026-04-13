# Event Manager

Система управления мероприятиями с поддержкой геопространственных данных и прогноза погоды.

## 📋 Описание

Проект представляет собой платформу для управления событиями, включающую:
- Создание и публикацию мероприятий
- Управление местами проведения с геолокацией (поддержка карты не реализована)
- Интеграцию с погодными сервисами
- Автоматическую публикацию запланированных событий
- Обновление погодной информации в реальном времени

## 🏗️ Архитектура

Проект использует клиент-серверную архитектуру:

```
┌─────────────────┐         ┌─────────────────────────┐
│   Frontend      │         │   Backend               │
│   (Vue 3)       │◄───────►│   (Django + DRF)        │
│   Vite          │   API   │   Celery + Redis        │
└─────────────────┘         └─────────────────────────┘
                                    │
                                    ▼
                          ┌─────────────────────┐
                          │   PostgreSQL +      │
                          │   PostGIS           │
                          └─────────────────────┘
```

## 🛠️ Технологический стек

### Frontend (Небольшой интерфейс для API)
- **Vue 3** — реактивный фреймворк
- **Vue Router** — маршрутизация
- **Axios** — HTTP-клиент
- **Vite** — сборщик проекта

### Backend
- **Django** — веб-фреймворк
- **Django REST Framework** — создание API
- **Celery** — асинхронные задачи
- **Redis** — брокер сообщений
- **PostgreSQL + PostGIS** — база данных с поддержкой геоданных
- **django-filter** — фильтрация запросов
- **drf-spectacular** — генерация OpenAPI документации

## 🚀 Быстрый старт

### Предварительные требования

- Docker и Docker Compose
- Git

### Запуск проекта

1. **Клонируйте репозиторий**
   ```bash
   git clone <repository-url>
   cd <project-folder>
   ```

2. **Настройте переменные окружения**
   ```bash
   # Backend
   cp backend/env_sample backend/.env
   cp backend/celery.env_sample backend/celery.env
   cp backend/postgres.env_sample backend/postgres.env
   
   # Frontend
   cp frontend/.env.example frontend/.env
   ```

3. **Запустите проект**
   ```bash
   docker-compose up --build
   ```
   
4. **Создайте суперпользователя**
   ```bash
   docker-compose exec backend python manage.py createsuperuser
   ```

5. **Добавьте демо-данные** (опционально)
   ```bash
   docker-compose exec backend python manage.py generate_demo_data
   ```

## 📁 Структура проекта

```
.
├── backend/                 # Django backend
│   ├── core/               # Основные настройки проекта
│   │   ├── settings.py     # Конфигурация Django
│   │   ├── celery.py       # Настройка Celery
│   │   └── urls.py         # Главные маршруты
│   ├── event_manager/      # Основное приложение
│   │   ├── api/            # API endpoints
│   │   ├── models/         # Модели данных
│   │   ├── serializers/    # Сериализаторы
│   │   ├── services/       # Бизнес-логика
│   │   ├── tasks.py        # Celery задачи
│   │   └── tests/          # Тесты
│   └── manage.py           # Django CLI
│
├── frontend/               # Vue 3 frontend
│   ├── src/
│   │   ├── api.js         # API клиент
│   │   ├── auth.js        # Аутентификация
│   │   ├── router/        # Роутер
│   │   ├── views/         # Страницы
│   │   └── App.vue        # Корневой компонент
│   └── package.json
│
└── docker-compose.yml      # Docker конфигурация
```

## 🔑 Основные возможности

### Модели данных

- **Event** — мероприятие (название, описание, даты, локация, рейтинг, статус)
- **Place** — место проведения (название, адрес, геокоординаты)
- **Weather** — погодные данные для мест проведения (генерируются рандомно в помощью celery задаче)

### API Endpoints

#### Аутентификация
- `POST /api/auth/login/` — вход
- Логаут на уровне клиента

#### Мероприятия
- `GET /api/events/` — список мероприятий
- `POST /api/events/` — создать мероприятие
- `GET /api/events/{id}/` — детали мероприятия
- `PUT /api/events/{id}/` — обновить мероприятие
- `DELETE /api/events/{id}/` — удалить мероприятие

#### Места
- `GET /api/places/` — список мест
- `POST /api/places/` — создать место
- `GET /api/places/{id}/` — детали места
- `PUT /api/places/{id}/` — обновить место
- `DELETE /api/places/{id}/` — удалить место

### Автоматизация (Celery)

- **publish-scheduled-events** — проверка и публикация запланированных событий (каждую минуту)
- **send_event_published_email** — отправка письма с запланированным мероприятием всем пользователям (вызывается в **publish-scheduled-events**)
- **refresh-weather** — обновление погодных данных (каждые 15 минут)

## 📝 Документация API

API документация доступна по адресу:
- Swagger UI: `http://localhost:8000/api/schema/swagger-ui/`
- ReDoc: `http://localhost:8000/api/schema/redoc/`
- OpenAPI JSON: `http://localhost:8000/api/schema/`

### Тестирование

```bash
# Backend тесты
docker-compose exec backend python manage.py test
