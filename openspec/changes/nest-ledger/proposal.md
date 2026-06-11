## Why

情侣和家庭用户需要一个**轻量、私密、一体化的记账+日历工具**。现有产品要么是个人记账App（无法共享），要么是通用日历（没有记账能力），要么数据不在自己手里（SaaS 服务）。nest-ledger 以微信小程序为载体降低使用门槛，数据部署在自有服务器保证隐私，让家庭成员在同一个空间里管理财务和日程。

## What Changes

- 新增微信小程序前端，提供记账、共享日历、家庭管理三个核心模块
- 新增 Python FastAPI 后端，提供 REST API 服务
- 新增 MongoDB 数据库，存储用户、家庭、账单、日历事件等数据
- 新增 Docker Compose 部署方案，一键部署到自有云服务器
- **MVP 阶段不做**：AI Agent 账单分析（预留接口）、PostgreSQL 迁移

## Capabilities

### New Capabilities

- `family-management`: 家庭创建、成员邀请与加入、角色管理（创建者/成员）
- `shared-accounting`: 收支记录 CRUD、分类管理、月度统计、家庭成员分摊
- `shared-calendar`: 日历事件 CRUD、重复规则（周/月/年）、提醒通知、日历月视图
- `api-backend`: FastAPI 服务、MongoDB 数据层、微信登录对接、Docker 部署

### Modified Capabilities

<!-- 全新项目，无现有 capabilities 需修改 -->

## Impact

- **前端**: 微信小程序原生 + Vant Weapp 组件库，全新项目
- **后端**: Python FastAPI + Motor (MongoDB 异步驱动) + Beanie ODM，全新项目
- **部署**: Docker Compose（fastapi + mongodb 两个容器），目标平台为 Linux 云服务器
- **认证**: 微信小程序登录（wx.login + openid），无需额外依赖
- **推送**: 微信小程序订阅消息，无需 APNs
