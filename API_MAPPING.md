# UI ↔ Backend API 매핑 정리

`index.html`(UI)과 `main.py`(FastAPI 서버) 간의 기능 연결 관계와 구현 상태를 정리합니다.

---

## 전체 API 현황

| 메서드 | 엔드포인트 | UI 사용 | main.py 구현 | 상태 |
|--------|-----------|---------|-------------|------|
| POST | `/upload` | ✅ | ❌ | **미구현 (필요)** |
| GET | `/files` | ✅ | ✅ | 정상 |
| GET | `/file/{file_name}` | ✅ | ✅ | 정상 |
| GET | `/config` | ✅ | ✅ | 정상 |
| GET | `/sheets` | ❌ | ✅ | UI 미사용 (제거 가능) |
| GET | `/data` | ✅ | ✅ | 정상 |
| POST | `/evaluate` | ✅ | ✅ | 정상 |
| GET | `/task/{task_id}` | ✅ | ✅ | 정상 |
| GET | `/download` | ✅ | ✅ | 정상 |
| GET | `/health` | ❌ | ✅ | UI 미사용 (유지) |

---

## 상세 API 명세

### 1. POST `/upload` — 파일 업로드 ❌ 미구현

UI 호출 위치: `index.html > handleFileUpload()`

```js
// UI 요청
fetch(`${API}/upload`, {
    method: 'POST',
    body: FormData  // key: 'file'
})
// UI 기대 응답: HTTP 200 (성공 시)
```

```python
# main.py에 추가 필요
@app.post("/upload", tags=["Files"])
async def upload_file(file: UploadFile = File(...)):
    # data_config.input_dir 에 파일 저장
    # 반환: { "file_name": str, "file_size": int }
```

> **조치 필요**: `main.py`에 `/upload` 엔드포인트 구현

---

### 2. GET `/files` — 파일 목록 ✅

UI 호출 위치: `index.html > loadFileList()`

```js
// UI 요청
fetch(`${API}/files`)

// UI 기대 응답
{ "files": ["test_data.xlsx", "data.csv"] }
```

```python
# main.py 구현 (FileListResponse)
{ "files": List[str] }  # data_manager.list_files() 결과
```

> 파일 목록 기준 디렉토리: `config.yaml > data.input_dir` (`./data`)

---

### 3. GET `/file/{file_name}` — 파일 정보 ✅

UI 호출 위치: `index.html > loadFileInfo(fileName)`

```js
// UI 요청
fetch(`${API}/file/${encodeURIComponent(fileName)}`)

// UI 기대 응답 (사용 필드)
{
    "file_name": "test_data.xlsx",
    "sheet_count": 3,
    "sheets": ["QA", "Sentiment", "Summary"]
}
```

```python
# main.py 구현 (FileInfoResponse)
{
    "file_name": str,
    "file_size": int,
    "sheets": List[str],
    "sheet_count": int,
    "created_time": str,
    "modified_time": str
}
```

> UI는 `file_name`, `sheet_count`, `sheets`만 사용. `file_size`, `created_time`, `modified_time`은 현재 미사용.

---

### 4. GET `/config` — 모델/프롬프트 설정 ✅

UI 호출 위치: `index.html > loadConfig()`

```js
// UI 요청
fetch(`${API}/config`)

// UI 기대 응답
{
    "models": ["model_1", "model_2", "model_3"],
    "prompts": ["template_1", "template_2", "template_3", "template_4"]
}
```

```python
# main.py 구현 (ConfigResponse)
{
    "models": List[str],    # config_manager.list_model_names()
    "prompts": List[str],   # config_manager.list_prompt_names()
    "vllm_test_mode": bool
}
```

> `config.yaml`의 `models`/`prompts` 키가 곧 UI 드롭다운 항목.
> 현재 등록된 모델: `model_1`, `model_2`, `model_3`
> 현재 등록된 템플릿: `template_1`, `template_2`, `template_3`, `template_4`

---

### 5. GET `/data` — 시트 데이터 조회 ✅

UI 호출 위치: `index.html > loadSheetData()`

```js
// UI 요청
fetch(`${API}/data?file_name=${fileName}&sheet_name=${sheetName}`)

// UI 기대 응답 (전체 사용)
{
    "file_name": "test_data.xlsx",
    "sheet_name": "QA",
    "columns": ["id", "question", "category"],
    "row_count": 5,
    "data": [{"id": 1, "question": "...", "category": "..."}, ...]
}
```

```python
# main.py 구현 (SheetDataResponse)
{
    "file_name": str,
    "sheet_name": str,
    "columns": List[str],
    "row_count": int,
    "data": List[Dict[str, Any]]
}
```

> `columns` 목록이 UI의 컬럼 선택 드롭다운(`inputColumnSelect`, `inputViewCol`, `answer1Col`, `answer2Col`)을 채우는 데 사용됨.

---

### 6. POST `/evaluate` — 추론 시작 ✅

UI 호출 위치: `index.html > handleStartInference()`

```js
// UI 요청
fetch(`${API}/evaluate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        file_name: "test_data.xlsx",
        sheet_name: "QA",
        model_name: "model_1",       // config.yaml의 models 키
        prompt_template: "template_1", // config.yaml의 prompts 키
        input_column: "question",     // 파일의 실제 컬럼명
        output_column: "answer_v1"    // 저장할 새 컬럼명
    })
})

// UI 기대 응답
{
    "task_id": "uuid-string",
    "status": "pending",
    "processed_rows": 0,
    "output_file": ""
}
```

```python
# main.py 구현 (EvaluateRequest → EvaluateResponse)
# 백그라운드 작업으로 실행 (BackgroundTasks)
# tasks dict에 EvaluationTask 저장
```

> `model_name` 필드가 Pydantic의 `model_` 네임스페이스 충돌 경고를 발생시킴.
> 해결: `model_config = ConfigDict(protected_namespaces=())` 추가 필요.

---

### 7. GET `/task/{task_id}` — 작업 상태 조회 ✅

UI 호출 위치: `index.html > pollTaskStatus()` (1초 간격 polling)

```js
// UI 요청
fetch(`${API}/task/${taskId}`)

// UI 기대 응답 (전체 사용)
{
    "task_id": "uuid-string",
    "status": "running",      // pending | running | completed | failed
    "progress": 3,
    "total": 5,
    "error_message": null
}
```

```python
# main.py 구현 (TaskStatusResponse)
# tasks dict에서 EvaluationTask 조회
```

> UI는 `status === 'completed'` 또는 `'failed'`가 될 때까지 polling 지속.
> `progress` / `total` 값으로 진행바 업데이트.

---

### 8. GET `/download` — 결과 파일 다운로드 ✅

UI 호출 위치: `index.html > handleDownload()`

```js
// UI 요청 (브라우저 리디렉션)
window.location.href = `${API}/download?file_name=${encodeURIComponent(fileName)}`
```

```python
# main.py 구현
# results 디렉토리에서 {stem}_output_*.xlsx 패턴으로 가장 최근 파일 반환
# FileResponse로 응답
```

> 결과 파일 저장 위치: `config.yaml > data.output_dir` (`./results`)
> 결과 파일명 패턴: `{원본파일명}_output_{timestamp}.xlsx`

---

## 데이터 흐름

```
[사용자]
  │
  ├─ 1. 파일 업로드 (POST /upload) ← ❌ 미구현
  │       └→ data/ 디렉토리에 저장
  │
  ├─ 2. 파일 목록 새로고침 (GET /files)
  │       └→ fileSelect 드롭다운 채움
  │
  ├─ 3. 파일 선택 → 파일 정보 조회 (GET /file/{name})
  │       └→ 파일명, 시트 수, sheetSelect 채움
  │
  ├─ 4. 시트 선택 → 데이터 조회 (GET /data)
  │       └→ 행 수, 컬럼명, 비교 뷰 컬럼 드롭다운 채움
  │
  ├─ 5. 추론 설정 (GET /config)
  │       └→ 모델/프롬프트 드롭다운 채움 (페이지 로드 시)
  │
  ├─ 6. 추론 실행 (POST /evaluate)
  │       └→ task_id 반환
  │
  ├─ 7. 상태 polling (GET /task/{id}) — 1초 간격
  │       └→ completed 시 loadSheetData() 재호출
  │
  └─ 8. 결과 다운로드 (GET /download)
```

---

## 조치 필요 항목

### 우선순위 HIGH

#### 1. POST `/upload` 엔드포인트 구현 (`main.py`)
현재 UI에서 파일 업로드 버튼을 눌러도 서버에 저장되지 않음.

```python
from fastapi import UploadFile, File
import shutil

@app.post("/upload", tags=["Files"])
async def upload_file(file: UploadFile = File(...)):
    dest = Path(data_config.input_dir) / file.filename
    with dest.open("wb") as f:
        shutil.copyfileobj(file.file, f)
    return {"file_name": file.filename, "file_size": dest.stat().st_size}
```

#### 2. Pydantic 경고 제거 (`main.py`)
`EvaluateRequest.model_name` 필드명이 `model_` 네임스페이스와 충돌.

```python
from pydantic import BaseModel, ConfigDict

class EvaluateRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    # ... 기존 필드들
```

---

### 우선순위 LOW

#### 3. GET `/sheets` 엔드포인트
`main.py`에 구현되어 있으나 UI에서 사용하지 않음.
`GET /file/{name}`의 응답에 `sheets`가 포함되어 있어 중복.
제거하거나 유지해도 무방.

---

## UI 컬럼 선택 ↔ 데이터 컬럼 연결

시트 선택 후 `GET /data`의 `columns` 응답이 아래 드롭다운을 모두 채움:

| UI 드롭다운 ID | 역할 |
|---------------|------|
| `inputColumnSelect` | 추론 시 LLM에 전달할 입력 컬럼 |
| `inputViewCol` | 비교 뷰 왼쪽 패널에 표시할 컬럼 |
| `answer1Col` | 비교 뷰 중간 패널 (LLM 답변 1) |
| `answer2Col` | 비교 뷰 오른쪽 패널 (LLM 답변 2) |

> `answer1Col`, `answer2Col`은 추론 완료 후 생성된 출력 컬럼을 선택해 비교하는 용도.

---

**Last Updated**: 2026-03-14
