# 项目名称

这是一个基于 FastAPI 的账单管理系统，支持用户注册、登录、账单创建、查询和管理等功能。

本README.md由Claude 3.5 Sonnet生成。

## 技术栈

- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- JWT
- Passlib
- BeautifulSoup
- DocxTemplate

## 启动

使用以下命令启动应用：

```bash
uvicorn main:app --reload
```

## API

### 用户相关

- **注册用户**
  - `POST /users/signup`
  - 请求体：`UserCreate` 模型
  - 响应：`User` 模型

- **获取当前用户信息**
  - `GET /current_users/short_info`
  - 响应：`UserBase` 模型

- **获取所有用户信息**
  - `GET /users/all_info`
  - 查询参数：`skip` (默认 0), `limit` (默认 100)
  - 响应：`List[User]`

### 账单相关

- **创建账单**
  - `POST /current_users/add_bills/`
  - 请求体：`BillCreate` 模型
  - 响应：`Bill` 模型

- **获取账单列表**
  - `GET /bills/`
  - 查询参数：`skip` (默认 0), `limit` (默认 100)
  - 响应：`List[Bill]`

- **获取单个账单信息**
  - `GET /bills/{bill_id}`
  - 响应：`Bill` 模型

- **更新账单信息**
  - `PUT /bills/{bill_id}`
  - 请求体：`BillUpdate` 模型
  - 响应：`Bill` 模型

- **删除账单**
  - `DELETE /bills/{bill_id}`
  - 响应：`Bill` 模型

- **获取当前用户的账单**
  - `GET /current_users/month_bills/`
  - 查询参数：`month` (1-12)
  - 响应：`List[Bill]`

### 会议相关

- **设置会议**
  - `POST /meeting/settings/`
  - 请求体：`dict`
  - 响应：成功消息

- **解析会议内容**
  - `POST /meeting/`
  - 请求体：`dict`
  - 响应：解析后的数据

- **生成 Docx 文件**
  - `POST /render/`
  - 请求体：`dict`
  - 响应：生成的 Docx 文件

## 数据库

使用 SQLite 数据库，数据库文件为 `sql_app.db`。可以根据需要修改数据库连接字符串。

## 依赖安装

使用以下命令安装项目依赖：

```bash
pip install -r requirements.txt
```


## 贡献

欢迎任何形式的贡献！请提交问题或拉取请求。

## 许可证

本项目采用 MIT 许可证，详细信息请查看 LICENSE 文件。