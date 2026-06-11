# 🏠 窝记 (nest-ledger)

家庭共享记账与日历微信小程序。情侣和家庭用户在一个空间里管理财务和日程，数据部署在自有服务器。

## ✨ 功能

- **共享记账** — 收支记录、分类管理、月度统计、家庭成员可见
- **共享日历** — 日历事件、重复规则（每天/每周/每月）、月视图
- **家庭管理** — 创建家庭、邀请码加入、成员角色

## 🛠 技术栈

| 层 | 技术 |
|---|------|
| 前端 | 微信小程序原生 + Vant Weapp |
| 后端 | Python FastAPI + Motor (MongoDB 异步) + Beanie ODM |
| 数据库 | MongoDB 7 |
| 部署 | Docker Compose |

## 📁 项目结构

```
nest-ledger/
├── miniprogram/              # 微信小程序
│   ├── pages/
│   │   ├── login/            # 登录页
│   │   ├── index/            # 记账首页
│   │   ├── calendar/         # 共享日历
│   │   ├── stats/            # 统计看板
│   │   └── family/           # 家庭管理
│   ├── components/           # 共享组件
│   ├── utils/api.js          # HTTP 请求封装
│   ├── app.js / app.json / app.wxss
│   └── package.json
├── server/                   # Python 后端
│   ├── app/
│   │   ├── api/              # API 路由
│   │   │   ├── auth.py       # 登录认证
│   │   │   ├── family.py     # 家庭管理
│   │   │   ├── transaction.py # 记账
│   │   │   ├── calendar.py   # 日历事件
│   │   │   └── deps.py       # 鉴权中间件
│   │   ├── models/           # Beanie ODM 模型
│   │   ├── services/         # 业务服务
│   │   ├── config.py         # 配置
│   │   └── main.py           # FastAPI 入口
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
├── docker-compose.yml
└── openspec/                 # OpenSpec 提案文档
```

## 🚀 快速部署

### 1. 克隆仓库

```bash
git clone https://github.com/EthanZeng0413/nest-ledger.git
cd nest-ledger
```

### 2. 配置环境

```bash
cp server/.env.example server/.env
# 编辑 server/.env，填入：
#   - WECHAT_APPID: 微信小程序 AppID
#   - WECHAT_SECRET: 微信小程序 Secret
#   - JWT_SECRET: 随机字符串
```

### 3. 启动服务

```bash
docker compose up -d
```

API 服务默认监听 `http://localhost:8000`，Swagger 文档在 `http://localhost:8000/docs`。

### 4. 配置小程序

1. 在 [微信公众平台](https://mp.weixin.qq.com) 注册小程序，获取 AppID 和 Secret
2. 打开 `miniprogram/` 目录到微信开发者工具
3. 修改 `miniprogram/app.js` 中的 `apiBaseUrl` 为你的服务器地址
4. 在开发者工具中：工具 → 构建 npm
5. 预览/上传

## 📡 API 概览

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/auth/login` | 微信登录 |
| POST | `/api/v1/family/create` | 创建家庭 |
| POST | `/api/v1/family/join` | 加入家庭 |
| GET | `/api/v1/family/info` | 家庭信息 |
| POST | `/api/v1/family/leave` | 退出家庭 |
| POST | `/api/v1/transaction/add` | 添加账单 |
| GET | `/api/v1/transaction/list?month=YYYY-MM` | 账单列表 |
| DELETE | `/api/v1/transaction/:id` | 删除账单 |
| GET | `/api/v1/transaction/stats?month=YYYY-MM` | 月度统计 |
| POST | `/api/v1/event/create` | 创建日历事件 |
| GET | `/api/v1/event/list?month=YYYY-MM` | 事件列表 |
| PUT | `/api/v1/event/:id` | 编辑事件 |
| DELETE | `/api/v1/event/:id` | 删除事件 |
| GET | `/api/v1/health` | 健康检查 |

## 🗺️ 路线图

- [x] MVP: 记账 + 日历 + 家庭管理
- [ ] Phase 2: AI Agent 账单分析
- [ ] Phase 3: 消息推送、Widget、第三方日历同步

## 📄 License

MIT
