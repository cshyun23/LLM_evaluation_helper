"""
테스트 데이터 생성 스크립트
"""

import pandas as pd
from pathlib import Path

# 데이터 디렉토리
data_dir = Path("data")
data_dir.mkdir(exist_ok=True)

# 테스트 데이터 1: 일반 QA
data1 = {
    'id': [1, 2, 3, 4, 5],
    'question': [
        'Python이란 무엇인가?',
        'JavaScript의 용도는?',
        'FastAPI의 장점은?',
        '머신러닝이란 무엇인가?',
        'Docker는 무엇인가?'
    ],
    'category': ['Programming', 'Programming', 'Framework', 'AI', 'DevOps']
}

# 테스트 데이터 2: 문장 분류
data2 = {
    'id': [1, 2, 3, 4, 5],
    'text': [
        '오늘 날씨가 정말 좋네요.',
        '이 상품은 품질이 별로입니다.',
        '매우 만족합니다.',
        '배송이 너무 느립니다.',
        '가격이 합리적입니다.'
    ],
    'sentiment': ['positive', 'negative', 'positive', 'negative', 'positive']
}

# 테스트 데이터 3: 요약
data3 = {
    'id': [1, 2, 3],
    'content': [
        '인공지능은 현대 사회에서 가장 중요한 기술 중 하나입니다. 머신러닝, 딥러닝 등 다양한 분야에서 활용되고 있으며, 앞으로 더욱 발전할 것으로 예상됩니다.',
        '파이썬은 간결한 문법과 풍부한 라이브러리로 인해 데이터 과학, 웹 개발, 자동화 등 다양한 분야에서 널리 사용되고 있습니다.',
        'FastAPI는 빠른 성능, 자동 API 문서 생성, 타입 힌트 지원 등의 특징을 가진 현대적인 웹 프레임워크입니다.'
    ]
}

# Excel 파일로 저장
output_file = data_dir / "test_data.xlsx"

with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
    pd.DataFrame(data1).to_excel(writer, sheet_name='QA', index=False)
    pd.DataFrame(data2).to_excel(writer, sheet_name='Sentiment', index=False)
    pd.DataFrame(data3).to_excel(writer, sheet_name='Summary', index=False)

print(f"✅ 테스트 데이터 생성: {output_file}")

# CSV로도 저장
csv_file = data_dir / "test_data.csv"
pd.DataFrame(data1).to_csv(csv_file, index=False, encoding='utf-8-sig')
print(f"✅ CSV 데이터 생성: {csv_file}")

print("\n생성된 파일:")
print(f"  - {output_file} (3개 시트: QA, Sentiment, Summary)")
print(f"  - {csv_file}")
