#!/usr/bin/env bash

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AI_VENV="$PROJECT_ROOT/.ai-venv"
AI_APP="$PROJECT_ROOT/ai-service-python/app/main.py"
AUTH_APP="$PROJECT_ROOT/auth-service-python/app.py"
BACKEND_DIR="$PROJECT_ROOT/backend-springboot"
BACKEND_JAR="$PROJECT_ROOT/backend-springboot/target/legal-document-analyzer-1.0.0.jar"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

PID_DIR="$PROJECT_ROOT/.run"
LOG_DIR="$PID_DIR/logs"
MONGO_DATA_DIR="$PID_DIR/mongo-data"

MONGO_PID_FILE="$PID_DIR/mongo.pid"
AI_PID_FILE="$PID_DIR/ai.pid"
AUTH_PID_FILE="$PID_DIR/auth.pid"
BACKEND_PID_FILE="$PID_DIR/backend.pid"
FRONTEND_PID_FILE="$PID_DIR/frontend.pid"

MONGO_LOG="$LOG_DIR/mongo.log"
AI_LOG="$LOG_DIR/ai.log"
AUTH_LOG="$LOG_DIR/auth.log"
BACKEND_LOG="$LOG_DIR/backend.log"
FRONTEND_LOG="$LOG_DIR/frontend.log"

require_cmd() {
    local cmd="$1"
    if ! command -v "$cmd" >/dev/null 2>&1; then
        echo "Missing required command: $cmd" >&2
        exit 1
    fi
}

is_running() {
    local pid_file="$1"
    if [[ -f "$pid_file" ]]; then
        local pid
        pid="$(cat "$pid_file")"
        if [[ -n "$pid" ]] && kill -0 "$pid" >/dev/null 2>&1; then
            return 0
        fi
        rm -f "$pid_file"
    fi
    return 1
}

wait_for_url() {
    local url="$1"
    local name="$2"
    local attempts="${3:-60}"
    local delay="${4:-2}"

    for ((i = 1; i <= attempts; i++)); do
        if curl -fsS "$url" >/dev/null 2>&1; then
            echo "$name is ready: $url"
            return 0
        fi
        sleep "$delay"
    done

    echo "$name did not become ready in time. Check logs in $LOG_DIR" >&2
    return 1
}

wait_for_tcp() {
    local host="$1"
    local port="$2"
    local name="$3"
    local attempts="${4:-30}"
    local delay="${5:-1}"

    for ((i = 1; i <= attempts; i++)); do
        if (echo >"/dev/tcp/$host/$port") >/dev/null 2>&1; then
            echo "$name is ready: $host:$port"
            return 0
        fi
        sleep "$delay"
    done

    echo "$name did not become ready in time. Check logs in $LOG_DIR" >&2
    return 1
}

port_is_open() {
    local host="$1"
    local port="$2"
    (echo >"/dev/tcp/$host/$port") >/dev/null 2>&1
}

start_detached() {
    local pid_file="$1"
    local log_file="$2"
    shift 2

    nohup setsid "$@" >"$log_file" 2>&1 &
    echo $! >"$pid_file"
}

setup_python_env() {
    if [[ ! -x "$AI_VENV/bin/python" ]]; then
        echo "Creating Python virtual environment at $AI_VENV"
        python3 -m venv "$AI_VENV"
    fi

    if ! "$AI_VENV/bin/python" -c "import flask, flask_cors, torch, transformers, sentencepiece" >/dev/null 2>&1; then
        echo "Installing AI service Python dependencies..."
        "$AI_VENV/bin/python" -m pip install -r "$PROJECT_ROOT/ai-service-python/requirements.txt"
    fi

    if ! "$AI_VENV/bin/python" -c "import flask_pymongo, flask_jwt_extended, pymongo" >/dev/null 2>&1; then
        echo "Installing auth service Python dependencies..."
        "$AI_VENV/bin/python" -m pip install -r "$PROJECT_ROOT/auth-service-python/requirements.txt"
    fi
}

setup_frontend() {
    if [[ ! -d "$FRONTEND_DIR/node_modules" ]]; then
        echo "Installing frontend dependencies..."
        (cd "$FRONTEND_DIR" && npm install)
    fi
}

setup_backend() {
    if [[ ! -f "$BACKEND_JAR" ]]; then
        echo "Building Spring backend..."
        (cd "$BACKEND_DIR" && mvn -DskipTests package)
    fi
}

mkdir -p "$PID_DIR" "$LOG_DIR" "$MONGO_DATA_DIR"

require_cmd python3
require_cmd java
require_cmd curl
require_cmd mvn
require_cmd npm
require_cmd mongod

setup_python_env
setup_frontend
setup_backend

if ! is_running "$MONGO_PID_FILE"; then
    echo "Starting MongoDB..."
    if port_is_open "127.0.0.1" "27017"; then
        echo "MongoDB port 27017 is already listening; using existing MongoDB."
        rm -f "$MONGO_PID_FILE"
    else
        start_detached "$MONGO_PID_FILE" "$MONGO_LOG" mongod --bind_ip 127.0.0.1 --port 27017 --dbpath "$MONGO_DATA_DIR"
    fi
else
    echo "MongoDB already running"
fi

if ! is_running "$AI_PID_FILE"; then
    if port_is_open "127.0.0.1" "5000"; then
        echo "AI service port 5000 is already listening; using existing service."
        rm -f "$AI_PID_FILE"
    else
        echo "Starting AI service..."
        start_detached "$AI_PID_FILE" "$AI_LOG" env PYTHONUNBUFFERED=1 FLASK_DEBUG=0 "$AI_VENV/bin/python" "$AI_APP"
    fi
else
    echo "AI service already running"
fi

if ! is_running "$AUTH_PID_FILE"; then
    if port_is_open "127.0.0.1" "5001"; then
        echo "Auth service port 5001 is already listening; using existing service."
        rm -f "$AUTH_PID_FILE"
    else
        echo "Starting auth service..."
        start_detached "$AUTH_PID_FILE" "$AUTH_LOG" env PYTHONUNBUFFERED=1 FLASK_DEBUG=0 MONGO_URI="mongodb://127.0.0.1:27017/llb_mini" "$AI_VENV/bin/python" "$AUTH_APP"
    fi
else
    echo "Auth service already running"
fi

if ! is_running "$BACKEND_PID_FILE"; then
    if port_is_open "127.0.0.1" "8080"; then
        echo "Spring backend port 8080 is already listening; using existing service."
        rm -f "$BACKEND_PID_FILE"
    else
        echo "Starting Spring backend..."
        start_detached "$BACKEND_PID_FILE" "$BACKEND_LOG" java -jar "$BACKEND_JAR" --spring.data.mongodb.uri="mongodb://127.0.0.1:27017/llb_mini"
    fi
else
    echo "Spring backend already running"
fi

if ! is_running "$FRONTEND_PID_FILE"; then
    if port_is_open "127.0.0.1" "3000"; then
        echo "Frontend port 3000 is already listening; using existing service."
        rm -f "$FRONTEND_PID_FILE"
    else
        echo "Starting frontend..."
        start_detached "$FRONTEND_PID_FILE" "$FRONTEND_LOG" npm --prefix "$FRONTEND_DIR" run dev -- --host 127.0.0.1 --port 3000
    fi
else
    echo "Frontend already running"
fi

wait_for_tcp "127.0.0.1" "27017" "MongoDB" 30 1
wait_for_url "http://127.0.0.1:5000/health" "AI service" 180 2
wait_for_url "http://127.0.0.1:5001/api/auth/health" "Auth service" 30 1
wait_for_url "http://127.0.0.1:8080/api/documents/health" "Spring backend" 60 2
wait_for_url "http://127.0.0.1:3000" "Frontend" 30 1

cat <<EOF

Application started successfully.

Open in browser:
  http://localhost:3000

Logs:
  $MONGO_LOG
  $AI_LOG
  $AUTH_LOG
  $BACKEND_LOG
  $FRONTEND_LOG

To stop everything:
  ./stop-all.sh
EOF
