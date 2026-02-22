# Test Coverage Report

**Дата:** 22 февраля 2026
**Общее покрытие:** 74% (4708 строк, 1222 непокрытых)
**Всего тестов:** 191 (все прошли успешно)

## Executive Summary

Проведен анализ test coverage для проекта stat-api. Текущее покрытие составляет 74%, что является хорошим показателем, но есть значительные области кода, требующие дополнительного тестирования.

## 1. Модули с нулевым покрытием (0%)

Следующие модули полностью не протестированы:

### Критические модули

1. **app/app.py** (52 строки, 0% coverage)
   - Основной файл приложения
   - Линии: 1-155
   - Содержит инициализацию FastAPI приложения

2. **app/handlers/update.py** (7 строк, 0% coverage)
   - Обработчики обновления данных
   - Линии: 1-29

3. **app/helpers/spa_static_files.py** (18 строк, 0% coverage)
   - Обработка статических файлов SPA
   - Линии: 1-20

### Jobs (планировщики задач)

4. **app/jobs/__init__.py** (14 строк, 0%)
5. **app/jobs/rasp/__init__.py** (18 строк, 0%)
6. **app/jobs/rasp/canonize.py** (54 строки, 0%)
7. **app/jobs/rasp/get_schedule.py** (51 строка, 0%)
8. **app/jobs/rasp/parse.py** (72 строки, 0%)
9. **app/jobs/schedule/get_graph.py** (27 строк, 0%)
10. **app/jobs/schedule/schedule.py** (14 строк, 0%)

### Routes (новые эндпоинты)

11. **app/routes/nav/campus.py** (45 строк, 0%)
    - Эндпоинт получения информации о кампусе
12. **app/routes/nav/campuses.py** (14 строк, 0%)
    - Эндпоинт списка кампусов
13. **app/routes/nav/plan.py** (30 строк, 0%)
    - Эндпоинт получения плана
14. **app/routes/jobs/schedule.py** (14 строк, 0%)

### Schemas

15. **app/schemas/rasp/dto.py** (32 строки, 0%)
16. **app/models/floor_map.py** (11 строк, 0%)

## 2. Модули с низким покрытием (<50%)

### Критические для тестирования

1. **app/handlers/insert.py** - 27% coverage
   - 55 строк, 40 непокрытых
   - Непокрытые линии: 27-32, 56-67, 95-109, 134-144, 171-183, 203-229
   - **Критичность:** ВЫСОКАЯ (обработка вставки данных)

2. **app/handlers/review.py** - 42% coverage
   - 12 строк, 7 непокрытых
   - Непокрытые линии: 14-27

3. **app/helpers/path.py** - 30% coverage
   - 27 строк, 19 непокрытых
   - Непокрытые линии: 16-24, 32-48, 54-68

4. **app/routes/graphql/tg_bot.py** - 31% coverage
   - 136 строк, 94 непокрыты
   - Непокрытые линии: 45-47, 54-56, 63, 79-89, 97-107, 117-144, 154-170, 177-180, 191-258
   - **Критичность:** ВЫСОКАЯ (новый функционал)

5. **app/routes/crud_roles/update.py** - 40% coverage
   - 57 строк, 34 непокрыты
   - Непокрытые линии: 45-134

6. **app/routes/crud_users/update.py** - 48% coverage
   - 29 строк, 15 непокрытых
   - Непокрытые линии: 30-64

7. **app/routes/review/add.py** - 48% coverage
   - 27 строк, 14 непокрытых
   - Непокрытые линии: 80-94

## 3. Модули со средним покрытием (50-75%)

1. **app/handlers/get.py** - 56% coverage
   - Непокрытые линии: 42, 109, 113-119, 123-140

2. **app/helpers/permissions.py** - 52% coverage
   - Непокрытые линии: 25-50

3. **app/routes/graphql/review_status.py** - 50% coverage
   - Непокрытые линии: 18-20, 28-38

4. **app/routes/crud_roles/create.py** - 54% coverage
   - Непокрытые линии: 24-36, 65-95

5. **app/routes/crud_roles/assign.py** - 56% coverage
   - Непокрытые линии: 36-62

6. **app/routes/review/status.py** - 55% coverage
   - Непокрытые линии: 34-57

7. **app/routes/graphql/endpoint_stats.py** - 70% coverage
   - Непокрытые линии: 32-50, 63, 73

8. **app/helpers/svobodn.py** - 70% coverage
   - Непокрытые линии: 18-26, 35

9. **app/schemas/graph/graph.py** - 76% coverage
   - Непокрытые линии: 35, 55, 89-94, 97-112, 115-123, 129, 138-139, 142-144, 185, 218

10. **app/schemas/rasp/schedule.py** - 66% coverage
    - Непокрытые линии: 29-51, 54-55

## 4. GraphQL Navigation (59-61% coverage)

Все новые GraphQL навигационные эндпоинты имеют среднее покрытие ~60%:

1. **app/routes/graphql/nav/auditory.py** - 59%
2. **app/routes/graphql/nav/campus.py** - 60%
3. **app/routes/graphql/nav/floor.py** - 59%
4. **app/routes/graphql/nav/location.py** - 60%
5. **app/routes/graphql/nav/nav_type.py** - 59%
6. **app/routes/graphql/nav/plan.py** - 61%
7. **app/routes/graphql/nav/static.py** - 59%

## 5. Приоритизация тестирования

### Приоритет 1 (Критический) - Рекомендуется для issue #217

1. **app/routes/graphql/tg_bot.py** (31% → цель 80%+)
   - Новый функционал для Telegram бота
   - 94 непокрытые строки
   - Необходимы integration и unit тесты для всех GraphQL запросов/мутаций

2. **app/handlers/insert.py** (27% → цель 80%+)
   - Критический функционал вставки данных
   - 40 непокрытых строк
   - Высокий риск ошибок при некорректной вставке

3. **app/routes/nav/campus.py** (0% → цель 80%+)
   - Новый REST эндпоинт
   - 45 непокрытых строк
   - Полностью непротестирован

4. **app/routes/nav/plan.py** (0% → цель 80%+)
   - Новый REST эндпоинт для планов
   - 30 непокрытых строк
   - Полностью непротестирован

### Приоритет 2 (Высокий)

5. **app/routes/crud_roles/update.py** (40% → цель 80%+)
   - Обновление ролей пользователей
   - 34 непокрытые строки

6. **app/helpers/path.py** (30% → цель 70%+)
   - Утилиты работы с путями
   - 19 непокрытых строк

7. **app/routes/review/add.py** (48% → цель 80%+)
   - Добавление отзывов
   - 14 непокрытых строк

8. **app/routes/graphql/review_status.py** (50% → цель 80%+)
   - GraphQL запросы статусов отзывов
   - 14 непокрытых строк

### Приоритет 3 (Средний)

9. **GraphQL Navigation endpoints** (59-61% → цель 80%+)
   - Все 7 эндпоинтов навигации
   - Необходимо добавить edge cases и error handling тесты

10. **app/jobs/rasp/*** (0% → цель 60%+)
    - Фоновые задачи расписания
    - Нужны integration тесты для планировщика

## 6. Рекомендуемая стратегия тестирования для issue #217

Исходя из требований issue #217 (добавить тесты для ~4 эндпоинтов), рекомендую следующие приоритеты:

### Вариант 1: Фокус на новых эндпоинтах

1. **app/routes/graphql/tg_bot.py** - Integration и unit тесты
2. **app/routes/nav/campus.py** - REST API тесты
3. **app/routes/nav/plan.py** - REST API тесты
4. **app/routes/graphql/review_status.py** - GraphQL тесты

### Вариант 2: Фокус на критичных handler'ах

1. **app/handlers/insert.py** - Unit тесты для всех методов вставки
2. **app/routes/graphql/tg_bot.py** - Integration тесты
3. **app/routes/crud_roles/update.py** - Unit и integration тесты
4. **app/routes/review/add.py** - Integration тесты

## 7. Дополнительные замечания

### Сильные стороны

- Отличное покрытие моделей (90%+)
- Хорошее покрытие существующих тестов (100% для test файлов)
- Отличное покрытие базовых routes (auth, roles, users - 70-90%)

### Области для улучшения

- Jobs/планировщики полностью не протестированы
- Новые навигационные эндпоинты требуют дополнительных тестов
- Telegram bot функционал нуждается в тестах
- Handler'ы обновления и вставки требуют больше тестов

## 8. Метрики

- **Всего модулей:** 159
- **Модулей с 100% coverage:** 47 (29.5%)
- **Модулей с 0% coverage:** 16 (10%)
- **Модулей с покрытием 50-80%:** 31 (19.5%)
- **Модулей с покрытием 80%+:** 86 (54%)

---

**Заключение:** Для достижения целевого покрытия 85%+ необходимо сосредоточиться на тестировании новых эндпоинтов (nav, tg_bot) и критичных handler'ов (insert, update). Рекомендуется начать с 4 приоритетных модулей из списка выше.
