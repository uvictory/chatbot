# schemas.py (Pydantic 모델 정의 + 상세 주석 추가)

from pydantic import BaseModel
from typing import Optional
"""token으로 받아서 user id 생성"""
"""사용자 요청 모델"""
class UserCreate(BaseModel):
    token: str

""" 질문 생성 요청 모델( 일반 질문 )"""
class QuestionCreate(BaseModel):
    token: str # userId -> token으로 수정
    question: str # 질문 텍스트
    policyId: Optional[int] = None # <- 선택적 필드로 통합


"""후속 질문 요청 모델"""
class FollowUpContextCreate(BaseModel):
    token: str
    question: str

