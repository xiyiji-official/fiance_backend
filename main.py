from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
import logging
from app.logger import main_logger

from sqladmin import Admin
from passlib.context import CryptContext

from app.sql_app import models, AdminSchemas
from app.sql_app.database import engine

from app.routers.auth import router as auth_router
from app.routers.user import router as user_router
from app.routers.bill import router as bill_router
from app.routers.others import router as others_router

from app.setting import settings


models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FianceApp",
    description="""# 项目名称

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

## 启动

使用以下命令启动应用：

```bash
uvicorn main:app --reload
```""",
    summary="财务管理系统和一些其他功能的API",
    version="0.0.3",
)

main_logger.info("FastAPI application initialized")

origins = settings.origins
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

# 配置Uvicorn的日志
uvicorn_logger = logging.getLogger("uvicorn")
uvicorn_logger.handlers = main_logger.handlers
