from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.sql_app import crud, schemas

from app.dependencies import get_db

router = APIRouter(
    tags=["登录注册"],
    dependencies=[Depends(get_db)]
)



@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
) -> schemas.Token:
    """
    登录获取访问令牌
    """
    try:
        user = crud.authenticate_user(
            db, name=form_data.username, hashed_password=form_data.password
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"验证错误: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user["status"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=user["message"],
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = user["user"]
    access_token_expires = timedelta(minutes=crud.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = crud.create_access_token(
        data={"sub": user.name}, expires_delta=access_token_expires
    )
    return schemas.Token(access_token=access_token, token_type="bearer")


@router.post("/users/signup", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    创建新用户

    此函数处理用户注册请求，创建新的用户账户。

    参数:
    - user (schemas.UserCreate): 包含用户注册信息的Pydantic模型，通常包括用户名、邮箱和密码。
    - db (Session): 数据库会话对象，由FastAPI的依赖注入系统提供。

    流程:
    1. 首先检查数据库中是否已存在使用相同邮箱的用户。
    2. 如果邮箱已被注册，则抛出HTTP 400错误。
    3. 如果邮箱未被使用，则创建新用户并将其添加到数据库中。

    返回:
    - schemas.User: 返回新创建的用户信息，包括自动生成的用户ID。

    异常:
    - HTTPException: 如果邮箱已被注册，则抛出状态码为400的HTTP异常。

    注意:
    - 此函数使用 @app.post 装饰器，表示它响应 POST 请求到 "/users/" 路径。
    - response_model=schemas.User 指定了响应的数据模型，确保返回的数据符合User模式。
    """
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="邮箱已注册")
    return crud.create_user(db=db, user=user)
