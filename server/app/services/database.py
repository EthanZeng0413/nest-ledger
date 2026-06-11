"""MongoDB 数据库连接管理"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from beanie import init_beanie

from app.models.user import User
from app.models.family import Family
from app.models.transaction import Transaction
from app.models.calendar_event import CalendarEvent

# 全局数据库客户端
client: AsyncIOMotorClient | None = None
db: AsyncIOMotorDatabase | None = None

# 所有 Beanie 文档模型
DOCUMENT_MODELS = [User, Family, Transaction, CalendarEvent]


async def init_db(mongo_url: str, db_name: str):
    """初始化 MongoDB 连接和 Beanie ODM"""
    global client, db
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    await init_beanie(database=db, document_models=DOCUMENT_MODELS)


async def close_db():
    """关闭数据库连接"""
    global client
    if client:
        client.close()
        client = None
