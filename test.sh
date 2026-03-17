
#
# test_governors.sh
# Скрипт для тестирования rate limit governor'ов
#
# Использование:
#   ./test_governors.sh <BASE_URL>
#
# Пример:
#   ./test_governors.sh http://localhost:8000
#

set -euo pipefail

# === Конфигурация ===
BASE_URL="${1:-http://localhost:8080}"

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# === Вспомогательные функции ===
log_info()    { echo -e "${BLUE}[INFO]${NC} $*"; }
log_success() { echo -e "${GREEN}[OK]${NC} $*"; }
log_warn()    { echo -e "${YELLOW}[WARN]${NC} $*"; }
log_error()   { echo -e "${RED}[ERROR]${NC} $*"; }
log_step()    { echo -e "${CYAN}[STEP]${NC} $*"; }

# Получение user_id через API
get_user_id() {
    local response
    response=$(curl -s -X GET "${BASE_URL}/api/get/user-id")
    
    if echo "$response" | grep -q '"user_id"'; then
        echo "$response" | grep -o '"user_id"[[:space:]]*:[[:space:]]*"[^"]*"' | cut -d'"' -f4
    else
        log_error "Не удалось получить user_id: $response"
        return 1
    fi
}

# Выполняет запрос и выводит статус
# Usage: do_request <METHOD> <ENDPOINT> <DATA> [EXPECTED_STATUS] [CONTENT_TYPE]
do_request() {
    local method="$1"
    local endpoint="$2"
    local data="$3"
    local expected="${4:-}"
    local content_type="${5:-application/json}"
    
    local response
    local http_code
    
    if [[ "$method" == "PUT" ]]; then
        response=$(curl -s -w "\n%{http_code}" -X PUT \
            -H "Content-Type: ${content_type}" \
            -d "$data" \
            "${BASE_URL}${endpoint}")
    elif [[ "$method" == "POST" ]]; then
        response=$(curl -s -w "\n%{http_code}" -X POST \
            -H "Content-Type: ${content_type}" \
            -d "$data" \
            "${BASE_URL}${endpoint}")
    else
        response=$(curl -s -w "\n%{http_code}" -X GET "${BASE_URL}${endpoint}")
    fi
    
    # Разделяем тело ответа и код статуса
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    # Вывод результата
    if [[ -n "$expected" ]]; then
        if [[ "$http_code" == "$expected" ]]; then
            log_success "✓ $method $endpoint → $http_code (ожидалось $expected)"
        else
            log_error "✗ $method $endpoint → $http_code (ожидалось $expected)"
            if [[ -n "$body" && "$body" != "null" ]]; then
                echo "  Response: $body"
            fi
        fi
    else
        log_info "$method $endpoint → $http_code"
        if [[ -n "$body" && "$body" != "null" ]]; then
            echo "  Response: $body"
        fi
    fi
    
    return 0
}

# Пауза с выводом
sleep_verbose() {
    local seconds="$1"
    local msg="${2:-}"
    if [[ -n "$msg" ]]; then
        log_info "$msg (ждем ${seconds}с)..."
    fi
    sleep "$seconds"
}

# === Получение user_id ===
fetch_user_ids() {
    log_step "=== Получение user_id через API ==="
    
    log_info "Запрашиваем user_id для тестов /api/stat/*..."
    USER_ID_STAT=$(get_user_id)
    if [[ -z "$USER_ID_STAT" ]]; then
        log_error "Не удалось получить user_id для stat тестов"
        exit 1
    fi
    log_success "✓ user_id (stat): $USER_ID_STAT"
    
    log_info "Запрашиваем user_id для тестов /api/review/*..."
    USER_ID_REVIEW=$(get_user_id)
    if [[ -z "$USER_ID_REVIEW" ]]; then
        log_error "Не удалось получить user_id для review тестов"
        exit 1
    fi
    log_success "✓ user_id (review): $USER_ID_REVIEW"
    
    echo
}

# === Тесты для /api/stat/* (RateLimiter: 1 запрос/сек на эндпоинт) ===
test_stat_rate_limiter() {
    log_step "=== Тестирование RateLimiter для /api/stat/* ==="
    log_info "Правило: не более 1 запроса в секунду на пользователя для каждого эндпоинта"
    echo
    
    local payload
    payload=$(cat <<EOF
{
    "user_id": "$USER_ID_STAT",
    "auditory_id": "a-100",
    "success": true
}
EOF
)
    
    # Тест 1: Первый запрос — должен пройти
    log_info "Тест 1: Первый запрос к /api/stat/select-aud"
    do_request "PUT" "/api/stat/select-aud" "$payload" "200"
    echo
    
    # Тест 2: Второй запрос сразу — должен получить 429
    log_info "Тест 2: Второй запрос сразу (ожидается 429)"
    do_request "PUT" "/api/stat/select-aud" "$payload" "429"
    echo
    
    # Тест 3: Запрос к ДРУГОМУ эндпоинту — должен пройти (разные ключи!)
    log_info "Тест 3: Запрос к /api/stat/site (другой эндпоинт — должен пройти)"
    local site_payload
    site_payload=$(cat <<EOF
{
    "user_id": "$USER_ID_STAT",
    "endpoint": "/some/path"
}
EOF
)
    do_request "PUT" "/api/stat/site" "$site_payload" "200"
    echo
    
    # Тест 4: Повторный запрос к site сразу — 429
    log_info "Тест 4: Повторный запрос к /api/stat/site сразу (ожидается 429)"
    do_request "PUT" "/api/stat/site" "$site_payload" "429"
    echo
    
    # Тест 5: Ждём 1.5 секунды и повторяем — должен пройти
    sleep_verbose 1.5 "Ждём окончания окна"
    log_info "Тест 5: Запрос к /api/stat/select-aud после паузы (должен пройти)"
    do_request "PUT" "/api/stat/select-aud" "$payload" "200"
    echo
    
    # Тест 6: Тест других stat эндпоинтов
    log_info "Тест 6: Запрос к /api/stat/start-way"
    local start_way_payload
    start_way_payload=$(cat <<EOF
{
    "user_id": "$USER_ID_STAT",
    "start_id": "a-100",
    "end_id": "a-101",
    "success": true
}
EOF
)
    do_request "PUT" "/api/stat/start-way" "$start_way_payload" "200"
    echo
    
    log_info "Тест 7: Запрос к /api/stat/change-plan"
    local change_plan_payload
    change_plan_payload=$(cat <<EOF
{
    "user_id": "$USER_ID_STAT",
    "plan_id": "plan-1"
}
EOF
)
    do_request "PUT" "/api/stat/change-plan" "$change_plan_payload" "200"
    echo
    
    log_success "✓ Тесты RateLimiter для /api/stat/* завершены"
    echo "=================================================="
    echo
}

# === Тесты для /api/review/add (ReviewRateLimiter) ===
test_review_rate_limiter() {
    log_step "=== Тестирование ReviewRateLimiter для /api/review/add ==="
    log_info "Правила:"
    log_info "  • Не более 5 запросов в минуту"
    log_info "  • Не более 20 запросов за 5 минут"
    log_info "  • Бан после 10 нарушений или 30 запросов за 10 секунд"
    echo
    
    # Тест 1: 5 запросов — все должны пройти
    log_info "Тест 1: Отправляем 5 запросов (лимит в минуту)"
    for i in {1..5}; do
        log_info "  Запрос #$i"
        
        # Используем multipart/form-data (-F вместо -d)
        response=$(curl -s -w "\n%{http_code}" -X POST \
            -F "user_id=$USER_ID_REVIEW" \
            -F "problem=way" \
            -F "text=Test review #$i" \
            "${BASE_URL}/api/review/add")
        
        http_code=$(echo "$response" | tail -n1)
        body=$(echo "$response" | sed '$d')
        
        if [[ "$http_code" == "200" ]]; then
            log_success "✓ Запрос #$i → $http_code"
        else
            log_error "✗ Запрос #$i → $http_code"
            echo "  Response: $body"
        fi
        
        sleep 0.1  # небольшая пауза чтобы не триггерить burst
    done
    echo
    
    # Тест 2: 6-й запрос — должен получить 429
    log_info "Тест 2: 6-й запрос в ту же минуту (ожидается 429)"
    response=$(curl -s -w "\n%{http_code}" -X POST \
        -F "user_id=$USER_ID_REVIEW" \
        -F "problem=way" \
        -F "text=Test review #6" \
        "${BASE_URL}/api/review/add")
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [[ "$http_code" == "429" ]]; then
        log_success "✓ 6-й запрос → $http_code (ожидалось 429)"
    else
        log_error "✗ 6-й запрос → $http_code (ожидалось 429)"
        echo "  Response: $body"
    fi
    echo
    
    # Тест 3: Проверка содержимого ответа 429
    log_info "Тест 3: Проверка содержимого ответа 429"
    if echo "$body" | grep -qi "too many"; then
        log_success "✓ Ответ 429 содержит ожидаемое сообщение"
    else
        log_warn "⚠ Ответ 429: $body"
    fi
    echo
    
    log_success "✓ Тесты ReviewRateLimiter (базовые) завершены"
    echo
}

# === Тест burst-атаки для бана ===
test_review_burst_ban() {
    log_warn "=== Тест burst-атаки для проверки бана ==="
    log_warn "ВНИМАНИЕ: Этот тест может ЗАБАНИТЬ пользователя"
    log_warn "Нажмите Enter для продолжения или Ctrl+C для отмены..."
    read -r
    
    # Получаем новый user_id для теста бана (чтобы не банить основной)
    log_info "Получаем новый user_id для теста бана..."
    local burst_user_id
    burst_user_id=$(get_user_id)
    log_success "✓ user_id (burst test): $burst_user_id"
    echo
    
    log_info "Отправляем 30+ запросов за 10 секунд (триггер бана)..."
    
    local banned=false
    local start_time=$(date +%s)
    
    for i in {1..35}; do
        # Используем multipart/form-data (-F вместо -d)
        local response
        response=$(curl -s -w "\n%{http_code}" -X POST \
            -F "user_id=$burst_user_id" \
            -F "problem=way" \
            -F "text=Burst test #$i" \
            "${BASE_URL}/api/review/add")
        
        local http_code=$(echo "$response" | tail -n1)
        local body=$(echo "$response" | sed '$d')
        
        if [[ "$http_code" == "403" ]]; then
            local end_time=$(date +%s)
            local duration=$((end_time - start_time))
            log_success "✓ Пользователь забанен после запроса #$i (за ${duration}с)"
            echo "  Response: $body"
            banned=true
            break
        elif [[ "$http_code" == "429" ]]; then
            log_warn "  Запрос #$i: 429 (ещё не бан)"
        elif [[ "$http_code" == "200" ]]; then
            log_info "  Запрос #$i: 200 (прошёл)"
        else
            log_error "  Запрос #$i: неожиданный код $http_code"
            echo "  Response: $body"
        fi
        
        # Минимальная пауза чтобы не быть слишком агрессивным
        sleep 0.05
    done
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    if [[ "$banned" == false ]]; then
        log_error "✗ Бан не сработал после 35 запросов (за ${duration}с)"
    else
        log_success "✓ Тест burst-атаки завершён успешно (за ${duration}с)"
    fi
    echo
}

# === Проверка доступности сервера ===
check_server_health() {
    log_step "=== Проверка доступности сервера ==="
    
    # Проверка OpenAPI
    local openapi_code
    openapi_code=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/openapi.json")
    if [[ "$openapi_code" == "200" ]]; then
        log_success "✓ OpenAPI доступен ($openapi_code)"
    else
        log_error "✗ OpenAPI недоступен ($openapi_code)"
        exit 1
    fi
    
    # Проверка получения user_id
    local user_id_test
    user_id_test=$(get_user_id)
    if [[ -n "$user_id_test" ]]; then
        log_success "✓ /api/get/user-id работает (user_id: $user_id_test)"
    else
        log_error "✗ /api/get/user-id не работает"
        exit 1
    fi
    
    echo
}

# === Вывод сводки ===
print_summary() {
    echo "=================================================="
    echo "📊 Сводка тестирования"
    echo "=================================================="
    echo "Base URL: $BASE_URL"
    echo "User ID (stat):   $USER_ID_STAT"
    echo "User ID (review): $USER_ID_REVIEW"
    echo "=================================================="
    echo
}

# === Main ===
main() {
    echo "=================================================="
    echo "🧪 Тестирование Rate Limit Governors"
    echo "=================================================="
    echo "Base URL: $BASE_URL"
    echo "=================================================="
    echo
    
    # Проверка сервера
    # check_server_health
    
    # Получение user_id
    fetch_user_ids
    
    # Вывод сводки
    print_summary
    
    # Запуск тестов
    test_stat_rate_limiter
    test_review_rate_limiter
    
    # Опционально: тест бана (раскомментируй если нужно)
    test_review_burst_ban
    
    log_success "🎉 Все тесты завершены!"
}

# Запуск
main "$@"