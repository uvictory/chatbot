import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Policy, Base
from utils.embedding import get_embedding
import time

# DB 연결
engine = create_engine('sqlite:///./welfare.db')
Session = sessionmaker(bind=engine)
session = Session()

# 임베딩되지 않은 정책 불러오기
policies = session.query(Policy).filter(Policy.embedding == None).all()

# title 배치 추출
titles = [p.title for p in policies]

# 배치 임베딩 수행
batch_size = 100
for i in range(0, len(titles), batch_size):
    batch_titles = titles[i:i + batch_size]
    batch_embeddings = get_embedding(batch_titles)

    # 임베딩 결과 저장
    for j, emb in enumerate(batch_embeddings):
        policies[i + j].embedding = emb

    session.commit()
    print(f"{i + len(batch_embeddings)}개 처리 완료!")

print(f" 임베딩 대상 정책 수 : {len(policies)}")

session.close()

