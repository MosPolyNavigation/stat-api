# 🧭 Polytech Navigation (PolyNa)

Проект для сбора и управления аналитикой, а также хранения и раздачи статических ресурсов сервиса **Polytech Navigation (PolyNa)**.

## Содержание
- [Требования](#требования)
- [Запуск проекта (Production / Docker)](#запуск-проекта-production--docker)
- [Локальная разработка (Development)](#локальная-разработка-development)
- [Правила работы с ветками](#правила-работы-с-ветками)
- [Проверка кода и тесты](#проверка-кода-и-тесты)

---

## Требования

Для работы с проектом вам понадобятся:
- [Docker](https://www.docker.com/) и [Docker Compose](https://docs.docker.com/compose/)
- [uv](https://github.com/astral-sh/uv)
- [Git](https://git-scm.com/)

---

## Запуск проекта (Production / Docker)

Для развертывания сервиса используется Docker Compose.

### 1. Подготовка конфигурации
Скопируйте файл конфигурации по умолчанию и отредактируйте его под ваши нужды (особенно секреты и пароли)

<details>
<summary><b>Нажмите, чтобы увидеть пример config.example.yaml</b></summary>

```yaml
server:
  host: {{ env("STATAPI_HOST", "0.0.0.0") }}
  port: {{ env("STATAPI_PORT", "8080") }}

  docs:
    openapi: false
    docs: false
    redoc: false

  cors:
    allowed_hosts:
      - "http://localhost:3000"
    allowed_methods:
      - GET
      - POST
      - PUT
    allowed_headers:
      - Authorization
    allow_credentials: false

  static:
    base_path: {{ env("STATAPI_STATIC", "./static") }}
    files: [] 

  compression:
    enable: true
    minimum_size: 1024

database:
  uri: {{ env("STATAPI_DB", "sqlite+aiosqlite:///app.db") }}
  auto_seed: false

jwt:
  access:
    secret: {{ env("STATAPI_ACCESS_SECRET", "example1") }}
    expiration: 900  # 15 минут
  refresh:
    secret: {{ env("STATAPI_REFRESH_SECRET", "example2") }}
    expiration: 2592000  # 30 дней
    cookie_name: refresh_token

jobs:
  queue: sqlite
  url: queue.db
  list:
    - name: fetch_location_data
      enabled: true
      desc: "Fetch location data every hour"
      trigger: interval
      interval:
        hours: 1
      scheduler:
        id: "hourly_location_fetch"
        replace_existing: true
        max_instances: 1
        misfire_grace_time: 300
        coalesce: true
    - name: fetch_cur_rasp
      enabled: true
      desc: "Fetch current schedule at midnight"
      trigger: cron
      cron:
        hour: 0
        minute: 0
        timezone: Europe/Moscow
      scheduler:
        id: "daily_rasp_fetch"
        replace_existing: true
        max_instances: 1
```
</details>

### 2. Настройка Docker Compose
Создайте или обновите файл `docker-compose.yml`. 

> **ВАЖНО:** Перед запуском в production обязательно замените значения паролей и секретов (`test`, `secret`) на надежные, уникальные строки!

```yaml
services:
  server:
    environment:
      STATAPI_DB: postgresql+asyncpg://statapi:test@172.16.0.11:5432/statapi # ПОМЕНЯТЬ НА БОЛЕЕ УСТОЙЧИВЫЕ ПАРОЛИ
      STATAPI_STATIC: /app/static/
      STATAPI_CONFIG: /app/config.yaml
      STATAPI_ACCESS_SECRET: secret # ЗАМЕНИТЬ НА РЕАЛЬНЫЙ СЕКРЕТ
      STATAPI_REFRESH_SECRET: secret # ЗАМЕНИТЬ НА РЕАЛЬНЫЙ СЕКРЕТ
    build: .
    ports:
      - "8080:8080"
    volumes:
      - app:/app/static
      - ./config.yaml:/app/config.yaml
    networks:
      front-tier:
        ipv4_address: 172.16.0.10
    depends_on:
      - database

  database:
    image: postgres:13.3
    environment:
      POSTGRES_DB: "statapi"
      POSTGRES_USER: "statapi"
      POSTGRES_PASSWORD: "test" # ПОМЕНЯТЬ НА БОЛЕЕ УСТОЙЧИВЫЕ ПАРОЛИ
    ports:
      - "5432:5432"
    volumes:
      - db-data:/var/lib/postgresql/data
    networks:
      front-tier:
        ipv4_address: 172.16.0.11

volumes:
  app:
  db-data:

networks:
  front-tier:
    ipam:
      driver: default
      config:
        - subnet: "172.16.0.0/24"
```

### 3. Порядок запуска в Docker
Из-за зависимости от инициализированной базы данных, запуск выполняется в два этапа:

1. Запустите только базу данных и дождитесь ее готовности:
   ```bash
   docker-compose up -d database
   ```
2. Зайдите в интерактивную оболочку контейнера `server`, чтобы применить миграции и сиды:
   ```bash
   docker-compose exec server sh
   # Внутри контейнера выполните:
   stat-api db migrate upgrade head
   stat-api db seed run
   # Выйдите из контейнера (exit)
   ```
3. Запустите основной сервис:
   ```bash
   docker-compose up -d server
   ```

---

## Локальная разработка (Development)

### 1. Установка окружения
1. Склонируйте репозиторий и переключитесь на ветку `dev`:
   ```bash
   git clone -b dev <ссылка_на_репозиторий>
   cd <папка_проекта>
   ```
2. Установите зависимости:
   ```bash
   uv sync
   uv sync --group lint
   ```
3. Настройте pre-commit хуки:
   ```bash
   uv run pre-commit
   uv run pre-commit install --hook-type pre-push --hook-type pre-commit
   ```

### 2. Работа с базой данных и запуск
Для управления базой данных используется встроенный CLI. К любой команде можно добавить `--help`, чтобы узнать доступные аргументы и подкоманды (например: `uv run stat-api db --help`).

Выберите подходящий сценарий:

#### Сценарий А: Чистый запуск (Dev, базы данных нет)
1. Примените миграции:
   ```bash
   uv run stat-api db migrate upgrade head
   ```
2. Заполните БД базовыми данными (сиды):
   ```bash
   uv run stat-api db seed run
   ```
3. *(Опционально)* Загрузите данные навигации из CSV. Для этого в корне проекта должна существовать папка `nav_data` с 4 файлами: `auds.csv`, `corpuses.csv`, `locations.csv`, `plans.csv`:
   ```bash
   uv run stat-api db seed nav-csv
   ```
4. Создайте администратора (эта же команда сбросит пароль существующего админа):
   ```bash
   uv run stat-api db create-admin <логин>
   ```
5. Запустите сервер:
   ```bash
   uv run stat-api serve
   ```

#### Сценарий Б: Обновление существующей БД
Если база данных уже существует, перед запуском нового кода обязательно:
1. Примените новые миграции: `uv run stat-api db migrate upgrade head`
2. Выполните сидинг, если в релизе появились новые сиды: `uv run stat-api db seed run`
3. Запустите сервер: `uv run stat-api serve`

#### Сценарий В: Миграция с SQLite на PostgreSQL
1. Укажите корректный URI подключения к PostgreSQL в `config.yaml` (переменная `STATAPI_DB`).
2. Инициализируйте схему в новой PostgreSQL БД:
   ```bash
   uv run stat-api db migrate upgrade head
   ```
3. Перенесите данные из старого SQLite файла:
   ```bash
   uv run stat-api db migrate sqlite-to-pg <путь_к_файлу_sqlite.db>
   ```

---

## Правила работы с ветками

Вся разработка ведется в ветках, базирующихся на `dev`. 

**Создание новой ветки:**
```bash
git checkout dev
git pull origin dev
git checkout -b <название_ветки>
```

**Правила именования веток:**
Название ветки должно четко описывать суть выполняемой работы или содержать номер назначенной задачи.
*Примеры:*
- `dev-192`
- `dev-fix-dependencies`
- `dev-add-analytics-endpoint`

---

## Проверка кода и тесты

Перед оформлением коммита и пушем в репозиторий **обязательно** убедитесь, что все проверки проходят успешно.

Выполните следующие команды:
```bash
# Проверка кода линтером
uv run ruff check .

# Проверка форматирования кода
uv run ruff format --check .

# Запуск тестов
uv run pytest
```

> **Примечание:** благодаря настроенным `pre-commit` и `pre-push` хукам, часть этих проверок будет запускаться автоматически, но рекомендуется проверять статус вручную перед финальным пушем.
