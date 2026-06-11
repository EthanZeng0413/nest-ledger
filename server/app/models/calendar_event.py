"""日历事件模型"""

from beanie import Document
from pydantic import Field
from datetime import datetime


class CalendarEvent(Document):
    """日历事件"""

    family_id: str
    user_id: str  # 事件创建者
    title: str
    start_time: str  # ISO 格式 datetime
    end_time: str = ""  # 可选结束时间
    repeat_type: str = "none"  # "none" | "daily" | "weekly" | "monthly"
    repeat_day: int = 0  # 重复日（每周几或每月几号，0 表示不适用）
    note: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "calendar_events"
