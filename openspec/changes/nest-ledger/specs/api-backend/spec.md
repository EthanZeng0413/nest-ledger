## ADDED Requirements

### Requirement: 微信登录认证
系统 SHALL 通过微信小程序登录获取用户身份。

#### Scenario: 首次登录
- **WHEN** 用户打开小程序并授权登录
- **THEN** 系统通过 `wx.login` 获取 code，服务端换取 openid，创建用户记录，签发 JWT token

#### Scenario: 已登录用户
- **WHEN** 已登录用户打开小程序，本地存在有效 token
- **THEN** 系统直接进入主页，不需重新登录

#### Scenario: Token 过期
- **WHEN** 服务端返回 401
- **THEN** 小程序自动重新执行登录流程

### Requirement: JWT 鉴权
所有业务 API SHALL 通过 JWT token 验证用户身份。

#### Scenario: 携带有效 token 请求
- **WHEN** 用户在请求头中携带有效 JWT token
- **THEN** 系统解析用户身份，正常处理请求

#### Scenario: 无 token 请求
- **WHEN** 请求头中不包含 Authorization
- **THEN** 系统返回 401 Unauthorized

#### Scenario: 过期 token 请求
- **WHEN** JWT token 已过期
- **THEN** 系统返回 401，附带"token 已过期"信息

### Requirement: 家庭数据隔离
系统 SHALL 确保用户只能访问自己所属家庭的数据。

#### Scenario: 跨家庭数据访问
- **WHEN** 用户请求非所属家庭的数据
- **THEN** 系统返回 403 Forbidden

### Requirement: RESTful API
系统 SHALL 提供符合 RESTful 规范的 API 接口。

#### Scenario: API 文档
- **WHEN** 开发者访问 /docs 路径
- **THEN** 系统展示 Swagger UI 交互式 API 文档

### Requirement: Docker 部署
系统 SHALL 提供 Docker Compose 部署方案。

#### Scenario: 一键部署
- **WHEN** 运维者执行 `docker compose up -d`
- **THEN** 系统启动 FastAPI 服务和 MongoDB 两个容器，API 监听 8000 端口

### Requirement: 错误处理
系统 SHALL 对所有 API 错误返回统一格式的错误响应。

#### Scenario: 参数校验错误
- **WHEN** 客户端提交的参数不符合要求
- **THEN** 系统返回 422 状态码，响应体包含错误字段和详细描述

#### Scenario: 服务器内部错误
- **WHEN** 服务端发生未预期的错误
- **THEN** 系统返回 500 状态码，响应体包含通用错误信息，不泄露内部细节
