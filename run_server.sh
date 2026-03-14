#!/bin/bash

# 스크립트 위치를 기준으로 프로젝트 루트로 이동
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 가상환경 활성화 (Windows/Linux 대응)
if [ -f ".venv/Scripts/activate" ]; then
    source .venv/Scripts/activate
elif [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
else
    echo "[ERROR] .venv 가상환경이 없습니다. setup_venv.sh를 먼저 실행하세요."
    exit 1
fi

# 서버 실행
python "$SCRIPT_DIR/main.py"
