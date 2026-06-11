"""JWT 认证服务"""

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from app.config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRE_DAYS


def create_token(user_id: str) -> str:
    """为用户签发 JWT token"""
    expire = datetime.now(timezone.utc) + timedelta(days=JWT_EXPIRE_DAYS)
    payload = {
        "sub": user_id,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_token(token: str) -> str | None:
    """验证 JWT token，返回 user_id 或 None"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None
