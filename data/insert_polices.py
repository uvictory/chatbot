import pandas as pd
from pymongo import MongoClient
from datetime import datetime

#CSV 파일 경로
csv_path = "bokjiro_임신출산.csv"
df = pd.read_csv(csv_path, encoding="utf-8-sig")

# MongoDB 연결
client = MongoClient("mongodb://localhost:27017/")
db = client["welfare"]
collection = db["policies"]

# 변환 함수
def convert_row_to_policy(row):
    now = datetime.utcnow()
    return {
        "_id": str(row["id"]),
        "title": str(row["title"]) if not pd.isna(row["title"]) else "",
        "summary": str(row["summary"]) if not pd.isna(row["summary"]) else "",
        "url": str(row["detail_url"]) if not pd.isna(row["detail_url"]) else "",
        "isDelete": False,
        "createdAt": now,
        "updatedAt": now,
        "labels": ["임신·출산"],
        "images": [],
        "files": [],
        "faqs": [],
        "extraInfo": str(row["contact"]) if not pd.isna(row["contact"]) else None
    }

# MongoDB에 삽입
documents = [convert_row_to_policy(row) for _, row in df.iterrows()]
inserted = collection.insert_many(documents)

print(f"✅ 저장 완료: {len(inserted.inserted_ids)}개 정책이 추가되었습니다.")