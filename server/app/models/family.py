"""家庭模型"""

from beanie import Document, Indexed
from pydantic import Field
from datetime import datetime


class FamilyMember:
    """家庭成员（嵌套在 Family 中）"""

    def __init__(self, user_id: str, nickname: str, avatar_url: str, role: str):
        self.user_id = user_id
        self.nickname = nickname
        self.avatar_url = avatar_url
        self.role = role  # "creator" | "member"
        self.joined_at = datetime.utcnow()


class Family(Document):
    """家庭"""

    name: str
    invite_code: Indexed(str, unique=True)  # type: ignore
    creator_id: str
    members: list[dict] = Field(default_factory=list)  # [{user_id, nickname, avatar_url, role, joined_at}]
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "families"
