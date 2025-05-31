from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey, Integer
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import uuid

#from db.test import File
# 모든 ORM 모델 클래스가 상속받는 기본 클래스
Base = declarative_base()

# 정책 목록 테이블
class Policy(Base):
    __tablename__ = "policies" # 실제 DB에 생성될 테이블 이름

    id = Column(Integer, primary_key=True, index=True) # 정책 ID, 수동 입력
    title = Column(String, nullable=False) # 정책명
    summary = Column(Text, nullable=True)  # 정책 요약 (HTML 가능)
    agency = Column(String, nullable=True)
    contact = Column(String, nullable=True)
    url = Column(String, nullable=False) # 정책 URL
    key = Column(String, nullable=True) #  정책 고유 id
    created_at = Column(DateTime, default=datetime.utcnow)  # 생성일
    updated_at = Column(DateTime, default=datetime.utcnow(), onupdate=datetime.utcnow) # 수정일
    is_delete = Column(Boolean, default=False) # soft delete 여부
    #연관 테이블
    labels = relationship("Label", back_populates="policy", cascade="all, delete-orphan")
    images = relationship("Image", back_populates="policy", cascade="all, delete-orphan")
    files = relationship("File", back_populates="policy", cascade="all, delete-orphan")
    faqs = relationship("FAQ", back_populates="policy",cascade="all, delete-orphan")
    extra_infos = relationship("ExtraInfo", back_populates="policy", cascade="all, delete-orphan")
    questions = relationship("Question", back_populates="policy")

# ✅ 라벨 테이블
class Label(Base):
    __tablename__ = "labels"

    id = Column(Integer, primary_key=True, index=True) # 라벨 ID
    name = Column(String, nullable=False) # 라벨 이름 (예: "출산지원", "청년")
    policy_id = Column(Integer, ForeignKey("policies.id"), nullable=False)

    policy = relationship("Policy", back_populates="labels")

# ✅ 이미지 테이블
class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True) # 이미지 ID
    url = Column(String, nullable=False) # 이미지 URL
    policy_id = Column(Integer, ForeignKey("policies.id"), nullable=False)

    policy = relationship("Policy", back_populates="images")

# ✅ 파일 테이블
class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)  # 파일 ID
    url = Column(String, nullable=False) # 파일 URL
    policy_id = Column(String, ForeignKey("policies.id"), nullable=False)

    policy = relationship("Policy", back_populates="files")

# ✅ FAQ 테이블
class FAQ(Base):
    __tablename__ = "faqs"

    id = Column(Integer, primary_key=True, index=True)  # FAQ ID
    question = Column(String, nullable=False) # 질문
    answer = Column(String, nullable=False)
    policy_id = Column(Integer, ForeignKey("policies.id"))
    policy = relationship("Policy", back_populates="faqs")

# ✅ 추가 정보 테이블
class ExtraInfo(Base):
    __tablename__ = "extra_info"

    id = Column(Integer, primary_key=True, index=True) # 추가 정보 ID
    info = Column(Text, nullable=False) # 정보 내용 (예: 129, 1350)
    policy_id = Column(String, ForeignKey("policies.id"), nullable=False)

    policy = relationship("Policy", back_populates="extra_infos")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    idDelete = Column(Boolean, default=False)

    questions = relationship("Question", back_populates="user")

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    userId = Column(Integer, ForeignKey("users.id"))
    policyId = Column(Integer, ForeignKey("policies.id"), nullable=True)
    summary = Column(Text)
    sessionId = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    idDelete = Column(Boolean, default=False)

    user = relationship("User", back_populates="questions")
    details = relationship("QuestionDetail", back_populates="question_ref")

    #정책 테이블과 관계 정의
    policy = relationship("Policy", back_populates="questions")

class QuestionDetail(Base):
    __tablename__ = "question_details"
    id = Column(Integer, primary_key=True, index=True)
    questionId = Column(Integer, ForeignKey("questions.id"), nullable=False)
    question = Column(Text)
    answer = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    isDelete = Column(Boolean, default=False)

    question_ref = relationship("Question", back_populates="details")

