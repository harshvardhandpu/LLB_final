#!/usr/bin/env bash

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_DIR="$PROJECT_ROOT/.run"

stop_from_pid_file() {
    local pid_file="$1"
    local name="$2"

    if [[ ! -f "$pid_file" ]]; then
        echo "$name is not running"
        return
    fi

    local pid
    pid="$(cat "$pid_file")"

    if [[ -n "$pid" ]] && kill -0 "$pid" >/dev/null 2>&1; then
        echo "Stopping $name (pid $pid)"
        kill -- "-$pid" >/dev/null 2>&1 || kill "$pid"

        for _ in {1..10}; do
            if ! kill -0 "$pid" >/dev/null 2>&1; then
                break
            fi
            sleep 1
        done

        if kill -0 "$pid" >/dev/null 2>&1; then
            echo "Force stopping $name (pid $pid)"
            kill -9 -- "-$pid" >/dev/null 2>&1 || kill -9 "$pid"
        fi
    else
        echo "$name is not running"
    fi

    rm -f "$pid_file"
}

stop_from_pid_file "$PID_DIR/ai.pid" "AI service"
stop_from_pid_file "$PID_DIR/auth.pid" "Auth service"
stop_from_pid_file "$PID_DIR/backend.pid" "Spring backend"
stop_from_pid_file "$PID_DIR/frontend.pid" "Frontend"
stop_from_pid_file "$PID_DIR/mongo.pid" "MongoDB"

echo "All services processed."
