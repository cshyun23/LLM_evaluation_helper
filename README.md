# LLM Evaluation Helper

프롬프트 변경에 따른 LLM의 답변을 체계적으로 비교 및 평가하기 위한 도구입니다.

---

## 📋 프로젝트 목표

1. **LLM 추론 동작 서버** 구축
   - CSV/Excel 파일의 데이터를 읽고 지정된 프롬프트를 통해 LLM 답변 생성
   - 생성된 답변을 동일 Excel 파일에 저장

2. **정성 비교용 HTML 기반 UI** 개발
   - 프롬프트 변경에 따른 LLM 답변을 시각적으로 비교
   - 답변의 품질을 정성적으로 평가할 수 있는 인터페이스 제공

---

## 🏗️ 설계안

### 1. 데이터 구조
- **입력 형식**: CSV / Excel 파일 (.xlsx, .csv)
- **데이터 구성**: 각 행에 평가 대상 데이터
- **시트 관리**: 시트별로 다른 유형의 데이터 분류
- **출력**: 생성된 LLM 답변을 원본 파일에 저장

### 2. 아키텍처 개요
```
┌─────────────────────────────────────────────────────────┐
│                  FastAPI Server (항상 실행)              │
├─────────────────────────────────────────────────────────┤
│  API Endpoints (HTTP 요청으로 제어)                      │
│  ├─ POST /evaluate                                      │
│  │  └─ 파라미터: file_name, sheet_name, model_name     │
│  ├─ GET /sheets?file_name=xxx                          │
│  ├─ GET /data?file_name=xxx&sheet_name=yyy             │
│  └─ GET /results?file_name=xxx&sheet_name=yyy          │
├─────────────────────────────────────────────────────────┤
│  설정 관리 (config.yaml)                                │
│  ├─ vLLM 서버 연결 정보                                 │
│  ├─ 프롬프트 템플릿                                     │
│  ├─ 모델 정보                                           │
│  └─ 파일 경로 설정                                      │
├─────────────────────────────────────────────────────────┤
│  LLM 추론 엔진                                          │
│  ├─ vLLM 서버 클라이언트                                │
│  ├─ 프롬프트 처리                                       │
│  └─ 응답 처리                                           │
├─────────────────────────────────────────────────────────┤
│  데이터 관리                                            │
│  ├─ Excel/CSV 읽기/쓰기                                 │
│  └─ 시트 선택 및 처리                                   │
└─────────────────────────────────────────────────────────┘
```

### 3. Config 구조
```yaml
# config.yaml
vllm:
  api_url: "http://localhost:8000"  # vLLM 서버 주소
  timeout: 30

models:
  model_1:
    name: "meta-llama/Llama-2-7b"
    max_tokens: 512
  model_2:
    name: "mistralai/Mistral-7B"
    max_tokens: 512

prompts:
  template_1: "질문: {input}\n답변:"
  template_2: "Please answer: {input}"

data:
  input_dir: "./data"
  output_dir: "./results"
```

### 4. API 엔드포인트 상세 설계
```
POST /evaluate
요청:
{
  "file_name": "data.xlsx",
  "sheet_name": "Sheet1",
  "model_name": "model_1",
  "prompt_template": "template_1",
  "input_column": "question",
  "output_column": "answer"
}
응답:
{
  "status": "success",
  "file_path": "./results/data_output.xlsx",
  "processed_rows": 100
}

GET /sheets?file_name=data.xlsx
응답:
{
  "file_name": "data.xlsx",
  "sheets": ["Sheet1", "Sheet2", "Sheet3"]
}

GET /data?file_name=data.xlsx&sheet_name=Sheet1
응답:
{
  "file_name": "data.xlsx",
  "sheet_name": "Sheet1",
  "columns": ["id", "question", "category"],
  "data": [...],
  "row_count": 100
}
```

### 5. 실행 흐름
```
1. FastAPI 서버 시작 (항상 실행 상태)
2. 사용자가 HTTP 요청으로 파일명, 시트명, 모델명 등 전달
3. 서버가 config에서 프롬프트, 모델 정보 로드
4. Excel/CSV 파일에서 데이터 읽기
5. 각 행의 데이터를 프롬프트에 맞춰 처리
6. vLLM 서버로 추론 요청
7. 응답을 받아 파일에 저장
8. 결과를 HTTP 응답으로 반환
```

### 6. UI 설계
- **HTML/CSS 기반 웹 인터페이스**
- **기능**:
  - 파일 선택 (input_dir에서 목록 조회)
  - 시트 선택 (동적 API 호출)
  - 모델 선택 (config에서 로드)
  - 프롬프트 템플릿 선택
  - 입력/출력 컬럼 지정
  - 추론 실행 (HTTP 요청)
  - 진행 상황 모니터링
  - 결과 비교 뷰 (원본 ↔ LLM 답변)
  - 결과 다운로드

---

## 🛠️ 기술 스택
- **Backend**: Python (FastAPI)
- **Frontend**: HTML/CSS/JavaScript
- **LLM Inference**: vLLM (이미 서빙 중)
- **Data Processing**: openpyxl, pandas
- **Configuration**: YAML (PyYAML)
- **Server**: FastAPI 내장 서버 또는 Gunicorn

---

## 📝 개발 일정
- [ ] 프로젝트 기본 구조 설정
- [ ] 서버 API 개발
- [ ] 파일 입출력 기능 구현
- [ ] HTML UI 개발
- [ ] LLM 통합 및 테스트
- [ ] 최적화 및 배포

---

**Last Updated**: 2026-03-13