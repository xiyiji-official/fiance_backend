from fastapi import APIRouter, Depends, HTTPException
from dependencies import get_current_active_user, get_db

from sqlalchemy.orm import Session
from sql_app import crud, schemas

from typing import Annotated, List

router = APIRouter(
    tags=["用户相关"]
)

@router.get("/current_users/short_info", response_model=schemas.UserBase)
async def read_users_me(
    current_user: Annotated[schemas.UserBase, Depends(get_current_active_user)],
):
    """
    获取当前活跃用户
    """
    return current_user

@router.get("/users/all_info", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    读取用户列表

    此函数用于从数据库中读取用户列表。

    参数:
    - skip (int): 跳过前多少个用户，默认为0。
    - limit (int): 限制返回的用户数量，默认为100。
    - db (Session): 数据库会话对象，由FastAPI的依赖注入系统提供。

    返回:
    - List[schemas.User]: 返回用户列表。
    """
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@router.get("/current_users/long_info", response_model=schemas.User)
def read_user(
    current_user: Annotated[schemas.User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
):
    """
    读取单个用户信息

    此函数用于从数据库中读取指定用户的信息。

    参数:
    - user_id (int): 用户ID。
    - db (Session): 数据库会话对象，由FastAPI的依赖注入系统提供。

    返回:
    - schemas.User: 返回指定用户的信息，包括balance、total_positive_amount、total_handled_negative_amount、total_unhandled_negative_amount。


    异常:
    - HTTPException: 如果用户不存在，则抛出状态码为404的HTTP异常。
    """
    db_user = crud.get_user(db, user_id=current_user.id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user