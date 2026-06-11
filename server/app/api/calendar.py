"""日历事件 API"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from app.api.deps import get_current_user
from app.models.user import User
from app.models.calendar_event import CalendarEvent

router = APIRouter(prefix="/api/v1/event", tags=["日历"])


# ---------- 请求/响应模型 ----------

class CreateEventRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=50)
    start_time: str = Field(..., min_length=1)  # ISO datetime
    end_time: str = ""
    repeat_type: str = "none"  # "none" | "daily" | "weekly" | "monthly"
    repeat_day: int = 0  # 周几(1-7)或几号(1-31)
    note: str = ""


class UpdateEventRequest(BaseModel):
    title: str | None = None
    start_time: str | None = None
    end_time: str | None = None
    repeat_type: str | None = None
    repeat_day: int | None = None
    note: str | None = None


class EventItem(BaseModel):
    id: str
    title: str
    start_time: str
    end_time: str
    repeat_type: str
    repeat_day: int
    note: str
    user_id: str
    nickname: str
    is_mine: bool


class EventListResponse(BaseModel):
    month: str
    events: list[EventItem]


class DeleteResponse(BaseModel):
    message: str


# ---------- API 端点 ----------

@router.post("/create", response_model=EventItem)
async def create_event(req: CreateEventRequest, user: User = Depends(get_current_user)):
    """创建日历事件"""
    if not user.family_id:
        raise HTTPException(status_code=400, detail="请先加入家庭")

    # 校验重复规则
    valid_repeat = {"none", "daily", "weekly", "monthly"}
    if req.repeat_type not in valid_repeat:
        raise HTTPException(
            status_code=400, detail=f"无效的重复类型，可选: {valid_repeat}"
        )

    event = CalendarEvent(
        family_id=user.family_id,
        user_id=str(user.id),
        title=req.title,
        start_time=req.start_time,
        end_time=req.end_time,
        repeat_type=req.repeat_type,
        repeat_day=req.repeat_day,
        note=req.note,
    )
    await event.insert()

    return EventItem(
        id=str(event.id),
        title=event.title,
        start_time=event.start_time,
        end_time=event.end_time,
        repeat_type=event.repeat_type,
        repeat_day=event.repeat_day,
        note=event.note,
        user_id=str(user.id),
        nickname=user.nickname,
        is_mine=True,
    )


@router.get("/list", response_model=EventListResponse)
async def list_events(
    month: str = Query(..., min_length=7, max_length=7),  # YYYY-MM
    user: User = Depends(get_current_user),
):
    """按月查询日历事件（含重复事件）"""
    if not user.family_id:
        raise HTTPException(status_code=400, detail="请先加入家庭")

    month_start = f"{month}-01"
    # 简单计算月末
    year, m = map(int, month.split("-"))
    if m == 12:
        month_end = f"{year + 1}-01-01"
    else:
        month_end = f"{year}-{m + 1:02d}-01"

    # 查询该月内的一次性事件 + 所有重复事件（开始时间在该月之前或之内）
    events = await CalendarEvent.find(
        CalendarEvent.family_id == user.family_id,
    ).to_list()

    # 过滤：一次性事件必须在当月的日期范围内
    # 重复事件：开始时间在 month_end 之前
    result = []
    for e in events:
        if e.repeat_type == "none":
            if month_start <= e.start_time[:10] < month_end:
                result.append(e)
        else:
            if e.start_time[:10] < month_end:
                result.append(e)

    # 获取用户昵称
    user_ids = list(set(e.user_id for e in result))
    nickname_map = {}
    for uid in user_ids:
        u = await User.get(uid)
        if u:
            nickname_map[uid] = u.nickname

    return EventListResponse(
        month=month,
        events=[
            EventItem(
                id=str(e.id),
                title=e.title,
                start_time=e.start_time,
                end_time=e.end_time,
                repeat_type=e.repeat_type,
                repeat_day=e.repeat_day,
                note=e.note,
                user_id=e.user_id,
                nickname=nickname_map.get(e.user_id, "未知"),
                is_mine=e.user_id == str(user.id),
            )
            for e in result
        ],
    )


@router.put("/{event_id}", response_model=EventItem)
async def update_event(
    event_id: str,
    req: UpdateEventRequest,
    user: User = Depends(get_current_user),
):
    """编辑日历事件（仅创建者）"""
    event = await CalendarEvent.get(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="事件不存在")

    if event.user_id != str(user.id):
        raise HTTPException(status_code=403, detail="只能编辑自己创建的事件")

    # 更新非空字段
    update_data = req.model_dump(exclude_none=True)
    for field, value in update_data.items():
        setattr(event, field, value)

    await event.save()

    return EventItem(
        id=str(event.id),
        title=event.title,
        start_time=event.start_time,
        end_time=event.end_time,
        repeat_type=event.repeat_type,
        repeat_day=event.repeat_day,
        note=event.note,
        user_id=str(user.id),
        nickname=user.nickname,
        is_mine=True,
    )


@router.delete("/{event_id}", response_model=DeleteResponse)
async def delete_event(event_id: str, user: User = Depends(get_current_user)):
    """删除日历事件（仅创建者）"""
    event = await CalendarEvent.get(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="事件不存在")

    if event.user_id != str(user.id):
        raise HTTPException(status_code=403, detail="只能删除自己创建的事件")

    await event.delete()
    return DeleteResponse(message="已删除")
