#FastAPI 실행용 진입점

import uvicorn
from fastapi import FastAPI
from data.routers import router as policy_router

app = FastAPI()
app.include_router(policy_router)

if __name__ == "__main__":
    uvicorn.run("run_fastapi:app", host="127.0.0.1", port=8000, reload=True)
