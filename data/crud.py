# crud.py
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import User, Question, QuestionDetail
from datetime import datetime
from typing import Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gpt.gpt_service import ask_gpt, ask_gpt_with_history
from models import Policy

engine = create_engine("sqlite:///./welfare.db", connect_args={"check_same_thread": False})

# 사용자 생성 함수
def get_or_create_user(db: Session, token: str) -> User:
    """
    주어진 token으로 새 사용자를 생성하고 DB에 저장, 이미 있는 사용자인지 체크
    """
    user = db.query(User).filter(User.token == token).first()
    if user:
        return user
    user = User(token=token)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# 질문 ( 일반 또는 정책 기반) 생성 함수
# policy_id가 None이면 일반 질문, 값이 있으면 정책 기반 질문으로 처리

def create_question(db: Session,
                    userId: int,
                    question: str,
                    policy_id: Optional[int] = None
                    ):
    """
    사용자의 질문을 저장하고, 이에 대한 응답(모의 GPT 응답) 을 생성하여
    Question 및 QuestionDetail 테이블에 함께 저장.
    """
    # 질문 요약 생성 (단순 요약으로 10글자 제한하여 사용)
    summary = question[:50] + "..." if len(question) > 50 else question

    context = None
    if policy_id:   # 정책 기반 질문인 경우
        policy = db.query(Policy).filter(Policy.id == policy_id).first()
        if policy:
            context = policy.summary # 또는 policy.description 등
            print(f"context: {context}")
        else:
            context = None

    answer = ask_gpt(question, context)

    # 질문 저장
    q = Question(
        userId=userId,
        policyId=policy_id,
        summary=summary,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(q)
    db.commit()
    db.refresh(q)


    # 질문 상세 저장
    detail = QuestionDetail(
        questionId=q.id,
        question=question,
        answer=answer,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(detail)
    db.commit()
    db.refresh(detail)

    print(f"[DB 저장] 질문: {question}, 답변: {answer}")

    return q, detail

    # 후속 질문 추가 함수
def create_follow_up(db: Session, token: str, question_id: int, question_text: str) -> QuestionDetail:
    #1. 토큰으로 사용자 조회
    user = db.query(User).filter(User.token == token).first()
    if not user:
        raise ValueError("해당 토큰의 사용자를 찾을 수 없습니다.")

    #2. 기존 질문 이력 가져오기
    prev_details = db.query(QuestionDetail)\
                     .filter(QuestionDetail.questionId == question_id)\
                     .order_by(QuestionDetail.created_at.asc())\
                     .all()

    history = []
    for detail in prev_details:
        history.append({"role": "user", "content": detail.question})
        history.append({"role": "assistant", "content": detail.answer})

    # 3. GPT 호출
    answer = ask_gpt_with_history(history, question_text)

    # 4. 후속 질문 저장
    detail = QuestionDetail(
        questionId=question_id,
        question=question_text,
        answer=answer,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(detail)
    db.commit()
    db.refresh(detail)

    return detail

