"""
통합 테스트 스크립트
모든 모듈이 제대로 작동하는지 확인합니다. (더미 모드)
"""

import logging
import sys
from pathlib import Path

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 로컬 모듈 임포트
from src.config_loader import ConfigManager
from src.data_manager import DataManager
from src.llm_client import LLMClientFactory
from src.inference_engine import InferenceEngine


def test_config_loader():
    """설정 로더 테스트"""
    print("\n" + "="*60)
    print("1️⃣  설정 로더 테스트")
    print("="*60)
    
    try:
        config = ConfigManager("config/config.yaml")
        
        print(f"✅ 설정 파일 로드 성공")
        
        # 모델 목록
        models = config.list_model_names()
        print(f"✅ 모델 목록: {models}")
        
        # 프롬프트 템플릿
        prompts = config.list_prompt_names()
        print(f"✅ 프롬프트 템플릿: {prompts}")
        
        # vLLM 설정
        vllm_config = config.get_vllm_config()
        print(f"✅ vLLM 테스트 모드: {vllm_config.test_mode}")
        print(f"✅ vLLM API URL: {vllm_config.api_url}")
        
        # 서버 설정
        server_config = config.get_server_config()
        print(f"✅ 서버 주소: {server_config.host}:{server_config.port}")
        
        return True
    except Exception as e:
        print(f"❌ 설정 로더 테스트 실패: {e}")
        return False


def test_data_manager():
    """데이터 매니저 테스트"""
    print("\n" + "="*60)
    print("2️⃣  데이터 매니저 테스트")
    print("="*60)
    
    try:
        config = ConfigManager("config/config.yaml")
        data_config = config.get_data_config()
        
        data_manager = DataManager(
            input_dir=data_config.input_dir,
            output_dir=data_config.output_dir,
            backup_dir=data_config.backup_dir
        )
        
        # 파일 목록
        files = data_manager.list_files()
        print(f"✅ 파일 목록: {files}")
        
        if files:
            file_name = files[0]
            
            # 시트 목록
            sheets = data_manager.get_sheets(file_name)
            print(f"✅ 시트 목록 ({file_name}): {sheets}")
            
            # 데이터 읽기
            if sheets:
                sheet_name = sheets[0]
                df, columns = data_manager.read_sheet(file_name, sheet_name)
                print(f"✅ 데이터 읽기 성공: {sheet_name}")
                print(f"   - 행 수: {len(df)}")
                print(f"   - 컬럼: {columns}")
                print(f"   - 데이터 미리보기:")
                print(df.head(2).to_string(index=False))
            
            # 파일 정보
            info = data_manager.get_file_info(file_name)
            print(f"✅ 파일 정보 조회 성공")
            print(f"   - 파일명: {info['file_name']}")
            print(f"   - 파일 크기: {info['file_size']} bytes")
            print(f"   - 시트 수: {info['sheet_count']}")
        
        return True
    except Exception as e:
        print(f"❌ 데이터 매니저 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_llm_client():
    """LLM 클라이언트 테스트"""
    print("\n" + "="*60)
    print("3️⃣  LLM 클라이언트 테스트 (더미 모드)")
    print("="*60)
    
    try:
        # 더미 클라이언트 생성
        client = LLMClientFactory.create_client(test_mode=True)
        
        print(f"✅ 더미 LLM 클라이언트 생성 성공")
        
        # 더미 응답 생성
        prompts = [
            "Python이란 무엇인가?",
            "JavaScript의 용도는?",
            "FastAPI의 장점은?"
        ]
        
        for prompt in prompts:
            response = client.generate(
                prompt=prompt,
                model="dummy-model",
                max_tokens=512
            )
            print(f"✅ 응답 생성 성공: '{prompt[:30]}...'")
            print(f"   응답: {response[:80]}...")
        
        if hasattr(client, 'get_call_count'):
            print(f"✅ 총 호출 횟수: {client.get_call_count()}")
        
        return True
    except Exception as e:
        print(f"❌ LLM 클라이언트 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_inference_engine():
    """추론 엔진 테스트"""
    print("\n" + "="*60)
    print("4️⃣  추론 엔진 테스트")
    print("="*60)
    
    try:
        config = ConfigManager("config/config.yaml")
        llm_client = LLMClientFactory.create_client(test_mode=True)
        
        inference_engine = InferenceEngine(llm_client, config)
        
        print(f"✅ 추론 엔진 초기화 성공")
        
        # 단일 추론
        result = inference_engine.infer(
            input_text="Python이란 무엇인가?",
            model="model_1",
            template="template_1"
        )
        
        print(f"✅ 단일 추론 성공")
        print(f"   - 상태: {result.status}")
        print(f"   - 입력: {result.input_text}")
        print(f"   - 출력: {result.output_text[:80]}...")
        print(f"   - 모델: {result.model}")
        print(f"   - 템플릿: {result.template}")
        
        # 배치 추론
        config_obj = ConfigManager("config/config.yaml")
        data_config = config_obj.get_data_config()
        data_manager = DataManager(
            input_dir=data_config.input_dir,
            output_dir=data_config.output_dir
        )
        
        files = data_manager.list_files()
        if files:
            file_name = files[0]
            sheets = data_manager.get_sheets(file_name)
            
            if sheets:
                sheet_name = sheets[0]
                df, columns = data_manager.read_sheet(file_name, sheet_name)
                
                if 'question' in columns:
                    print(f"\n배치 추론 수행 중...")
                    result_df = inference_engine.infer_batch(
                        data=df,
                        input_column='question',
                        output_column='answer',
                        model='model_1',
                        template='template_1'
                    )
                    
                    print(f"✅ 배치 추론 성공")
                    print(f"   - 처리된 행: {len(result_df)}")
                    print(f"   - 컬럼: {list(result_df.columns)}")
                    print(f"   - 결과 미리보기:")
                    print(result_df[['question', 'answer']].head(2).to_string(index=False))
        
        return True
    except Exception as e:
        print(f"❌ 추론 엔진 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """메인 테스트 함수"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  LLM Evaluation Helper - 통합 테스트 (더미 모드)".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    results = []
    
    # 각 테스트 실행
    results.append(("설정 로더", test_config_loader()))
    results.append(("데이터 매니저", test_data_manager()))
    results.append(("LLM 클라이언트", test_llm_client()))
    results.append(("추론 엔진", test_inference_engine()))
    
    # 결과 요약
    print("\n" + "="*60)
    print("📊 테스트 결과 요약")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\n총 {passed}/{total} 테스트 통과")
    
    if passed == total:
        print("\n🎉 모든 테스트 통과! 서버를 시작할 준비가 되었습니다.")
        print("\n서버 시작 명령:")
        print("  python main.py")
        return 0
    else:
        print("\n⚠️  일부 테스트가 실패했습니다. 위 오류를 확인하세요.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
