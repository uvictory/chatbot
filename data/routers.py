#FastAPI 라우터

from fastapi import Query, FastAPI, HTTPException, WebSocket, APIRouter, Depends
from json import JSONEncoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

from database import SessionLocal
import crud
import schemas

# ✅ Safari에서 한글 인코딩 깨짐 방지용 커스텀 응답 클래스
class UTF8JSONResponse(JSONResponse):
    media_type = "application/json; charset=utf-8"

# ✅ FastAPI 인스턴스 생성 시 기본 응답 클래스 지정
app = FastAPI(default_response_class=UTF8JSONResponse)
router = APIRouter()

# MongoDB 연결
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.welfare
policy_collection = db.policies
extra_info_collection = db.extra_info

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


# Helper to convert ObjectId to str
def fix_id(doc):
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc

# Pydantic Models
class FAQ(BaseModel):
    question: str
    answer: str

class Image(BaseModel):
    url: str

class File(BaseModel):
    url: str

class PolicyCreate(BaseModel):
    title: str
    summary: str
    url: str
    labels: List[str]
    images: List[Image] = []
    files: List[File] = []
    faqs: List[FAQ] = []
    extraInfo: Optional[str] = None

class Policy(PolicyCreate):
    id: str
    created_at: datetime
    updated_at: datetime
    isDelete: bool

class ExtraInfoCreate(BaseModel):
    info: str

class ExtraInfo(BaseModel):
    id: str
    info: str
    policy_id: str




# 정책 CRUD
@router.get("/api/policies", response_model=List[Policy])
async def get_policies():
    docs = await policy_collection.find({"isDelete": False}).to_list(100)
    return [fix_id(doc) for doc in docs]

# 정책 검색 및 필터 기능 구현
@router.get("/api/policies/search", response_model=List[Policy])
async def search_policies(
    keyword: Optional[str] = Query(None),
    label: Optional[str] = Query(None),
    agency: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100)
):
    query = {"isDelete": False}

    # 제목, 요약 키워드 포함 검색
    if keyword:
        query["$or"] = [
            {"title": {"$regex": keyword, "$options": "i"}},
            {"summary": {"$regex": keyword, "$options": "i"}}
        ]

    # 라벨 포함 필터링
    if label:
        query["labels"] = label

    # 시행기관 포함 필터링
    if agency:
        query["agency"] = {"$regex": agency, "$options": "i"}

    docs = await policy_collection.find(query).to_list(length=limit)
    return [fix_id(doc) for doc in docs] # fix_id 필요






@router.get("/api/policies/{policy_id}", response_model=Policy)
async def get_policy(policy_id: str):
    doc = await policy_collection.find_one({"_id": policy_id, "isDelete": False})
    if not doc:
        raise HTTPException(status_code=404, detail="Not found")
    """
    # 추가 정보 조회
    extra_doc = await db["extra_infos"].find_one({"policy_id": policy_id})
    if extra_doc:
        doc["extraInfo"] = extra_doc["content"]
    """
    return fix_id(doc)


@router.post("/api/policies", response_model=Policy)
async def create_policy(policy: PolicyCreate):
    now = datetime.utcnow()
    doc = policy.dict()
    doc.update({
        "_id": str(now.timestamp()),
        "createdAt": now,
        "updatedAt": now,
        "isDelete": False
    })
    await policy_collection.insert_one(doc)
    return fix_id(doc)

@router.put("/api/policies/{policy_id}", response_model=Policy)
async def update_policy(policy_id: str, policy: PolicyCreate):
    doc = policy.dict()
    doc["updatedAt"] = datetime.utcnow()
    result = await policy_collection.update_one({"_id": policy_id}, {"$set": doc})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return fix_id(await policy_collection.find_one({"_id": policy_id}))

@router.delete("/api/policies/{policy_id}")
async def delete_policy(policy_id: str):
    result = await policy_collection.update_one({"_id": policy_id}, {"$set": {"isDelete": True}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"message": "Deleted"}

# 추가정보 API
@router.get("/api/policies/{policy_id}/extra-info", response_model=List[ExtraInfo])
async def get_extra_infos(policy_id: str):
    docs = await extra_info_collection.find({"policy_id": policy_id}).to_list(100)
    return [fix_id(doc) for doc in docs]

@router.post("/api/policies/{policy_id}/extra-info", response_model=ExtraInfo)
async def create_extra_info(policy_id: str, body: ExtraInfoCreate):
    doc = {
        "info": body.info,
        "policy_id": policy_id
    }
    result = await extra_info_collection.insert_one(doc)
    doc["_id"] = result.inserted_id
    return fix_id(doc)

@router.put("/api/extra-info/{extra_info_id}", response_model=ExtraInfo)
async def update_extra_info(extra_info_id: str, body: ExtraInfoCreate):
    result = await extra_info_collection.update_one({"_id": ObjectId(extra_info_id)}, {"$set": {"info": body.info}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    doc = await extra_info_collection.find_one({"_id": ObjectId(extra_info_id)})
    return fix_id(doc)

@router.delete("/api/extra-info/{extra_info_id}")
async def delete_extra_info(extra_info_id: str):
    result = await extra_info_collection.delete_one({"_id": ObjectId(extra_info_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"message": "Deleted"}

app.include_router(router)
