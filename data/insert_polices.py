# insert_policies.py
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Policy, Base
from datetime import datetime
from utils.embedding import get_embedding # 임베딩 함수 임포트 추가
import json
import os

# 기존 DB 파일 삭제 (있는 경우)
if os.path.exists("./welfare.db"):
    os.remove("./welfare.db")

# ✅ SQLite DB 연결
engine = create_engine("sqlite:///./welfare.db", echo=True)
Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)
session = Session()

# ✅ CSV 읽기 및 NaN -> None 처리
df = pd.read_csv("bokjiro_임신출산.csv").fillna("")

# ✅ 각 행을 Policy 객체로 변환 후 DB 삽입
for _, row in df.iterrows():
    # ✅ 중복 방지
    if session.query(Policy).filter_by(id=row["id"]).first():
        continue


    policy = Policy(
        id=row['id'],
        title=row['title'],
        summary=row['summary'],
        agency=row.get('agency', '') or None,
        contact=row.get('contact', '') or None,
        url=row['detail_url'],
        key=row['key'],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        is_delete=False
    )
    session.add(policy)

# ✅ 커밋
session.commit()
print("✅ CSV 데이터 삽입 완료")

