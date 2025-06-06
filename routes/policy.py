from flask import Blueprint, request, jsonify
from utils.policy_search import search_policy
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from data.routers import get_db
from utils.embedding import get_embedding
from utils.policy_search import cosine_similarity
from data.models import Policy
from pydantic import BaseModel

# Blueprint 생성: /policy/search API 담당
#policy_bp = Blueprint("policy", __name__)

router = APIRouter(prefix ="/api/policies", tags=["policies"])

# 요청 바디 구조 정의 (pydantic 모델)
class PolicySearchRequest(BaseModel):
    query: str # 사용자 질의어를 JSON body에서 받기 위함

# 정책 벡터 검색 API
@router.post("/search")
def search_policy_by_text(payload: PolicySearchRequest, db: Session = Depends(get_db)):
    """
    사용자의 텍스트를 벡터로 임베딩하여 정책 요약들과 비교해 유사한 정책 반환
    """
    # 사용자 쿼리 추출
    query = payload.query

    # 사용자 쿼리를 임베딩 벡터로 변환
    query_embedding = get_embedding(query)

    # DB에서 임베딩이 존재하는 정책들 조회
    polices = db.query(Policy).filter(Policy.embedding != None).all()

    # 유사도 계산 및 결과 정렬
    ranked = []

    for policy in polices:
        score = cosine_similarity(query_embedding, policy.embedding)
        ranked.append((score, policy))

    ranked.sort(key=lambda x: x[0], reverse=True)   # 유사도 높은 순 정렬

    # 상위 5개 정책을 응답 구조로 구성
    results = [{
        "id": p.id,
        "title": p.title,
        "summary": p.summary
    } for score, p in ranked[:5]] # 상위 5개만 반환

    return {"query": query, "results": results}
