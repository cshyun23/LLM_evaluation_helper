"""
FastAPI 메인 서버
LLM Evaluation Helper REST API
"""

import logging
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from fastapi import FastAPI, HTTPException, File, UploadFile, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# 로컬 모듈 import
from src.config_loader import ConfigManager
from src.data_manager import DataManager
from src.llm_client import LLMClientFactory
from src.inference_engine import InferenceEngine, EvaluationTask

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ==================== Pydantic 모델 ====================

class SheetListResponse(BaseModel):
    """시트 목록 응답"""
    file_name: str
    sheets: List[str]


class SheetDataResponse(BaseModel):
    """시트 데이터 응답"""
    file_name: str
    sheet_name: str
    columns: List[str]
    row_count: int
    data: List[Dict[str, Any]]


class FileListResponse(BaseModel):
    """파일 목록 응답"""
    files: List[str]


class FileInfoResponse(BaseModel):
    """파일 정보 응답"""
    file_name: str
    file_size: int
    sheets: List[str]
    sheet_count: int
    created_time: str
    modified_time: str


class EvaluateRequest(BaseModel):
    """평가 요청"""
    file_name: str
    sheet_name: str
    model_name: str
    prompt_template: str
    input_column: str
    output_column: str


class EvaluateResponse(BaseModel):
    """평가 응답"""
    task_id: str
    status: str
    processed_rows: int
    output_file: str


class TaskStatusResponse(BaseModel):
    """작업 상태 응답"""
    task_id: str
    status: str
    progress: int
    total: int
    error_message: Optional[str] = None


class ConfigResponse(BaseModel):
    """설정 정보 응답"""
    models: List[str]
    prompts: List[str]
    vllm_test_mode: bool


# ==================== FastAPI 앱 초기화 ====================

# 설정 로드
config_manager = ConfigManager("config/config.yaml")
server_config = config_manager.get_server_config()
data_config = config_manager.get_data_config()
vllm_config = config_manager.get_vllm_config()

# 데이터 매니저 초기화
data_manager = DataManager(
    input_dir=data_config.input_dir,
    output_dir=data_config.output_dir,
    backup_dir=data_config.backup_dir if data_config.backup_enabled else None
)

# LLM 클라이언트 생성
llm_client = LLMClientFactory.create_client(
    test_mode=vllm_config.test_mode,
    api_url=vllm_config.api_url,
    timeout=vllm_config.timeout
)

# 추론 엔진 초기화
inference_engine = InferenceEngine(llm_client, config_manager)

# FastAPI 앱 생성
app = FastAPI(
    title="LLM Evaluation Helper API",
    description="프롬프트 변경에 따른 LLM 답변을 비교하고 평가하는 도구",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 작업 저장소
tasks: Dict[str, EvaluationTask] = {}


# ==================== API 엔드포인트 ====================

@app.get("/", tags=["Root"])
async def root():
    """루트 엔드포인트"""
    return {
        "message": "LLM Evaluation Helper API",
        "version": "1.0.0",
        "test_mode": vllm_config.test_mode
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """헬스 체크"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/config", response_model=ConfigResponse, tags=["Configuration"])
async def get_config():
    """설정 정보 조회"""
    return ConfigResponse(
        models=config_manager.list_model_names(),
        prompts=config_manager.list_prompt_names(),
        vllm_test_mode=vllm_config.test_mode
    )


@app.get("/files", response_model=FileListResponse, tags=["Files"])
async def list_files():
    """업로드 가능한 파일 목록"""
    try:
        files = data_manager.list_files()
        return FileListResponse(files=files)
    except Exception as e:
        logger.error(f"파일 목록 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/file/{file_name}", response_model=FileInfoResponse, tags=["Files"])
async def get_file_info(file_name: str):
    """파일 정보 조회"""
    try:
        info = data_manager.get_file_info(file_name)
        return FileInfoResponse(
            file_name=info["file_name"],
            file_size=info["file_size"],
            sheets=info["sheets"],
            sheet_count=info["sheet_count"],
            created_time=info["created_time"],
            modified_time=info["modified_time"]
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"파일 정보 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sheets", response_model=SheetListResponse, tags=["Sheets"])
async def get_sheets(file_name: str):
    """시트 목록 조회"""
    try:
        sheets = data_manager.get_sheets(file_name)
        return SheetListResponse(file_name=file_name, sheets=sheets)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"시트 목록 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/data", response_model=SheetDataResponse, tags=["Data"])
async def get_sheet_data(file_name: str, sheet_name: str):
    """시트 데이터 조회"""
    try:
        df, columns = data_manager.read_sheet(file_name, sheet_name)
        
        # 데이터를 딕셔너리 리스트로 변환
        data = df.to_dict('records')
        
        return SheetDataResponse(
            file_name=file_name,
            sheet_name=sheet_name,
            columns=columns,
            row_count=len(df),
            data=data
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"데이터 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/evaluate", response_model=EvaluateResponse, tags=["Evaluation"])
async def evaluate(request: EvaluateRequest, background_tasks: BackgroundTasks):
    """평가 작업 시작"""
    try:
        # 입력값 검증
        inference_engine.validate_inputs(
            request.model_name,
            request.prompt_template,
            request.input_column
        )
        
        # 데이터 로드
        df, columns = data_manager.read_sheet(request.file_name, request.sheet_name)
        
        # 입력 컬럼 확인
        if request.input_column not in columns:
            raise ValueError(f"입력 컬럼을 찾을 수 없습니다: {request.input_column}")
        
        # 작업 생성
        task_id = str(uuid.uuid4())
        task = EvaluationTask(
            task_id=task_id,
            file_name=request.file_name,
            sheet_name=request.sheet_name,
            model=request.model_name,
            template=request.prompt_template,
            input_column=request.input_column,
            output_column=request.output_column
        )
        
        tasks[task_id] = task
        
        # 백그라운드 작업으로 추론 시작
        background_tasks.add_task(
            run_evaluation,
            task_id=task_id,
            df=df,
            request=request
        )
        
        logger.info(f"평가 작업 시작: task_id={task_id}")
        
        return EvaluateResponse(
            task_id=task_id,
            status='pending',
            processed_rows=0,
            output_file=''
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"평가 작업 생성 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/task/{task_id}", response_model=TaskStatusResponse, tags=["Tasks"])
async def get_task_status(task_id: str):
    """작업 상태 조회"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail=f"작업을 찾을 수 없습니다: {task_id}")
    
    task = tasks[task_id]
    return TaskStatusResponse(
        task_id=task.task_id,
        status=task.status,
        progress=task.progress,
        total=task.total,
        error_message=task.error_message
    )


@app.get("/download", tags=["Download"])
async def download_result(file_name: str):
    """결과 파일 다운로드"""
    try:
        # 결과 디렉토리에서 가장 최근 파일 찾기
        output_dir = Path(data_config.output_dir)
        files = list(output_dir.glob(f"{Path(file_name).stem}_output_*.xlsx"))
        
        if not files:
            raise FileNotFoundError(f"결과 파일을 찾을 수 없습니다: {file_name}")
        
        # 가장 최근 파일 선택
        latest_file = max(files, key=lambda p: p.stat().st_mtime)
        
        return FileResponse(
            latest_file,
            filename=latest_file.name,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"파일 다운로드 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 백그라운드 작업 ====================

async def run_evaluation(task_id: str, df, request: EvaluateRequest):
    """평가 작업 실행"""
    task = tasks[task_id]
    
    try:
        task.start()
        
        # 배치 추론 수행
        result_df = inference_engine.infer_batch(
            data=df,
            input_column=request.input_column,
            output_column=request.output_column,
            model=request.model_name,
            template=request.prompt_template,
            progress_callback=lambda current, total: task.update_progress(current, total)
        )
        
        # 결과 저장
        output_file = data_manager.write_sheet(
            result_df,
            request.file_name,
            request.sheet_name
        )
        
        task.complete(output_file)
        logger.info(f"평가 작업 완료: task_id={task_id}, output={output_file}")
    
    except Exception as e:
        task.fail(str(e))
        logger.error(f"평가 작업 실패: task_id={task_id}, error={e}")


# ==================== 메인 ====================

if __name__ == "__main__":
    logger.info(f"서버 시작: {server_config.host}:{server_config.port}")
    logger.info(f"vLLM 테스트 모드: {vllm_config.test_mode}")
    
    uvicorn.run(
        app,
        host=server_config.host,
        port=server_config.port,
        reload=server_config.reload
    )
