# Product Catalog API
ПО ЭТОМУ АДРЕСУ ДОСТУПЕН: http://212.19.134.63:8000/docs#/ поднял на ssh сервере


Небольшой backend для интерактивного каталога товаров и корзины.

Сделано на `FastAPI + SQLAlchemy + PostgreSQL`.

## Что умеет

- Список товаров с фильтрацией, сортировкой, поиском и пагинацией
- Детальная карточка товара
- Корзина (добавить, получить, изменить количество, удалить позицию)
- JWT авторизация (регистрация, логин, текущий пользователь)
- Загрузка изображения товара
- Swagger/OpenAPI документация

## Стек

- Python 3.12
- FastAPI
- SQLAlchemy (async)
- Alembic
- PostgreSQL
- Docker / docker-compose

## Быстрый запуск (Docker)

1. Поднимите сервис по докер компосее:

```bash
docker-compose up --build
```

2.API будет доступен:

- `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

При старте контейнера API автоматически применяются миграции Alembic.

## Локальный запуск (без Docker)

1. Поднимите PostgreSQL локально и проверьте `DATABASE_URL` в `.env`.
2. Установите зависимости:

```bash
pip install -r requirements.txt
```

3. Примените миграции:

```bash
alembic upgrade head
```

4. Запустите приложение:

```bash
uvicorn main:app --reload
```

## Переменные окружения

Минимально необходимые:

- `DATABASE_URL`
- `SECRET_KEY`

Остальные:

- `ALGORITHM` (по умолчанию `HS256`)
- `ACCESS_TOKEN_EXPIRE_MINUTES` (по умолчанию `30`)
- `CORS_ORIGINS` (список origin)
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` (нужны для docker-compose db сервиса)

## Аутентификация и корзина

Для корзины нужно передавать хотя бы один способ идентификации:

- `Authorization: Bearer <token>` (для авторизованного пользователя)
- или `X-Session-ID: <ваш-session-id>` (для гостя)

Если не передать ни токен, ни `X-Session-ID`, API корзины вернет `400`.

## Основные эндпоинты

Подробно: [docs/API.md](docs/API.md)

- `GET /api/products/`
- `GET /api/products/{product_id}/`
- `POST /api/products/` (нужен Bearer token)
- `POST /api/products/{product_id}/image/` (нужен Bearer token)
- `POST /api/cart/`
- `GET /api/cart/`
- `PUT /api/cart/{item_id}/`
- `DELETE /api/cart/{item_id}/`
- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`

## Короткие примеры

Получить товары:

```bash
curl "http://localhost:8000/api/products/?limit=20&offset=0&search=iphone&sort_by=price&sort_order=asc&has_image=true"
```

Добавить товар в корзину как гость:

```bash
curl -X POST "http://localhost:8000/api/cart/" \
  -H "Content-Type: application/json" \
  -H "X-Session-ID: guest-123" \
  -d '{"product_id":"11111111-1111-1111-1111-111111111111","quantity":2}'
```

## Структура проекта

```text
app/
  api/           # роутеры
  core/          # конфиг, security, зависимости
  db/            # сессия и Base
  models/        # SQLAlchemy модели
  repositories/  # запросы к БД
  schemas/       # Pydantic схемы
  services/      # бизнес-логика
  utils/         # вспомогательные функции
alembic/         # миграции
main.py          # точка входа FastAPI
```

## Примечание

Для ручной проверки API удобно использовать Swagger (`/docs`) или curl.

## Тесты

```bash
pip install -r requirements-dev.txt
pytest -q
```
