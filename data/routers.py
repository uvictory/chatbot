#FastAPI 라우터

from fastapi import Query, FastAPI, HTTPException, WebSocket, APIRouter, Depends
from json import JSONEncoder
from sqlalchemy.orm import Session, load_only
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

from data.database import SessionLocal
from data import crud, schemas
from data.models import Policy, QuestionDetail

from utils.embedding import get_embedding
from utils.policy_search import cosine_similarity

router = APIRouter()


# 의존성 주입을 통해 DB 세션을 얻는 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post(
    "/users",
    summary="사용자 생성",
    description="클라이언트에서 전송한 token 기반으로 사용자 정보를 생성합니다."
)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.get_or_create_user(db, user.token)

@router.post(
    "/questions",
    summary="질문 생성",
    description="토큰 기반으로 사용자 식별 후,일반 질문 또는 정책 질문을 생성하고 GPT 응답을 함께 저장."
)
def create_question(data: schemas.QuestionCreate, db: Session = Depends(get_db)):
    """
    클라에서 전달된 token 기반으로 사용자 조회 또는 생성
    질문 내용과 선택적으로 정책 ID 받아 GPT에게 질문 던짐
    응답과 함께 질문과답변을 db에 저장, 저장된 정보를 클라에게 리턴
    """
    #1. 토큰 기반 사용자 식별 ( 기존 사용자면 조회, 없으면 생성)
    user = crud.get_or_create_user(db, data.token)

    #2. 질문 저장 및 GPT 응답 저장
    q, detail = crud.create_question(db, user.id, data.question, policy_id=data.policyId)

    #3. 클라에게 결과 리턴
    return {
        "questionId": q.id,
        "summary": q.summary,
        "detail": {
            "questionDetailId": detail.id,
            "question": detail.question,
            "answer": detail.answer
        }
    }

@router.post("/questions/follow-up/{questionId}", summary="후속 질문 (문맥 유지, 토큰 기반)")
def follow_up(questionId: int, data: schemas.FollowUpContextCreate, db: Session = Depends(get_db)):
    try:
        detail = crud.create_follow_up(
            db=db,
            token=data.token,
            question_id=questionId,
            question_text=data.question
        )
        return {
            "questionId": questionId,
            "summary": f"후속질문: {data.question[:50]}",
            "detail": {
                "questionDetailId": detail.id,
                "question": detail.question,
                "answer": detail.answer
            }
        }
    except Exception as e:
        print(f"[후속 질문 오류] {e}")
        raise HTTPException(status_code=500, detail="후속 질문 처리 중 오류가 발생했습니다.")


@router.get("/policies")
def get_policy(query: Optional[str] = None, db: Session = Depends(get_db)):
    if query:
        query_embedding = get_embedding(query)

        # DB에서 임베딩이 존재하는 정책들 조회
        polices = db.query(Policy).filter(Policy.embedding != None).all()

        # 유사도 계산 및 결과 정렬
        ranked = []

        for policy in polices:
            score = cosine_similarity(query_embedding, policy.embedding)
            ranked.append((score, policy))

        ranked.sort(key=lambda x: x[0], reverse=True)   # 유사도 높은 순 정렬

        results = [p for score, p in ranked[:8]] 
    else:
        results = db.query(Policy) \
        .filter(Policy.is_delete.is_(False)) \
        .options(
            load_only(
                Policy.id, Policy.title, Policy.summary, Policy.agency, Policy.contact,
                Policy.url, Policy.key, Policy.created_at, Policy.updated_at, Policy.is_delete
            )
        ).all()

    return results

    
@router.get("/policies/search")
def search_policy_by_text(db: Session = Depends(get_db)):
    """
    사용자의 텍스트를 벡터로 임베딩하여 정책 요약들과 비교해 유사한 정책 반환
    """

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