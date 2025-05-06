#FastAPI 라우터
from json import JSONEncoder

from fastapi import Query, FastAPI, HTTPException, WebSocket, APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

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
    createdAt: datetime
    updatedAt: datetime
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
