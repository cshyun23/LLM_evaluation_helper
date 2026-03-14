# 개발 진행 이력

## 2026-03-13

### 1. 프로젝트 목표 및 설계안 작성
- **파일**: README.md
- **내용**: 
  - 프로젝트 목표 정의 (LLM 추론 서버 + HTML UI)
  - 아키텍처 설계 (FastAPI, vLLM, Config 기반)
  - Config 구조 설계 (YAML 형식)
  - API 엔드포인트 상세 설계
  - 기술 스택 결정

### 2. 개발 주의사항 문서화
- **파일**: DEVELOPMENT_NOTES.md
- **내용**:
  - 테스트 정책: 명시적 지시 없이는 테스트 수행 안 함
  - 문서화 정책: 모든 결과를 history.md에 기록
  - 개발 환경: .venv 가상환경 사용

### 3. HTML UI 설계 및 구현
- **파일**: index.html
- **기능**:
  - 📁 파일 업로드/다운로드
  - 📄 시트 선택
  - ⚙️ 추론 설정 (모델, 프롬프트, 컬럼명)
  - 🔄 좌우 비교 뷰 (원본 ↔ LLM 답변)
  - 📊 데이터 테이블
  - ⏱️ 진행 상황 표시
  - 🎨 반응형 디자인

- **주요 특징**:
  - 시트별 데이터 관리
  - 행 단위 네비게이션
  - 실시간 상태 표시
  - REST API 기반 (POST /evaluate, GET /sheets, 등)
  - 매개변수 입력 폼

### 4. Python 가상환경 설정
- **파일**: .venv, requirements.txt
- **상태**: ✅ 완료

**가상환경 생성:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**설치된 라이브러리:**

| 카테고리 | 패키지 | 버전 |
|---------|--------|------|
| **Web Framework** | FastAPI | 0.135.1 |
| | Uvicorn | 0.41.0 |
| | Starlette | 0.52.1 |
| | Python-multipart | 0.0.22 |
| **Data Processing** | Pandas | 3.0.1 |
| | NumPy | 2.4.3 |
| | OpenPyXL | 3.1.5 |
| | Python-dateutil | 2.9.0.post0 |
| **HTTP Client** | Requests | 2.32.5 |
| | HTTPx | 0.28.1 |
| **Configuration** | PyYAML | 6.0.3 |
| | Python-dotenv | 1.2.2 |
| **Data Validation** | Pydantic | 2.12.5 |
| **Utilities** | Certifi, Charset-normalizer, 기타 | - |

**가상환경 활성화 명령:**
```bash
# Windows CMD
.venv\Scripts\activate

# Windows PowerShell
.venv\Scripts\Activate.ps1

# Linux/Mac
source .venv/bin/activate
```

---

**현재 상태**: 가상환경 및 라이브러리 설치 완료 / 백엔드 구현 시작 예정

### 5. 프로젝트 구조 및 백엔드 구현 (완료)
- **파일들**:
  - `config/config.yaml` - 설정 파일 (vLLM, 모델, 프롬프트 등)
  - `src/config_loader.py` - 설정 로더 모듈
  - `src/data_manager.py` - Excel/CSV 데이터 관리
  - `src/llm_client.py` - vLLM 클라이언트 (더미 + 실제 버전)
  - `src/inference_engine.py` - 추론 엔진
  - `main.py` - FastAPI 메인 서버
  - `create_test_data.py` - 테스트 데이터 생성
  - `test_integration.py` - 통합 테스트

**주요 특징:**

1. **더미/실제 모드 분리**
   - `DummyLLMClient`: 테스트용 더미 응답 (vLLM 필요 없음)
   - `VLLMClient`: 실제 vLLM 서버 연동
   - `config.yaml`의 `test_mode` 플래그로 전환 가능

2. **설정 관리 (YAML)**
   - vLLM 서버 설정
   - 3개 모델 정의 (model_1, model_2, model_3)
   - 4개 프롬프트 템플릿 정의
   - 서버, 처리, UI 설정

3. **데이터 관리 기능**
   - Excel/CSV 파일 읽기/쓰기
   - 시트 목록 조회
   - 파일 정보 조회
   - 자동 백업 기능

4. **LLM 클라이언트**
   - 추상 클래스 기반 설계
   - 더미 클라이언트: 사전 정의된 응답 제공
   - 실제 클라이언트: vLLM API 호출 (재시도, 타임아웃 처리)
   - 팩토리 패턴으로 생성

5. **추론 엔진**
   - 단일 추론 (문자열 입력 → 문자열 출력)
   - 배치 추론 (DataFrame 입력 → 결과 DataFrame)
   - 진행 상황 콜백 지원
   - 입력값 검증

6. **FastAPI 서버**
   - REST API 엔드포인트 구현
   - 파일 관리 (업로드, 다운로드)
   - 시트 및 데이터 조회
   - 평가 작업 (비동기)
   - 작업 상태 추적
   - CORS 지원

**테스트 결과: ✅ 4/4 PASS**
- ✅ 설정 로더 테스트
- ✅ 데이터 매니저 테스트
- ✅ LLM 클라이언트 테스트 (더미 모드)
- ✅ 추론 엔진 테스트 (배치 처리 포함)

**생성된 파일:**
- `data/test_data.xlsx` - 3개 시트 테스트 데이터 (QA, Sentiment, Summary)
- `data/test_data.csv` - CSV 테스트 데이터

---

**현재 상태**: 전체 백엔드 구현 완료 / 서버 시작 준비 완료

### 6. Git 설정 (.gitignore)
- **파일**: `.gitignore`
- **제외 항목**:
  - `.venv/` - Python 가상환경
  - `.vscode/` - VS Code 설정
  - `backups/` - 백업 디렉토리
  - `logs/` - 로그 파일
  - `__pycache__/` - Python 캐시
  - `*.pyc`, `*.pyo`, `*.pyd` - 컴파일된 Python 파일
  - `.pytest_cache/`, `.coverage` - 테스트 관련 파일
  - `*.log` - 로그 파일
  - 기타 시스템 파일 (.DS_Store, Thumbs.db 등)

**효과:**
- 로컬 개발 환경 파일이 커밋되지 않음
- 저장소 크기 최소화
- 팀 협업 시 충돌 방지

---

**현재 상태**: Git 설정 완료 / 프로젝트 준비 완료

---

## 2026-03-14

### 7. 테스트 데이터 생성 및 데이터 템플릿 문서 작성

- **파일들**:
  - `data/test_data.xlsx` - 더미 테스트 데이터 (3개 시트)
  - `data/test_data.csv` - QA 데이터 CSV
  - `data/DATA_TEMPLATE.md` - 데이터 템플릿 가이드 문서

**생성된 데이터:**

| 시트 | 컬럼 | 행 수 | 용도 |
|------|------|-------|------|
| QA | id, question, category | 5 | 질의응답 추론 테스트 |
| Sentiment | id, text, sentiment | 5 | 감성 분류 테스트 |
| Summary | id, content | 3 | 텍스트 요약 테스트 |

**데이터 템플릿 문서 내용:**
- 지원 파일 형식 (xlsx, csv)
- 필수/선택 컬럼 구성 규칙
- 시트별 예시 데이터 및 추천 설정 (입력 컬럼, 출력 컬럼, 프롬프트 템플릿)
- 사용자 데이터 작성 방법 (Excel/CSV)
- 추론 실행 후 결과 구조 설명

**참고**: `.venv` 미존재로 시스템 Python(3.11.9) 사용, `openpyxl` pip 설치 후 실행

---

**현재 상태**: 테스트 데이터 및 문서 완료 / UI-백엔드 연동 테스트 단계 남음

### 8. 서버 실행 명령어 문서화

- **파일**: `README.md` — "서버 실행" 섹션 추가
- **내용**:
  - 환경 준비 (가상환경 생성/활성화, 의존성 설치)
  - 서버 시작 3가지 방법 (python main.py / uvicorn / uvicorn --reload)
  - 접속 URL 정리 (API 루트, Swagger UI, ReDoc, 헬스 체크)
  - test_mode 전환 방법

---

**현재 상태**: README 서버 실행 섹션 추가 완료

### 9. index.html UI 수정

- **변경 내용**:
  - 비교 뷰: 2-pane → 3-pane (입력 / LLM 답변 1 / LLM 답변 2)
  - 하단 데이터 테이블 섹션 제거
  - 입력 컬럼 직접 입력 → 드롭다운 선택 (시트 선택 시 서버에서 컬럼 목록 로드)
  - 파일 정보 (시트 수/행 수/컬럼명) 서버 API로 실제 값 표시
  - 모델/프롬프트 드롭다운 GET /config 에서 동적 로드
  - 추론 완료를 GET /task/{id} polling으로 감지 후 자동 갱신
  - 서버 파일 목록 새로고침 버튼 추가

### 10. API_MAPPING.md 작성

- **파일**: `API_MAPPING.md`
- **내용**:
  - 전체 API 현황표 (UI 사용 여부 / 구현 여부 / 상태)
  - 엔드포인트별 UI 요청 형식 ↔ main.py 응답 형식 상세 대조
  - 데이터 흐름 다이어그램
  - 조치 필요 항목 (HIGH: POST /upload 미구현, Pydantic 경고 / LOW: GET /sheets 중복)
  - UI 컬럼 선택 드롭다운 역할 정리

---

**현재 상태**: UI-백엔드 매핑 문서 완료 / 조치 필요: POST /upload 구현, Pydantic 경고 수정
