# API Notes

Базовый префикс: `/api`

Формат данных: `application/json` (кроме загрузки изображения).

## 1) Products

### GET `/api/products/`

Список товаров.

Query-параметры:

- `category` (string, optional)
- `min_price` (decimal > 0, optional)
- `max_price` (decimal > 0, optional)
- `search` (string, optional)
- `sort_by` (`name` | `price`, default `name`)
- `sort_order` (`asc` | `desc`, default `asc`)
- `limit` (int 1..100, default 20)
- `offset` (int >= 0, default 0)

Ответ `200`:

```json
{
  "count": 150,
  "next": "http://localhost:8000/api/products/?limit=20&offset=20",
  "previous": null,
  "results": [
    {
      "id": "f09f2d95-a63b-4f40-b43e-2f9d696f9f6d",
      "name": "Товар 1",
      "description": "Описание",
      "price": 1000,
      "image": "http://localhost:8000/media/products/file.png",
      "category": "Электроника"
    }
  ]
}
```

Ошибки:

- `400` если `min_price > max_price`
- `422` ошибка валидации query-параметров

### GET `/api/products/{product_id}/`

Детальная информация о товаре.

Ответы:

- `200` товар найден
- `404` товар не найден

### POST `/api/products/`

Создание товара. Требует `Authorization: Bearer <token>`.

Body:

```json
{
  "name": "iPhone 16",
  "description": "Смартфон",
  "price": 1200.00,
  "image": null,
  "category": "Электроника"
}
```

Ответы:

- `201` создано
- `401` нет токена / токен невалиден
- `403` пользователь отключен
- `422` ошибка валидации

### POST `/api/products/{product_id}/image/`

Загрузка изображения товара (`multipart/form-data`, поле `file`).
Требует `Authorization: Bearer <token>`.

Ответы:

- `200` изображение обновлено
- `400` неподдерживаемый тип файла / слишком большой файл
- `401`/`403` проблемы авторизации
- `404` товар не найден

## 2) Cart

Для корзины нужен:

- либо `Authorization: Bearer <token>`,
- либо `X-Session-ID: <value>`.

### POST `/api/cart/`

Добавить товар в корзину.

Body:

```json
{
  "product_id": "f09f2d95-a63b-4f40-b43e-2f9d696f9f6d",
  "quantity": 2
}
```

Ответы:

- `201` корзина после добавления
- `400` не передан `Authorization` и не передан `X-Session-ID`
- `404` товар не найден
- `422` ошибка валидации

### GET `/api/cart/`

Получить корзину и `total_price`.

Ответы:

- `200` корзина
- `400` не передан `Authorization` и не передан `X-Session-ID`
- `404` корзина не найдена

### PUT `/api/cart/{item_id}/`

Изменить количество позиции.

Body:

```json
{
  "quantity": 5
}
```

Ответы:

- `200` обновленная корзина
- `404` позиция корзины не найдена
- `422` ошибка валидации

### DELETE `/api/cart/{item_id}/`

Удалить позицию из корзины.

Ответы:

- `204` удалено
- `404` позиция не найдена

## 3) Auth (опционально)

### POST `/api/auth/register`

Регистрация пользователя.

Body:

```json
{
  "email": "user@example.com",
  "password": "secret123"
}
```

Ответы:

- `201` создан пользователь
- `400` email уже занят

### POST `/api/auth/login`

Логин пользователя.

Если в запросе передан `X-Session-ID`, гостевая корзина сливается в пользовательскую.

Body:

```json
{
  "email": "user@example.com",
  "password": "secret123"
}
```

Ответы:

- `200` токен
- `401` неверные данные
- `403` аккаунт отключен

### GET `/api/auth/me`

Информация о текущем пользователе.

Требует `Authorization: Bearer <token>`.

## 4) Служебные

### GET `/health`

Проверка работоспособности сервиса.

Ответ:

```json
{
  "status": "ok"
}
```
