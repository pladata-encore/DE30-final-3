import logging
from fastapi import FastAPI
from app.api.v1.endpoints.run_module import router as run_router
import uvicorn

# 로거 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# 라우터 등록
app.include_router(run_router, prefix="/api/v1")

@app.get("/")
def read_root():
    logger.info("Root endpoint was called")
    return {"Hello": "World"}

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down...")

if __name__ == "__main__":
    uvicorn.run(app, host="10.11.10.180", port=8000)
