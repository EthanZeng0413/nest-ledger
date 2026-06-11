"""nest-ledger FastAPI 应用入口"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import MONGODB_URL, MONGODB_DB_NAME
from app.services.database import init_db, close_db
from app.api.auth import router as auth_router
from app.api.family import router as family_router
from app.api.transaction import router as transaction_router
from app.api.calendar import router as calendar_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时连接数据库，关闭时断开"""
    await init_db(MONGODB_URL, MONGODB_DB_NAME)
    yield
    await close_db()


app = FastAPI(
    title="nest-ledger API",
    description="窝记 — 家庭共享记账与日历小程序后端",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS（小程序请求）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth_router)
app.include_router(family_router)
app.include_router(transaction_router)
app.include_router(calendar_router)


@app.get("/api/v1/health")
async def health_check():
    """健康检查接口"""
    return {"status": "ok", "version": "0.1.0"}
