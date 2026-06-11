"""记账 API"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from app.api.deps import get_current_user
from app.models.user import User
from app.models.transaction import Transaction

router = APIRouter(prefix="/api/v1/transaction", tags=["记账"])

# 预设分类
EXPENSE_CATEGORIES = ["餐饮", "交通", "购物", "住房", "娱乐", "医疗", "教育", "其他"]
INCOME_CATEGORIES = ["工资", "奖金", "理财", "兼职", "其他"]


# ---------- 请求/响应模型 ----------

class AddTransactionRequest(BaseModel):
    amount: float = Field(..., gt=0)
    category: str = Field(..., min_length=1)
    type: str = Field(..., pattern="^(expense|income)$")
    date: str = Field(..., min_length=10, max_length=10)  # YYYY-MM-DD
    note: str = ""


class TransactionItem(BaseModel):
    id: str
    amount: float
    category: str
    type: str
    date: str
    note: str
    user_id: str
    nickname: str
    created_at: str


class TransactionListResponse(BaseModel):
    month: str
    total_income: float
    total_expense: float
    items: list[TransactionItem]


class StatsResponse(BaseModel):
    month: str
    total_income: float
    total_expense: float
    balance: float
    expense_by_category: list[dict]  # [{category, amount, percent}]
    income_by_category: list[dict]


class DeleteResponse(BaseModel):
    message: str


# ---------- API 端点 ----------

@router.post("/add", response_model=TransactionItem)
async def add_transaction(req: AddTransactionRequest, user: User = Depends(get_current_user)):
    """添加收支记录"""
    if not user.family_id:
        raise HTTPException(status_code=400, detail="请先加入家庭")

    # 校验分类
    if req.type == "expense" and req.category not in EXPENSE_CATEGORIES:
        raise HTTPException(status_code=400, detail=f"无效的支出分类，可选: {EXPENSE_CATEGORIES}")
    if req.type == "income" and req.category not in INCOME_CATEGORIES:
        raise HTTPException(status_code=400, detail=f"无效的收入分类，可选: {INCOME_CATEGORIES}")

    tx = Transaction(
        family_id=user.family_id,
        user_id=str(user.id),
        amount=req.amount,
        category=req.category,
        type=req.type,
        date=req.date,
        note=req.note,
    )
    await tx.insert()

    return TransactionItem(
        id=str(tx.id),
        amount=tx.amount,
        category=tx.category,
        type=tx.type,
        date=tx.date,
        note=tx.note,
        user_id=str(user.id),
        nickname=user.nickname,
        created_at=tx.created_at.isoformat() if tx.created_at else "",
    )


@router.get("/list", response_model=TransactionListResponse)
async def list_transactions(
    month: str = Query(..., min_length=7, max_length=7),  # YYYY-MM
    user: User = Depends(get_current_user),
):
    """按月查询账单列表"""
    if not user.family_id:
        raise HTTPException(status_code=400, detail="请先加入家庭")

    # 查询该月所有记录，按日期降序
    txs = await Transaction.find(
        Transaction.family_id == user.family_id,
        Transaction.date >= f"{month}-01",
        Transaction.date <= f"{month}-31",  # MongoDB 字符串比较足够
    ).sort(-Transaction.date, -Transaction.created_at).to_list()

    # 计算汇总
    total_income = sum(t.amount for t in txs if t.type == "income")
    total_expense = sum(t.amount for t in txs if t.type == "expense")

    # 获取用户昵称映射（逐个查询）
    nickname_map = {}
    for uid in set(t.user_id for t in txs):
        u = await User.get(uid)
        if u:
            nickname_map[uid] = u.nickname

    return TransactionListResponse(
        month=month,
        total_income=round(total_income, 2),
        total_expense=round(total_expense, 2),
        items=[
            TransactionItem(
                id=str(t.id),
                amount=t.amount,
                category=t.category,
                type=t.type,
                date=t.date,
                note=t.note,
                user_id=t.user_id,
                nickname=nickname_map.get(t.user_id, "未知"),
                created_at=t.created_at.isoformat() if t.created_at else "",
            )
            for t in txs
        ],
    )


@router.delete("/{tx_id}", response_model=DeleteResponse)
async def delete_transaction(tx_id: str, user: User = Depends(get_current_user)):
    """删除自己创建的记录"""
    tx = await Transaction.get(tx_id)
    if not tx:
        raise HTTPException(status_code=404, detail="记录不存在")

    if tx.user_id != str(user.id):
        raise HTTPException(status_code=403, detail="只能删除自己的记录")

    await tx.delete()
    return DeleteResponse(message="已删除")


@router.get("/stats", response_model=StatsResponse)
async def get_stats(
    month: str = Query(..., min_length=7, max_length=7),
    user: User = Depends(get_current_user),
):
    """月度统计"""
    if not user.family_id:
        raise HTTPException(status_code=400, detail="请先加入家庭")

    txs = await Transaction.find(
        Transaction.family_id == user.family_id,
        Transaction.date >= f"{month}-01",
        Transaction.date <= f"{month}-31",
    ).to_list()

    total_income = sum(t.amount for t in txs if t.type == "income")
    total_expense = sum(t.amount for t in txs if t.type == "expense")

    def calc_category_stats(items, total):
        """计算各分类金额和占比"""
        cat_map = {}
        for t in items:
            cat_map[t.category] = cat_map.get(t.category, 0) + t.amount
        return [
            {
                "category": cat,
                "amount": round(amt, 2),
                "percent": round(amt / total * 100, 1) if total > 0 else 0,
            }
            for cat, amt in sorted(cat_map.items(), key=lambda x: -x[1])
        ]

    expenses = [t for t in txs if t.type == "expense"]
    incomes = [t for t in txs if t.type == "income"]

    return StatsResponse(
        month=month,
        total_income=round(total_income, 2),
        total_expense=round(total_expense, 2),
        balance=round(total_income - total_expense, 2),
        expense_by_category=calc_category_stats(expenses, total_expense),
        income_by_category=calc_category_stats(incomes, total_income),
    )
