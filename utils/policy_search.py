from scipy.spatial.distance import cosine
from sqlalchemy.orm import Session
from data.models import Policy
from utils.embedding import get_embedding

import json
def cosine_similarity(v1: list[float], v2) -> float:
    """
    두 벡터의 코사인 유사도를 계산.
    """
    if isinstance(v2, str):
        v2 = json.loads(v2)
    return 1 - cosine(v1, v2)

def get_policy_context(query: str) -> str:
    """
    향후 DB 또는 정책 문서 요약에서 질의와 관련된 내용을 불러오는 함수
    현재는 더미 텍스트 반환
    """
    return "예시 정책 문서 내용 요약입니다."

def search_policy(db: Session, query: str) -> list:
    query_embedding = get_embedding(query)
    polices = db.query(Policy).filter(Policy.embedding != None).all()

    # 유사도 계산 및 결과 정렬
    ranked = []

    for policy in polices:
        score = cosine_similarity(query_embedding, policy.embedding)
        ranked.append((score, policy))

    ranked.sort(key=lambda x: x[0], reverse=True)

    results = [{
        "id": p.id,
        "title": p.title,
        "summary": p.summary,
        "url": p.url
    } for score, p in ranked[:10]] # 상위 5개만 반환

    return {"query": query, "results": results}