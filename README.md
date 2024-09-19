# Fiance_backend

这是一个基于 FastAPI 的账单管理系统，支持用户注册、登录、账单创建、查询和管理等功能。

## 技术栈

- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- JWT
- Passlib
- BeautifulSoup
- DocxTemplate

## 安装和使用

1. 克隆仓库:
   ```bash
   git clone https://github.com/your-username/Fiance_backend.git
   cd Fiance_backend
   ```

2. 安装依赖:
   ```bash
   pip install -r requirements.txt
   ```

3. 启动应用:
   ```bash
   uvicorn main:app --reload
   ```

4. 访问 API 文档: 打开浏览器并访问 `http://localhost:8000/docs`

## API 概览

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

- **获取当前用户的月度账单**
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

### 其他API

- **读取参考资料**
  - `GET /reference/`
  - 查询参数：`weekday` (可选)
  - 响应：参考资料内容

- **合并文件**
  - `POST /mergefiles/`
  - 请求体：文件列表和文件顺序
  - 响应：合并后的文件信息

## 数据库

项目使用 SQLite 数据库，数据库文件为 `sql_app.db`。如需修改数据库配置，请更新 `database.py` 文件中的连接字符串。

## 贡献指南

欢迎贡献代码、报告问题或提出新功能建议。请遵循以下步骤：

1. Fork 本仓库
2. 创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启一个 Pull Request

## 许可证

本项目采用 MIT 许可证。详细信息请查看 [LICENSE](LICENSE) 文件。