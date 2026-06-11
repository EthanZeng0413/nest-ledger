# nest-ledger (窝记)

家庭共享记账与日历微信小程序。情侣/家庭用户在一个空间里管理财务和日程，数据部署在自有服务器。

## 技术栈

- **前端**: 微信小程序原生 + Vant Weapp 组件库
- **后端**: Python FastAPI + Motor (MongoDB 异步驱动) + Beanie ODM
- **数据库**: MongoDB
- **部署**: Docker Compose (fastapi + mongodb)

## 项目结构

```
nest-ledger/
├── miniprogram/           # 微信小程序
│   ├── pages/
│   │   ├── index/         # 记账首页
│   │   ├── calendar/      # 共享日历
│   │   ├── stats/         # 统计看板
│   │   └── family/        # 家庭设置
│   ├── components/        # 共享组件
│   ├── utils/             # 工具函数
│   ├── app.js
│   ├── app.json
│   └── app.wxss
├── server/                # Python 后端
│   ├── app/
│   │   ├── api/           # 路由
│   │   ├── models/        # Beanie ODM 模型
│   │   ├── services/      # 业务逻辑
│   │   └── main.py
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml
└── openspec/              # OpenSpec 提案与设计文档
```

## 开发约定

- 代码注释用中文
- API 路径: `/api/v1/`
- 微信小程序页面名用小写
- MongoDB 集合名用 snake_case
- 每个任务组完成后 commit
