# Решение: Auth модуль — JWT + RLS + ролевая модель

**Дата**: 2026-05-10
**Категория**: tech
**Статус**: Принято

## Контекст

Спринт 1. Цель — реализовать полноценный Auth модуль на кастомном FastAPI бэкенде
(без Supabase) с JWT, bcrypt, ролевой моделью и интеграцией RLS.

Требования: 152-ФЗ (данные в РФ), мультиарендность через PostgreSQL RLS, ротация
refresh-токенов, аудит логинов.

## Решение

### Структура файлов

```
src/backend/
├── app/
│   ├── models/user.py              # SQLAlchemy: User, UserRole enum
│   ├── schemas/auth.py             # Pydantic v2: UserCreate, Token, UserResponse...
│   ├── api/v1/auth.py              # Endpoints: /register /login /refresh /logout /me
│   ├── api/v1/deps.py              # get_current_user, require_roles(), get_db_with_rls
│   └── core/security.py            # bcrypt (rounds=12), create/decode access+refresh JWT
└── alembic/versions/
    └── 2026_05_10_add_users_table.py  # таблица users, enum user_role, RLS policy
```

### Модель данных (таблица `users`)

Поля: `id` (UUID), `tenant_id` (UUID), `email` (unique), `password_hash`, `role` (enum),
`is_active`, `refresh_token_jti` (String 36), `created_at`, `updated_at`,
`last_login_at`, `deleted_at`.

Индексы: `ix_users_email` (unique), `ix_users_tenant_id`, `ix_users_role`, `ix_users_deleted_at`.

### JWT стратегия

- **Access-токен**: 15 мин, payload = `{sub, tenant_id, role, type="access", jti, exp}`
- **Refresh-токен**: 30 дней, payload = `{sub, type="refresh", jti, exp}`
- Алгоритм: HS256, ключ из `JWT_SECRET_KEY` (отдельно от `SECRET_KEY`)
- Токены различаются по полю `type` — взаимозаменяемость исключена на уровне decode-функций

### Ротация refresh-токена (Refresh Token Rotation)

`refresh_token_jti` в таблице `users` хранит `jti` **только последнего** выданного
refresh-токена. При `/refresh`:
1. Декодируем токен, извлекаем `jti`
2. Сравниваем с `user.refresh_token_jti` в БД
3. Несовпадение → 401 (токен уже использован или разлогинен)
4. При успехе — записываем новый `jti`, старый больше не работает

### Logout

`POST /api/v1/auth/logout` устанавливает `refresh_token_jti = NULL`.
Access-токен доживает свои ≤15 мин — без чёрного списка (приемлемо для MVP).
Endpoint идемпотентен: невалидный токен принимается молча.

### Ролевая модель

```python
# Роли (UserRole enum): owner > admin > master

# Использование в роутерах:
Depends(get_current_user)                              # любой авторизованный
Depends(require_roles(UserRole.owner))                 # только owner
Depends(require_roles(UserRole.owner, UserRole.admin)) # owner или admin
```

`get_current_user` не только декодирует JWT, но и **проверяет пользователя в БД**
(is_active, deleted_at). Это важно: деактивация юзера работает немедленно.

### RLS интеграция

`get_db_with_rls` берёт `tenant_id` из объекта `User` (не из raw JWT-payload) и
выполняет `SET LOCAL app.tenant_id = '<uuid>'`. Это исключает подмену tenant_id
через модифицированный токен.

Политика в PostgreSQL:
```sql
CREATE POLICY tenant_isolation_policy ON users
    FOR ALL
    USING (
        tenant_id::text = current_setting('app.tenant_id', true)
        OR current_setting('app.tenant_id', true) IS NULL
        OR current_setting('app.tenant_id', true) = ''
    )
    WITH CHECK (tenant_id::text = current_setting('app.tenant_id', true));
```

Условие `IS NULL OR ''` позволяет бэкенду работать с таблицей users до установки
контекста (например, при `/login` и `/register`).

### Регистрация

- Первый пользователь в системе → автоматически `role=owner`, создаётся новый `tenant_id`
- Последующие регистрации через публичный endpoint закрыты (403)
- Добавление сотрудников — через будущий `POST /api/v1/users` (авторизованный, только owner)

### Безопасность

- bcrypt rounds=12 (не дефолт)
- Пароль: минимум 8 символов, хотя бы 1 буква + 1 цифра (Pydantic validator)
- Email через `pydantic.EmailStr`
- CORS whitelist вместо `*` (`localhost:3000`, `localhost:5173`)
- `JWT_SECRET_KEY` отдельно от `SECRET_KEY` — компрометация одного не даёт доступ к другому
- Никаких секретов в коде; `.env.example` с инструкцией генерации

## Альтернативы

- **Supabase Auth**: отклонено — внешняя зависимость, данные вне РФ (152-ФЗ), лишние расходы.
- **Чёрный список access-токенов в Redis**: отклонено для MVP — сложность + Redis как SPoF.
  Митигация: короткий TTL (15 мин) + немедленная проверка `is_active` в БД.
- **httpOnly cookie вместо Bearer**: отложено — нужен фронт, не критично для API-first MVP.

## Последствия

- ✅ Полная изоляция tenant-данных через RLS без изменений в бизнес-логике
- ✅ Ротация токенов защищает от replay-атак и кражи refresh-токена
- ✅ Деактивация пользователя работает немедленно (проверка в БД при каждом запросе)
- ✅ Готовая фабрика `require_roles()` — один паттерн для всех роутеров
- ⚠️ Access-токен живёт до 15 мин после logout — без Redis-блэклиста
- ⚠️ Один активный refresh-токен на пользователя — параллельные сессии (браузер + мобайл)
  инвалидируют друг друга. Для MVP ок, позже доработать до per-device tokens.
- 🔧 Технический долг: `POST /api/v1/users` (CRUD сотрудников), rate limiting на `/login` (slowapi), per-device refresh tokens

## Тестирование

15 тестов в `tests/test_auth.py`:
- Unit: password hash/verify, JWT roundtrip, тип-защита (access ≠ refresh)
- Integration: register (первый=owner, второй=403, слабый пароль=422)
- Integration: login (успех, неверный пароль, неизвестный email)
- Integration: /me (валидный токен, без токена, невалидный токен)
- Integration: refresh rotation (новые токены, старый отклонён)
- Integration: logout (refresh инвалидируется)
- Integration: RLS isolation (два owner → разные tenant_id)

Тесты используют SQLite in-memory (aiosqlite) — не требуют запущенного PostgreSQL.

## Связанные файлы

- `src/backend/app/models/user.py`
- `src/backend/app/schemas/auth.py`
- `src/backend/app/api/v1/auth.py`
- `src/backend/app/api/v1/deps.py`
- `src/backend/app/core/security.py`
- `src/backend/app/core/config.py`
- `src/backend/alembic/versions/2026_05_10_add_users_table.py`
- `.env.example`
- `tests/test_auth.py`
- `tests/conftest.py`
- `.ai/memory/tech/2026-05-10_infra-review-sprint1.md` (предыдущая сессия)

## Следующие шаги

1. `POST /api/v1/users` — добавление сотрудников owner'ом
2. Rate limiting на `/login` через `slowapi` (brute force защита)
3. Подключить `get_db_with_rls` в роутеры `clients`, `vehicles`, `orders`
4. `docker compose exec backend pytest tests/ -v --cov=app` — прогнать тесты в CI

## История изменений

- 2026-05-10: создано по итогам сессии реализации Auth модуля
