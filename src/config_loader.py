"""
설정 로더 모듈
YAML 설정 파일을 읽고 관리합니다.
"""

import logging
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class VLLMConfig:
    """vLLM 설정"""
    api_url: str
    test_mode: bool
    timeout: int
    max_retries: int
    retry_delay: float


@dataclass
class ServerConfig:
    """서버 설정"""
    host: str
    port: int
    reload: bool
    workers: int


@dataclass
class DataConfig:
    """데이터 설정"""
    input_dir: str
    output_dir: str
    backup_enabled: bool
    backup_dir: Optional[str]


class ConfigManager:
    """설정 매니저"""
    
    def __init__(self, config_file: str = "config/config.yaml"):
        """
        설정 매니저 초기화
        
        Args:
            config_file: 설정 파일 경로
        """
        self.config_file = Path(config_file)
        self.config = self._load_config()
        
        logger.info(f"설정 로드 완료: {config_file}")
    
    def _load_config(self) -> Dict[str, Any]:
        """YAML 설정 파일 로드"""
        if not self.config_file.exists():
            raise FileNotFoundError(f"설정 파일을 찾을 수 없습니다: {self.config_file}")
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            if config is None:
                raise ValueError("설정 파일이 비어있습니다")
            
            return config
        except Exception as e:
            logger.error(f"설정 파일 로드 실패: {e}")
            raise
    
    def get_vllm_config(self) -> VLLMConfig:
        """vLLM 설정 반환"""
        vllm = self.config.get('vllm', {})
        return VLLMConfig(
            api_url=vllm.get('api_url', 'http://localhost:8000/v1'),
            test_mode=vllm.get('test_mode', True),
            timeout=vllm.get('timeout', 30),
            max_retries=vllm.get('max_retries', 3),
            retry_delay=vllm.get('retry_delay', 1)
        )
    
    def get_server_config(self) -> ServerConfig:
        """서버 설정 반환"""
        server = self.config.get('server', {})
        return ServerConfig(
            host=server.get('host', '0.0.0.0'),
            port=server.get('port', 8001),
            reload=server.get('reload', True),
            workers=server.get('workers', 4)
        )
    
    def get_data_config(self) -> DataConfig:
        """데이터 설정 반환"""
        data = self.config.get('data', {})
        return DataConfig(
            input_dir=data.get('input_dir', './data'),
            output_dir=data.get('output_dir', './results'),
            backup_enabled=data.get('backup_enabled', True),
            backup_dir=data.get('backup_dir', './backups')
        )
    
    def get_models(self) -> Dict[str, Dict[str, Any]]:
        """모델 설정 반환"""
        return self.config.get('models', {})
    
    def get_model(self, model_name: str) -> Dict[str, Any]:
        """특정 모델 설정 반환"""
        models = self.get_models()
        if model_name not in models:
            raise ValueError(f"모델을 찾을 수 없습니다: {model_name}")
        return models[model_name]
    
    def get_prompts(self) -> Dict[str, Dict[str, Any]]:
        """프롬프트 템플릿 설정 반환"""
        return self.config.get('prompts', {})
    
    def get_prompt(self, template_name: str) -> Dict[str, Any]:
        """특정 프롬프트 템플릿 설정 반환"""
        prompts = self.get_prompts()
        if template_name not in prompts:
            raise ValueError(f"프롬프트 템플릿을 찾을 수 없습니다: {template_name}")
        return prompts[template_name]
    
    def get_prompt_template_string(self, template_name: str) -> str:
        """프롬프트 템플릿 문자열 반환"""
        template = self.get_prompt(template_name)
        return template.get('template', '')
    
    def get_logging_config(self) -> Dict[str, Any]:
        """로깅 설정 반환"""
        return self.config.get('logging', {})
    
    def get_processing_config(self) -> Dict[str, Any]:
        """처리 설정 반환"""
        return self.config.get('processing', {})
    
    def get_ui_config(self) -> Dict[str, Any]:
        """UI 설정 반환"""
        return self.config.get('ui', {})
    
    def list_model_names(self) -> list:
        """모든 모델 이름 반환"""
        return list(self.get_models().keys())
    
    def list_prompt_names(self) -> list:
        """모든 프롬프트 템플릿 이름 반환"""
        return list(self.get_prompts().keys())
    
    def to_dict(self) -> Dict[str, Any]:
        """설정을 딕셔너리로 반환"""
        return self.config
