# Pydantic 모델
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from db.test import File


class FAQ(BaseModel):
    question: str
    answer: str

class Image(BaseModel):
    url: str

class File(BaseModel):
    url: str

class PolicyBase(BaseModel):
    title: str
    summary: str
    labels: List[str]
    images: List[Image] = []
    files: List[File] = []
    faqs: List[FAQ] = []
    extraInfo: Optional[str] = None

class PolicyCreate(PolicyBase):
    pass

class Policy(PolicyBase):
    id: str
    createdAt : datetime
    updatedAt : datetime
    isDelete : bool

class ExtraInfo(BaseModel):
    id: str
    policy_id: str
    content: str
