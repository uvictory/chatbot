#FastAPI 실행용 진입점

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from data.models import Base
from data.database import engine
from data.routers import router

class UTF8JSONResponse(JSONResponse):
    media_type = "application/json; charset=utf-8"
    
app = FastAPI(default_response_class=UTF8JSONResponse)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    uvicorn.run("run_fastapi:app", host="0.0.0.0", port=6002, reload=True)
