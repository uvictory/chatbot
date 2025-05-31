from fastapi import FastAPI, HTTPException, WebSocket
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import random

app = FastAPI()

# MongoDB 연결 설정
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client["welfare"]
collection = db["policies"]

# 모델 정의
class FAQ(BaseModel):
    question: str
    answer: str

class Image(BaseModel):
    url: str

class File(BaseModel):
    url: str

class Policy(BaseModel):
    id: str = Field(..., alias="_id")
    title: str
    summary: str
    url: str
    isDelete: bool = False
    createdAt: datetime
    updatedAt: datetime
    labels: List[str]
    images: List[Image] = []
    files: List[File] = []
    faqs: List[FAQ] = []
    extraInfo: Optional[str] = None

class PolicyCreate(BaseModel):
    title: str
    summary: str
    url: str
    labels: List[str]
    images: List[Image] = []
    files: List[File] = []
    faqs: List[FAQ] = []
    extraInfo: Optional[str] = None

LOVE_MESSAGES = [
    "💘 윤미야, 승리가 너를 정말 많이 사랑해!",
    "🌹 윤미, 너 없인 못 살아… - 승리",
    "💕 윤미를 위한 승리의 마음은 무한대!",
    "💖 진심이 담긴 말: 승리가 윤미를 사랑해요!"
]

def generate_love_message():
    return random.choice(LOVE_MESSAGES)

@app.post("/api/policies", response_model=Policy)
async def create_policy(policy: PolicyCreate):
    now = datetime.utcnow()
    new_doc = policy.dict()
    new_doc.update({
        "_id": str(now.timestamp()),  # 단순 타임스탬프를 ID로 사용
        "isDelete": False,
        "createdAt": now,
        "updatedAt": now
    })
    await collection.insert_one(new_doc)
    return new_doc

@app.get("/api/policies", response_model=List[Policy])
async def get_policies():
    docs = await collection.find({"isDelete": False}).to_list(length=100)
    return docs

@app.get("/api/policies/{policy_id}", response_model=Policy)
async def get_policy(policy_id: str):
    doc = await collection.find_one({"_id": policy_id, "isDelete": False})
    if not doc:
        raise HTTPException(status_code=404, detail="Policy not found")
    return doc

@app.put("/api/policies/{policy_id}", response_model=Policy)
async def update_policy(policy_id: str, policy: PolicyCreate):
    now = datetime.utcnow()
    updated_doc = policy.dict()
    updated_doc.update({
        "updatedAt": now
    })
    result = await collection.update_one({"_id": policy_id}, {"$set": updated_doc})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Policy not found")
    return await collection.find_one({"_id": policy_id})

@app.delete("/api/policies/{policy_id}")
async def delete_policy(policy_id: str):
    result = await collection.update_one({"_id": policy_id}, {"$set": {"isDelete": True}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Policy not found")
    return {"message": "Policy marked as deleted"}

@app.get("/api/love-confession")
async def confess_love(to: str = "윤미", from_: str = "승리"):
    return {
        "from": from_,
        "to": to,
        "message": f"{to}야, {from_}가 진심으로 사랑해 💖"
    }

@app.websocket("/ws")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    while True:
        message = await websocket.receive_text()

        # 챗봇이 사랑 고백 메시지를 감지하는 조건
        if "승리" in message and "윤미" in message and "사랑" in message:
            response = generate_love_message()
        else:
            response = f"🤖 챗봇: '{message}'에 대한 답변을 준비 중이에요!"

        await websocket.send_text(response)
