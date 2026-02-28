from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import create_tables
from app.routers.coach import router as coach_router
from app.routers.analyze import router as analyze_router
from app.routers.guardian import router as guardian_router
from app.routers.auth import router as auth_router

app = FastAPI(
    title="스미싱 예방 코치 API",
    description="고령층 사기 예방 서비스 백엔드 – OCR/QR/BERT/URL분석/RAG 파이프라인",
    version="0.2.0",
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5000",
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(coach_router)
app.include_router(analyze_router)
app.include_router(guardian_router)
app.include_router(auth_router)


@app.on_event("startup")
async def init_tables() -> None:
    await create_tables()


@app.get("/")
def root():
    return {"message": "스미싱 예방 코치 API v0.2.0"}


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "version": "0.2.0",
        "services": {
            "ocr": "active (simulation)",
            "qr_decoder": "active (simulation)",
            "bert_classifier": "active (simulation)",
            "safe_browsing": "active (simulation)",
            "ml_url_scorer": "active (simulation)",
            "rag_generator": "active",
            "pipeline": "active",
            "guardian_mode": "active",
        },
    }
