from fastapi import FastAPI
from models import Base
from database import engine
from routers import router

app = FastAPI()
app.include_router(router, prefix="/api")

# DB 테이블 자동 생성
Base.metadata.create_all(bind=engine)