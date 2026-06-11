"""用户模型"""

from beanie import Document, Indexed
from pydantic import Field
from datetime import datetime


class User(Document):
    """微信小程序用户"""

    openid: Indexed(str, unique=True)  # type: ignore
    nickname: str = ""
    avatar_url: str = ""
    family_id: str | None = None  # 当前所属家庭
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"
