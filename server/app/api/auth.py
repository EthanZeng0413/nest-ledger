"""认证相关 API"""

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.config import WECHAT_APPID, WECHAT_SECRET
from app.models.user import User
from app.services.auth import create_token

router = APIRouter(prefix="/api/v1/auth", tags=["认证"])


class LoginRequest(BaseModel):
    code: str  # wx.login 返回的 code
    nickname: str = ""
    avatar_url: str = ""


class LoginResponse(BaseModel):
    token: str
    user_id: str
    nickname: str
    is_new: bool  # 是否新用户


# ---------- 开发测试用 ----------

class DevLoginRequest(BaseModel):
    nickname: str = "测试用户"


@router.post("/dev/login", response_model=LoginResponse)
async def dev_login(req: DevLoginRequest):
    """开发环境登录：绕过微信，直接创建测试用户并签发 token"""
    import hashlib
    fake_openid = "dev_" + hashlib.md5(req.nickname.encode()).hexdigest()[:16]

    user = await User.find_one(User.openid == fake_openid)
    is_new = user is None

    if is_new:
        user = User(openid=fake_openid, nickname=req.nickname)
        await user.insert()

    token = create_token(str(user.id))
    return LoginResponse(
        token=token,
        user_id=str(user.id),
        nickname=user.nickname,
        is_new=is_new,
    )


@router.post("/login", response_model=LoginResponse)
async def wechat_login(req: LoginRequest):
    """微信小程序登录：用 wx.login code 换取 openid，签发 JWT"""
    # 1. 调用微信接口换取 openid
    wechat_url = "https://api.weixin.qq.com/sns/jscode2session"
    params = {
        "appid": WECHAT_APPID,
        "secret": WECHAT_SECRET,
        "js_code": req.code,
        "grant_type": "authorization_code",
    }

    async with httpx.AsyncClient() as client:
        resp = await client.get(wechat_url, params=params)
        data = resp.json()

    if "errcode" in data and data["errcode"] != 0:
        raise HTTPException(status_code=400, detail=f"微信登录失败: {data.get('errmsg', '未知错误')}")

    openid = data["openid"]

    # 2. 查找或创建用户
    user = await User.find_one(User.openid == openid)
    is_new = user is None

    if is_new:
        user = User(
            openid=openid,
            nickname=req.nickname or f"用户{openid[-6:]}",
            avatar_url=req.avatar_url,
        )
        await user.insert()

    # 3. 签发 JWT
    token = create_token(str(user.id))

    return LoginResponse(
        token=token,
        user_id=str(user.id),
        nickname=user.nickname,
        is_new=is_new,
    )
