## 1. 项目脚手架

- [ ] 1.1 初始化微信小程序项目，注册 AppID，配置 app.json（页面路由、tabBar）
- [ ] 1.2 安装 Vant Weapp，配置按需引入
- [ ] 1.3 初始化 server/ 目录，创建 FastAPI 项目骨架（main.py、requirements.txt）
- [ ] 1.4 配置 Docker Compose（fastapi + mongodb 两个容器）

## 2. 后端：数据模型与认证

- [ ] 2.1 定义 Beanie ODM 模型（User、Family、Transaction、CalendarEvent）
- [ ] 2.2 实现 MongoDB 连接管理，数据库初始化
- [ ] 2.3 实现微信登录接口（wx.login code → openid → JWT）
- [ ] 2.4 实现 JWT 鉴权中间件

## 3. 后端：家庭管理 API

- [ ] 3.1 实现 POST /family — 创建家庭，生成邀请码
- [ ] 3.2 实现 POST /family/join — 通过邀请码加入家庭
- [ ] 3.3 实现 GET /family/members — 查看家庭成员列表
- [ ] 3.4 实现 POST /family/leave — 退出家庭（含创建者转让检查）

## 4. 后端：记账 API

- [ ] 4.1 实现 POST /transaction — 添加收支记录
- [ ] 4.2 实现 GET /transaction?month=YYYY-MM — 按月查询账单列表
- [ ] 4.3 实现 DELETE /transaction/:id — 删除自己创建的记录
- [ ] 4.4 实现 GET /transaction/stats?month=YYYY-MM — 月度统计（总收支、分类占比）

## 5. 后端：日历 API

- [ ] 5.1 实现 POST /event — 创建日历事件（含重复规则）
- [ ] 5.2 实现 GET /event?month=YYYY-MM — 按月查询日历事件
- [ ] 5.3 实现 PUT /event/:id — 编辑自己创建的事件
- [ ] 5.4 实现 DELETE /event/:id — 删除自己创建的事件

## 6. 前端：基础框架

- [ ] 6.1 配置全局样式（app.wxss），设定 CSS 变量（主题色、字体）
- [ ] 6.2 实现微信登录页（wx.login + 调用后端登录 API，存储 token）
- [ ] 6.3 实现 HTTP 请求封装（wx.request + token 注入 + 401 自动重登录）
- [ ] 6.4 配置 tabBar（记账、日历、统计、我的）

## 7. 前端：家庭管理

- [ ] 7.1 实现"我的"页面（显示用户信息、当前家庭、成员列表）
- [ ] 7.2 实现创建家庭页面（输入名称 → 调用 API → 展示邀请码）
- [ ] 7.3 实现加入家庭页面（输入邀请码 → 调用 API → 跳转首页）
- [ ] 7.4 实现退出/切换家庭功能

## 8. 前端：记账模块

- [ ] 8.1 实现记账首页（当月账单列表、按日期分组、收支合计栏）
- [ ] 8.2 实现添加账单弹窗（Vant Popup + Field + Picker + NumberKeyboard）
- [ ] 8.3 实现删除账单（左滑删除或长按删除，仅自己的记录）
- [ ] 8.4 实现月份切换（顶部月份选择器）
- [ ] 8.5 实现统计看板页面（Vant 环形图或简单进度条，分类占比展示）

## 9. 前端：日历模块

- [ ] 9.1 实现日历月视图页面（Vant Calendar 组件，事件日期标记）
- [ ] 9.2 实现创建事件弹窗（标题、时间选择、重复规则、备注）
- [ ] 9.3 实现点击日期查看事件列表
- [ ] 9.4 实现编辑和删除事件

## 10. 部署与文档

- [ ] 10.1 编写 README.md（项目介绍、部署步骤、技术栈说明）
- [ ] 10.2 验证 Docker Compose 部署流程，确保一键启动
- [ ] 10.3 编写 server/.env.example 环境变量模板
