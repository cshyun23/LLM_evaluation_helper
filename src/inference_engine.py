"""
추론 엔진 모듈
LLM 모델을 사용하여 실제 추론을 수행합니다.
"""

import logging
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
import pandas as pd

from .llm_client import LLMClientBase
from .config_loader import ConfigManager

logger = logging.getLogger(__name__)


@dataclass
class InferenceResult:
    """추론 결과"""
    input_text: str
    output_text: str
    model: str
    template: str
    timestamp: str
    status: str  # 'success' or 'error'
    error_message: Optional[str] = None


class InferenceEngine:
    """추론 엔진"""
    
    def __init__(self, llm_client: LLMClientBase, config_manager: ConfigManager):
        """
        추론 엔진 초기화
        
        Args:
            llm_client: LLM 클라이언트
            config_manager: 설정 매니저
        """
        self.llm_client = llm_client
        self.config_manager = config_manager
        self.results_cache = {}
        
        logger.info("추론 엔진 초기화 완료")
    
    def infer(self, input_text: str, model: str, template: str) -> InferenceResult:
        """
        입력 텍스트를 기반으로 추론 수행
        
        Args:
            input_text: 입력 텍스트
            model: 모델명
            template: 프롬프트 템플릿명
        
        Returns:
            InferenceResult 객체
        """
        try:
            # 모델 설정 가져오기
            model_config = self.config_manager.get_model(model)
            
            # 프롬프트 템플릿 생성
            prompt_template = self.config_manager.get_prompt_template_string(template)
            prompt = prompt_template.format(input=input_text)
            
            # LLM 호출
            logger.info(f"추론 시작: 모델={model}, 템플릿={template}")
            
            output_text = self.llm_client.generate(
                prompt=prompt,
                model=model_config.get('name', model),
                max_tokens=model_config.get('max_tokens', 512),
                temperature=model_config.get('temperature', 0.7),
                top_p=model_config.get('top_p', 0.95)
            )
            
            result = InferenceResult(
                input_text=input_text,
                output_text=output_text,
                model=model,
                template=template,
                timestamp=datetime.now().isoformat(),
                status='success'
            )
            
            logger.info(f"추론 완료: 모델={model}")
            return result
        
        except Exception as e:
            logger.error(f"추론 실패: {e}")
            
            result = InferenceResult(
                input_text=input_text,
                output_text='',
                model=model,
                template=template,
                timestamp=datetime.now().isoformat(),
                status='error',
                error_message=str(e)
            )
            
            return result
    
    def infer_batch(self, data: pd.DataFrame, input_column: str, output_column: str,
                   model: str, template: str,
                   progress_callback: Optional[Callable[[int, int], None]] = None) -> pd.DataFrame:
        """
        배치 추론 수행
        
        Args:
            data: 입력 데이터프레임
            input_column: 입력 컬럼명
            output_column: 출력 컬럼명
            model: 모델명
            template: 프롬프트 템플릿명
            progress_callback: 진행 상황 콜백 함수 (현재, 전체)
        
        Returns:
            추론 결과가 포함된 데이터프레임
        """
        logger.info(f"배치 추론 시작: 행 수={len(data)}, 모델={model}")
        
        results = []
        total = len(data)
        
        for idx, row in data.iterrows():
            input_text = row[input_column]
            
            # None 또는 빈 값 처리
            if pd.isna(input_text):
                logger.warning(f"행 {idx}의 입력 값이 None입니다. 스킵합니다.")
                results.append("")
                continue
            
            input_text = str(input_text).strip()
            
            # 추론 수행
            result = self.infer(input_text, model, template)
            
            # 결과 저장
            results.append(result.output_text)
            
            # 진행 상황 콜백
            if progress_callback:
                progress_callback(idx + 1, total)
            
            logger.debug(f"배치 추론 진행: {idx + 1}/{total}")
        
        # 결과를 데이터프레임에 추가
        data[output_column] = results
        
        logger.info(f"배치 추론 완료: 총 {len(results)}행 처리됨")
        
        return data
    
    def validate_inputs(self, model: str, template: str, input_column: str) -> bool:
        """
        입력값 검증
        
        Args:
            model: 모델명
            template: 프롬프트 템플릿명
            input_column: 입력 컬럼명
        
        Returns:
            검증 성공 여부
        """
        try:
            # 모델 확인
            self.config_manager.get_model(model)
            
            # 프롬프트 템플릿 확인
            self.config_manager.get_prompt_template_string(template)
            
            # 컬럼명이 비어있지 않은지 확인
            if not input_column or not input_column.strip():
                raise ValueError("입력 컬럼명이 비어있습니다")
            
            return True
        
        except Exception as e:
            logger.error(f"입력값 검증 실패: {e}")
            raise


class EvaluationTask:
    """평가 작업"""
    
    def __init__(self, task_id: str, file_name: str, sheet_name: str, 
                 model: str, template: str, input_column: str, output_column: str):
        """
        평가 작업 초기화
        
        Args:
            task_id: 작업 ID
            file_name: 파일명
            sheet_name: 시트명
            model: 모델명
            template: 프롬프트 템플릿명
            input_column: 입력 컬럼명
            output_column: 출력 컬럼명
        """
        self.task_id = task_id
        self.file_name = file_name
        self.sheet_name = sheet_name
        self.model = model
        self.template = template
        self.input_column = input_column
        self.output_column = output_column
        self.status = 'pending'  # pending, running, completed, failed
        self.progress = 0
        self.total = 0
        self.result = None
        self.error_message = None
        self.created_at = datetime.now().isoformat()
        self.started_at = None
        self.completed_at = None
    
    def start(self):
        """작업 시작"""
        self.status = 'running'
        self.started_at = datetime.now().isoformat()
        logger.info(f"작업 시작: {self.task_id}")
    
    def complete(self, result=None):
        """작업 완료"""
        self.status = 'completed'
        self.completed_at = datetime.now().isoformat()
        self.result = result
        logger.info(f"작업 완료: {self.task_id}")
    
    def fail(self, error_message: str):
        """작업 실패"""
        self.status = 'failed'
        self.completed_at = datetime.now().isoformat()
        self.error_message = error_message
        logger.error(f"작업 실패: {self.task_id} - {error_message}")
    
    def update_progress(self, progress: int, total: int):
        """진행 상황 업데이트"""
        self.progress = progress
        self.total = total
        progress_percent = (progress / total * 100) if total > 0 else 0
        logger.debug(f"작업 진행: {self.task_id} - {progress}/{total} ({progress_percent:.1f}%)")
    
    def to_dict(self) -> Dict[str, Any]:
        """작업을 딕셔너리로 변환"""
        return {
            'task_id': self.task_id,
            'file_name': self.file_name,
            'sheet_name': self.sheet_name,
            'model': self.model,
            'template': self.template,
            'input_column': self.input_column,
            'output_column': self.output_column,
            'status': self.status,
            'progress': self.progress,
            'total': self.total,
            'error_message': self.error_message,
            'created_at': self.created_at,
            'started_at': self.started_at,
            'completed_at': self.completed_at
        }
