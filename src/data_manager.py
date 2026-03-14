"""
데이터 처리 모듈
Excel/CSV 파일 읽기 및 쓰기 기능
"""

import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
from openpyxl import load_workbook, Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from datetime import datetime

logger = logging.getLogger(__name__)


class DataManager:
    """데이터 파일 관리 클래스"""
    
    def __init__(self, input_dir: str, output_dir: str, backup_dir: str = None):
        """
        데이터 매니저 초기화
        
        Args:
            input_dir: 입력 파일 디렉토리
            output_dir: 출력 파일 디렉토리
            backup_dir: 백업 디렉토리 (선택사항)
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.backup_dir = Path(backup_dir) if backup_dir else None
        
        # 디렉토리 생성
        self.input_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        if self.backup_dir:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def list_files(self) -> List[str]:
        """data 디렉토리의 Excel/CSV 파일 목록 반환"""
        files = []
        for ext in ['*.xlsx', '*.csv', '*.xls']:
            files.extend([f.name for f in self.input_dir.glob(ext)])
        return sorted(files)

    def list_result_files(self) -> List[str]:
        """results 디렉토리의 Excel/CSV 파일 목록 반환"""
        files = []
        for ext in ['*.xlsx', '*.csv', '*.xls']:
            files.extend([f.name for f in self.output_dir.glob(ext)])
        return sorted(files)

    def find_file_path(self, file_name: str) -> Path:
        """data 또는 results 디렉토리에서 파일 경로 반환"""
        for directory in [self.input_dir, self.output_dir]:
            p = directory / file_name
            if p.exists():
                return p
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_name}")

    def get_sheets(self, file_name: str) -> List[str]:
        """파일의 시트 목록 반환"""
        file_path = self.find_file_path(file_name)

        if not file_path.exists():
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_name}")
        
        if file_name.endswith('.csv'):
            return ['Sheet1']
        
        try:
            wb = load_workbook(file_path, data_only=True)
            return wb.sheetnames
        except Exception as e:
            logger.error(f"시트 목록 조회 실패: {e}")
            raise
    
    def read_sheet(self, file_name: str, sheet_name: str) -> Tuple[pd.DataFrame, List[str]]:
        """
        시트 데이터 읽기

        Returns:
            (데이터프레임, 컬럼 이름 리스트)
        """
        file_path = self.find_file_path(file_name)
        
        try:
            if file_name.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            # NaN 값을 None으로 변환
            df = df.where(pd.notna(df), None)
            
            columns = list(df.columns)
            logger.info(f"파일 읽기 성공: {file_name}, 시트: {sheet_name}, 행: {len(df)}, 컬럼: {len(columns)}")
            
            return df, columns
        
        except Exception as e:
            logger.error(f"파일 읽기 실패: {e}")
            raise
    
    def write_sheet(self, df: pd.DataFrame, file_name: str, sheet_name: str, 
                   output_name: Optional[str] = None) -> str:
        """
        시트 데이터 쓰기
        
        Args:
            df: 저장할 데이터프레임
            file_name: 원본 파일명
            sheet_name: 시트명
            output_name: 출력 파일명 (None이면 자동 생성)
        
        Returns:
            저장된 파일의 전체 경로
        """
        try:
            if output_name is None:
                # 자동 생성: filename_timestamp.xlsx
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                base_name = Path(file_name).stem
                output_name = f"{base_name}_output_{timestamp}.xlsx"
            
            output_path = self.output_dir / output_name
            
            # 기존 파일이 있으면 백업
            if output_path.exists() and self.backup_dir:
                backup_name = f"{output_path.stem}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                backup_path = self.backup_dir / backup_name
                output_path.rename(backup_path)
                logger.info(f"기존 파일 백업: {backup_path}")
            
            # Excel 파일로 저장
            df.to_excel(output_path, sheet_name=sheet_name, index=False)
            
            logger.info(f"파일 저장 성공: {output_path}")
            return str(output_path)
        
        except Exception as e:
            logger.error(f"파일 저장 실패: {e}")
            raise
    
    def update_cell(self, file_name: str, sheet_name: str, row_idx: int, 
                   column_name: str, value: Any) -> None:
        """특정 셀 업데이트"""
        file_path = self.input_dir / file_name
        
        try:
            df, _ = self.read_sheet(file_name, sheet_name)
            
            if column_name not in df.columns:
                raise ValueError(f"컬럼을 찾을 수 없습니다: {column_name}")
            
            df.at[row_idx, column_name] = value
            
            # 임시 저장
            self.write_sheet(df, file_name, sheet_name, f"{Path(file_name).stem}_temp.xlsx")
            
            logger.info(f"셀 업데이트: {file_name}[{sheet_name}][{row_idx},{column_name}]")
        
        except Exception as e:
            logger.error(f"셀 업데이트 실패: {e}")
            raise
    
    def get_file_info(self, file_name: str) -> Dict[str, Any]:
        """파일 정보 조회"""
        file_path = self.find_file_path(file_name)
        
        try:
            sheets = self.get_sheets(file_name)
            
            info = {
                "file_name": file_name,
                "file_path": str(file_path),
                "file_size": file_path.stat().st_size,
                "sheets": sheets,
                "sheet_count": len(sheets),
                "created_time": datetime.fromtimestamp(file_path.stat().st_ctime).isoformat(),
                "modified_time": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
            }
            
            # 각 시트의 행/컬럼 수
            sheet_details = {}
            for sheet in sheets:
                try:
                    df, cols = self.read_sheet(file_name, sheet)
                    sheet_details[sheet] = {
                        "rows": len(df),
                        "columns": len(cols),
                        "column_names": cols
                    }
                except Exception as e:
                    logger.warning(f"시트 정보 조회 실패: {sheet} - {e}")
            
            info["sheet_details"] = sheet_details
            
            return info
        
        except Exception as e:
            logger.error(f"파일 정보 조회 실패: {e}")
            raise


class ExcelWriter:
    """Excel 파일 쓰기 전문 클래스"""
    
    @staticmethod
    def write_multiple_sheets(data_dict: Dict[str, pd.DataFrame], 
                             file_path: str) -> None:
        """여러 시트를 가진 Excel 파일 작성"""
        try:
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                for sheet_name, df in data_dict.items():
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            logger.info(f"멀티 시트 Excel 파일 저장: {file_path}")
        
        except Exception as e:
            logger.error(f"Excel 파일 저장 실패: {e}")
            raise
