"""家庭管理 API"""

import random
import string

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.api.deps import get_current_user
from app.models.user import User
from app.models.family import Family

router = APIRouter(prefix="/api/v1/family", tags=["家庭"])


def _generate_invite_code() -> str:
    """生成 6 位邀请码（大写字母+数字）"""
    chars = string.ascii_uppercase + string.digits
    return "".join(random.choices(chars, k=6))


# ---------- 请求/响应模型 ----------

class CreateFamilyRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=20)


class CreateFamilyResponse(BaseModel):
    family_id: str
    name: str
    invite_code: str
    message: str


class JoinFamilyRequest(BaseModel):
    invite_code: str = Field(..., min_length=6, max_length=6)


class JoinFamilyResponse(BaseModel):
    family_id: str
    name: str
    message: str


class MemberInfo(BaseModel):
    user_id: str
    nickname: str
    avatar_url: str
    role: str
    joined_at: str


class FamilyInfoResponse(BaseModel):
    family_id: str
    name: str
    invite_code: str
    members: list[MemberInfo]
    my_role: str


class LeaveFamilyResponse(BaseModel):
    message: str


# ---------- API 端点 ----------

@router.post("/create", response_model=CreateFamilyResponse)
async def create_family(req: CreateFamilyRequest, user: User = Depends(get_current_user)):
    """创建家庭，创建者自动成为第一个成员"""
    # 检查用户是否已在家庭中
    if user.family_id:
        raise HTTPException(status_code=400, detail="你已在家庭中，请先退出当前家庭")

    # 生成唯一邀请码
    for _ in range(10):
        code = _generate_invite_code()
        existing = await Family.find_one(Family.invite_code == code)
        if not existing:
            break
    else:
        raise HTTPException(status_code=500, detail="生成邀请码失败，请重试")

    # 创建家庭
    family = Family(
        name=req.name,
        invite_code=code,
        creator_id=str(user.id),
        members=[
            {
                "user_id": str(user.id),
                "nickname": user.nickname,
                "avatar_url": user.avatar_url,
                "role": "creator",
                "joined_at": user.created_at.isoformat() if user.created_at else "",
            }
        ],
    )
    await family.insert()

    # 更新用户的 family_id
    user.family_id = str(family.id)
    await user.save()

    return CreateFamilyResponse(
        family_id=str(family.id),
        name=family.name,
        invite_code=code,
        message="家庭创建成功！将邀请码分享给家人吧",
    )


@router.post("/join", response_model=JoinFamilyResponse)
async def join_family(req: JoinFamilyRequest, user: User = Depends(get_current_user)):
    """通过邀请码加入家庭"""
    # 检查是否已在家庭中
    if user.family_id:
        raise HTTPException(status_code=400, detail="你已在家庭中，请先退出当前家庭")

    # 查找家庭
    family = await Family.find_one(Family.invite_code == req.invite_code.upper())
    if not family:
        raise HTTPException(status_code=404, detail="邀请码无效")

    # 检查是否已是成员
    member_ids = [m["user_id"] for m in family.members]
    if str(user.id) in member_ids:
        raise HTTPException(status_code=400, detail="你已在该家庭中")

    # 加入家庭
    family.members.append({
        "user_id": str(user.id),
        "nickname": user.nickname,
        "avatar_url": user.avatar_url,
        "role": "member",
        "joined_at": "",
    })
    await family.save()

    # 更新用户
    user.family_id = str(family.id)
    await user.save()

    return JoinFamilyResponse(
        family_id=str(family.id),
        name=family.name,
        message=f"已加入「{family.name}」",
    )


@router.get("/info", response_model=FamilyInfoResponse)
async def get_family_info(user: User = Depends(get_current_user)):
    """获取当前用户所在家庭的信息"""
    if not user.family_id:
        raise HTTPException(status_code=404, detail="你还没有加入家庭")

    family = await Family.get(user.family_id)
    if not family:
        # 数据不一致，修复用户状态
        user.family_id = None
        await user.save()
        raise HTTPException(status_code=404, detail="家庭不存在")

    # 确定当前用户角色
    my_role = "member"
    for m in family.members:
        if m["user_id"] == str(user.id):
            my_role = m.get("role", "member")
            break

    return FamilyInfoResponse(
        family_id=str(family.id),
        name=family.name,
        invite_code=family.invite_code,
        members=[
            MemberInfo(
                user_id=m["user_id"],
                nickname=m.get("nickname", ""),
                avatar_url=m.get("avatar_url", ""),
                role=m.get("role", "member"),
                joined_at=m.get("joined_at", ""),
            )
            for m in family.members
        ],
        my_role=my_role,
    )


@router.post("/leave", response_model=LeaveFamilyResponse)
async def leave_family(user: User = Depends(get_current_user)):
    """退出当前家庭"""
    if not user.family_id:
        raise HTTPException(status_code=400, detail="你还没有加入家庭")

    family = await Family.get(user.family_id)
    if not family:
        user.family_id = None
        await user.save()
        raise HTTPException(status_code=404, detail="家庭不存在")

    # 检查是否为创建者且家庭中还有其他人
    is_creator = family.creator_id == str(user.id)
    other_members = [m for m in family.members if m["user_id"] != str(user.id)]

    if is_creator and len(other_members) > 0:
        raise HTTPException(
            status_code=400,
            detail="你是家庭创建者，请先将创建者角色转让给其他成员，或等所有成员退出后再解散家庭",
        )

    if is_creator and len(other_members) == 0:
        # 家庭没有其他成员，直接解散
        await family.delete()
    else:
        # 普通成员退出
        family.members = other_members
        await family.save()

    # 清除用户家庭归属
    user.family_id = None
    await user.save()

    return LeaveFamilyResponse(message="已退出家庭")
