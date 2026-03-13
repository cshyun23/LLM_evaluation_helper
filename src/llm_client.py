"""
vLLM 클라이언트 모듈
더미 버전과 실제 호출 버전 분리
"""

import logging
import requests
import time
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class LLMClientBase(ABC):
    """LLM 클라이언트 기본 클래스"""
    
    def __init__(self, api_url: str = None, timeout: int = 30):
        """
        기본 초기화
        
        Args:
            api_url: API 엔드포인트
            timeout: 요청 타임아웃 (초)
        """
        self.api_url = api_url
        self.timeout = timeout
    
    @abstractmethod
    def generate(self, prompt: str, model: str, max_tokens: int = 512,
                temperature: float = 0.7, top_p: float = 0.95) -> str:
        """
        텍스트 생성 (추상 메서드)
        
        Args:
            prompt: 입력 프롬프트
            model: 모델명
            max_tokens: 최대 토큰 수
            temperature: 창의성 (0.0 ~ 2.0)
            top_p: Top-p 샘플링 값
        
        Returns:
            생성된 텍스트
        """
        pass


class DummyLLMClient(LLMClientBase):
    """더미 LLM 클라이언트 (테스트용)"""
    
    def __init__(self):
        """더미 클라이언트 초기화"""
        super().__init__()
        self.call_count = 0
        
        # 더미 응답 데이터
        self.dummy_responses = {
            "Python이란 무엇인가?": "Python은 Guido van Rossum이 개발한 고급 프로그래밍 언어입니다. 간결한 문법, 강력한 기능, 풍부한 라이브러리를 특징으로 하며, 데이터 과학, 머신러닝, 웹 개발 등 다양한 분야에서 널리 사용되고 있습니다.",
            "JavaScript의 용도는?": "JavaScript는 웹 브라우저에서 실행되는 클라이언트 사이드 스크립팅 언어입니다. DOM 조작, 이벤트 처리, 동적 웹 페이지 구현이 가능하며, Node.js를 통해 서버 사이드에서도 사용할 수 있습니다.",
            "FastAPI의 장점은?": "FastAPI는 Python 기반의 현대적 웹 프레임워크로, 빠른 성능, 자동 API 문서 생성, 타입 힌트 지원, 비동기 프로그래밍 지원 등의 장점이 있습니다. 또한 Starlette와 Pydantic 기반으로 매우 견고합니다.",
            "머신러닝이란?": "머신러닝은 데이터로부터 패턴을 학습하고 예측하는 인공지능 기술입니다. 지도학습, 비지도학습, 강화학습 등 다양한 방법론이 있으며, 현대의 데이터 분석과 의사결정에 필수적입니다.",
        }
        
        logger.info("더미 LLM 클라이언트 초기화됨")
    
    def generate(self, prompt: str, model: str = "dummy-model", 
                max_tokens: int = 512, temperature: float = 0.7, 
                top_p: float = 0.95) -> str:
        """
        더미 응답 생성
        
        실제 API 호출 없이 사전 정의된 응답을 반환합니다.
        """
        self.call_count += 1
        
        # 프롬프트에서 질문 부분만 추출 (간단한 처리)
        question = prompt.split('\n')[0] if '\n' in prompt else prompt
        question = question.replace("질문: ", "").replace("Question: ", "").strip()
        
        # 기본 응답 또는 사전 정의된 응답 반환
        response = self.dummy_responses.get(
            question,
            f"이것은 '{question}'에 대한 더미 응답입니다. 실제 {model} 모델의 응답은 vLLM 서버를 통해 얻을 수 있습니다."
        )
        
        # 시뮬레이션: 약간의 지연
        time.sleep(0.5)
        
        logger.debug(f"더미 응답 생성 #{self.call_count}: {question[:50]}...")
        return response
    
    def get_call_count(self) -> int:
        """호출 횟수 반환"""
        return self.call_count


class VLLMClient(LLMClientBase):
    """실제 vLLM 클라이언트"""
    
    def __init__(self, api_url: str, timeout: int = 30, max_retries: int = 3, 
                retry_delay: float = 1.0):
        """
        vLLM 클라이언트 초기화
        
        Args:
            api_url: vLLM API 엔드포인트 (예: http://localhost:8000/v1)
            timeout: 요청 타임아웃
            max_retries: 최대 재시도 횟수
            retry_delay: 재시도 간격 (초)
        """
        super().__init__(api_url, timeout)
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.session = requests.Session()
        
        logger.info(f"vLLM 클라이언트 초기화: {api_url}")
    
    def generate(self, prompt: str, model: str, max_tokens: int = 512,
                temperature: float = 0.7, top_p: float = 0.95) -> str:
        """
        vLLM API를 통해 텍스트 생성
        
        Args:
            prompt: 입력 프롬프트
            model: 모델명 (vLLM에 등록된 모델)
            max_tokens: 최대 토큰 수
            temperature: 창의성 (0.0 ~ 2.0)
            top_p: Top-p 샘플링 값
        
        Returns:
            생성된 텍스트
        
        Raises:
            Exception: API 호출 실패
        """
        request_payload = {
            "model": model,
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0,
        }
        
        endpoint = f"{self.api_url}/completions"
        
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"vLLM 요청 시도 {attempt + 1}/{self.max_retries}: {model}")
                
                response = self.session.post(
                    endpoint,
                    json=request_payload,
                    timeout=self.timeout
                )
                
                response.raise_for_status()
                
                result = response.json()
                
                # vLLM 응답 형식에서 텍스트 추출
                if 'choices' in result and len(result['choices']) > 0:
                    generated_text = result['choices'][0].get('text', '').strip()
                    logger.info(f"vLLM 응답 성공: {model}")
                    return generated_text
                else:
                    raise ValueError("예상하지 않은 응답 형식")
            
            except requests.exceptions.Timeout:
                logger.warning(f"요청 타임아웃 (시도 {attempt + 1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
            
            except requests.exceptions.ConnectionError:
                logger.warning(f"연결 오류 (시도 {attempt + 1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
            
            except Exception as e:
                logger.error(f"vLLM API 오류: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    raise
        
        raise RuntimeError(f"vLLM API 호출 실패 (최대 시도: {self.max_retries})")
    
    def check_connection(self) -> bool:
        """vLLM 서버 연결 확인"""
        try:
            response = self.session.get(
                f"{self.api_url}/models",
                timeout=self.timeout
            )
            response.raise_for_status()
            logger.info("vLLM 서버 연결 성공")
            return True
        except Exception as e:
            logger.error(f"vLLM 서버 연결 실패: {e}")
            return False


class LLMClientFactory:
    """LLM 클라이언트 팩토리"""
    
    @staticmethod
    def create_client(test_mode: bool = True, api_url: str = None, 
                     timeout: int = 30) -> LLMClientBase:
        """
        LLM 클라이언트 생성
        
        Args:
            test_mode: True면 더미 클라이언트, False면 실제 vLLM 클라이언트
            api_url: vLLM API 엔드포인트 (test_mode=False일 때 필수)
            timeout: 요청 타임아웃
        
        Returns:
            LLM 클라이언트 인스턴스
        """
        if test_mode:
            logger.info("더미 LLM 클라이언트 생성")
            return DummyLLMClient()
        else:
            if not api_url:
                raise ValueError("test_mode=False일 때 api_url은 필수입니다")
            logger.info(f"실제 vLLM 클라이언트 생성: {api_url}")
            return VLLMClient(api_url, timeout)
