from fastapi import FastAPI
from models import Base
from database import engine
from routers import router
from routes import policy

app = FastAPI()
app.include_router(router, prefix="/api")
app.include_router(policy.router)


# DB 테이블 자동 생성
Base.metadata.create_all(bind=engine)