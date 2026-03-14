#!/bin/bash

# LLM Evaluation Helper - 가상환경 설정 스크립트

# 스크립트 위치로 이동 (한글 경로 대응)
cd "$(dirname "$(readlink -f "$0" 2>/dev/null || echo "$0")")" 2>/dev/null || true

# 가상환경 생성
echo "[INFO] 가상환경 생성 중..."
python -m venv .venv

# 가상환경 활성화 (Windows/Linux 모두 대응)
if [ -f ".venv/Scripts/activate" ]; then
    source .venv/Scripts/activate
elif [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

# pip 업그레이드
pip install --upgrade pip -q

# 의존성 설치
echo "[INFO] 패키지 설치 중..."
pip install -r requirements.txt

echo "[INFO] 가상환경 설정 완료. 'bash run_server.sh'로 서버를 시작하세요."
