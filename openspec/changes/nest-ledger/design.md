## Context

nest-ledger 是一个全新的项目，面向情侣和家庭用户，提供共享记账和共享日历功能。项目以微信小程序为载体，后端部署在自有云服务器上。MVP 阶段聚焦核心功能，不做过度设计。

- **用户**: 2-6 人的家庭/情侣群体
- **平台**: 微信小程序（iOS/Android 均可用）
- **后端**: 用户自有 Linux 云服务器，Docker 部署
- **数据量级**: 单个家庭日均 5-20 条账单，年累计 < 1 万条

## Goals / Non-Goals

**Goals:**
- 微信小程序原生开发，提供流畅的记账和日历体验
- FastAPI 后端 + MongoDB，RESTful API
- 家庭为单位的数据隔离，邀请码加入机制
- Docker Compose 一键部署
- 代码结构清晰，为后续 Agent 功能预留扩展点

**Non-Goals:**
- 不做 AI Agent 账单分析（Phase 2）
- 不做 PostgreSQL 迁移（SQLite/MongoDB 满足需求）
- 不做多币种支持
- 不做第三方日历同步（CalDAV/Google Calendar）
- 不做微信支付/支付宝账单导入
- 不做消息推送（Phase 2）

## Decisions

### 1. 小程序原生 vs uni-app/Taro

**选原生**。uni-app 的价值在于多端编译，但 nest-ledger 只做微信小程序，不需要那层抽象。原生开发调试链路最短、性能最好、微信新特性支持最快。后续如果真要扩展到支付宝小程序，再评估迁移成本。

### 2. Vant Weapp 作为 UI 组件库

**选 Vant Weapp**。社区最活跃（16.5k stars），组件覆盖记账表单、日历视图、弹窗等全部需求。按需引入，包体积可控。TDesign 偏企业级太重，WeUI 太基础。

### 3. FastAPI vs Flask / Django

**选 FastAPI**。异步支持好（配合 Motor 驱动 MongoDB），自动生成 OpenAPI 文档方便前后端联调，Pydantic 数据校验与 MongoDB schema-less 特性互补。Flask 异步支持弱，Django 太重不适合微服务。

### 4. MongoDB vs SQLite

**选 MongoDB**（用户决策）。早期 schema 频繁迭代时无需 migration，字段随时加减。后续推广时水平扩展路径清晰。使用 Beanie ODM 提供类型安全和数据校验，弥补 schema-less 的不足。

### 5. 项目结构：Monorepo

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
│   │   └── main.py        # FastAPI 入口
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml
└── README.md
```

### 6. API 设计风格

RESTful，JSON 格式。认证用微信 `wx.login` 获取 openid，服务端生成 JWT token。所有业务 API 需携带 token，按 `family_id` 做数据隔离。

### 7. 日历提醒方案（MVP）

小程序订阅消息。用户在创建事件时授权"日程提醒"模板，服务端定时任务检查即将开始的事件，通过微信订阅消息接口推送。暂不做复杂的事件提醒升级。

## Risks / Trade-offs

- **[微信生态锁定]**: 只做微信小程序 → 后续扩展到独立 App 需重写前端。缓解：后端 API 完全独立，可服务任何客户端。
- **[MongoDB 运维]**: 比 SQLite 多一个容器 → 通过 Docker Compose 简化部署，MongoDB 官方镜像开箱即用。
- **[小程序审核风险]**: 微信审核可能不通过 → 功能设计符合小程序规范，不涉及敏感内容。
- **[用户数据隐私]**: 自部署模式下用户数据在自己服务器 → 提供数据库备份指南，建议用户定期备份。
