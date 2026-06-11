"""收支记录模型"""

from beanie import Document
from pydantic import Field
from datetime import datetime


class Transaction(Document):
    """收支记录"""

    family_id: str
    user_id: str  # 记录创建者
    amount: float  # 金额
    category: str  # 类别（餐饮、交通、购物等）
    type: str  # "expense" | "income"
    date: str  # 日期 YYYY-MM-DD
    note: str = ""  # 备注
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "transactions"
