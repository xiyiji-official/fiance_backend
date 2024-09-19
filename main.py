from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer

from sqladmin import Admin
from passlib.context import CryptContext

from sql_app import models, AdminSchemas
from sql_app.database import engine

from auth import router as auth_router
from user import router as user_router
from bill import router as bill_router
from others import router as others_router


models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FianceApp",
    description='''# 项目名称

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
```''',
    summary="财务管理系统和一些其他功能的API",
    version="0.0.3",
)

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://154.8.202.195:8000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许的源，根据你的前端应用地址调整
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头
)

# 设置 Admin
admin = Admin(
    app, engine, authentication_backend=AdminSchemas.AdminAuth(secret_key="youcanuseit")
)
admin.add_view(AdminSchemas.UserAdmin)
admin.add_view(AdminSchemas.BillAdmin)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  # 定义OAuth2的认证方案
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 包含其他路由
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(bill_router)
app.include_router(others_router)



