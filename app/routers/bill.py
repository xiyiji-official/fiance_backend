from fastapi import APIRouter, Depends, HTTPException, Query
from app.dependencies import get_current_active_user, get_db

from sqlalchemy.orm import Session
from app.sql_app import crud, schemas

from typing import Annotated, List

router = APIRouter(tags=["账单相关"])


@router.post("/current_users/add_bills/", response_model=schemas.Bill)
def create_bill_for_user(
    current_user: Annotated[schemas.User, Depends(get_current_active_user)],
    bill: schemas.BillCreate,
    db: Session = Depends(get_db),
):
    """
    为指定用户创建账单

    此函数用于为指定用户创建一个新的账单。

    参数:
    - user_id (int): 用户ID。
    - bill (schemas.BillCreate): 包含账单信息的Pydantic模型。

    返回:
    - schemas.Bill: 返回新创建的账单信息。

    异常:
    - HTTPException: 如果用户不存在，则抛出状态码为404的HTTP异常。
    """
    return crud.create_bill(db=db, bill=bill, user_id=current_user.user_id)


@router.get("/current_users/month_bills/", response_model=List[schemas.Bill])
def get_user_bills(
    current_user: Annotated[schemas.User, Depends(get_current_active_user)],
    month: int = Query(..., description="Month (1-12)"),
    db: Session = Depends(get_db),
):
    """
    按月获取当前用户的账单

    此函数用于获取当前用户的某一月的账单。

    参数:
    - user_id (int): 用户ID。
    - month (int): 月份。
    - db (Session): 数据库会话对象，由FastAPI的依赖注入系统提供。
    """
    bills = crud.get_user_bills(db, user_id=current_user.id, month=month)
    if bills is None or len(bills) == 0:
        raise HTTPException(status_code=404, detail="本月无账单明细内容。")
    return bills


@router.get("/bills/", response_model=List[schemas.Bill])
def read_bills(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    读取账单列表

    此函数用于从数据库中读取账单列表。

    参数:
    - skip (int): 跳过前多少个账单，默认为0。
    - limit (int): 限制返回的账单数量，默认为100。
    - db (Session): 数据库会话对象，由FastAPI的依赖注入系统提供。

    返回:
    - List[schemas.Bill]: 返回账单列表。
    """
    bills = crud.get_bills(db, skip=skip, limit=limit)
    return bills


@router.get("/bills/{bill_id}", response_model=schemas.Bill)
def read_bill(bill_id: int, db: Session = Depends(get_db)):
    """
    读取指定单个账单信息

    此函数用于从数据库中读取指定账单的信息。

    参数:
    - bill_id (int): 账单ID。
    - db (Session): 数据库会话对象，由FastAPI的依赖注入系统提供。

    返回:
    - schemas.Bill: 返回指定账单的信息。

    异常:
    - HTTPException: 如果账单不存在，则抛出状态码为404的HTTP异常。
    """
    db_bill = crud.get_bill(db, bill_id=bill_id)
    if db_bill is None:
        raise HTTPException(status_code=404, detail="Bill not found")
    return db_bill


@router.put("/bills/{bill_id}", response_model=schemas.Bill)
def update_bill(bill_id: int, bill: schemas.BillUpdate, db: Session = Depends(get_db)):
    """
    更新指定账单信息

    此函数用于更新指定账单的信息。

    参数:
    - bill_id (int): 账单ID。
    - bill (schemas.BillUpdate): 包含账单更新信息的Pydantic模型。

    返回:
    - schemas.Bill: 返回更新后的账单信息。

    异常:
    - HTTPException: 如果账单不存在，则抛出状态码为404的HTTP异常。
    """
    db_bill = crud.update_bill(db, bill_id=bill_id, bill=bill)
    if db_bill is None:
        raise HTTPException(status_code=404, detail="Bill not found")
    return db_bill


@router.delete("/bills/{bill_id}", response_model=schemas.Bill)
def delete_bill(bill_id: int, db: Session = Depends(get_db)):
    """
    删除指定账单

    此函数用于删除指定账单。

    参数:
    - bill_id (int): 账单ID。
    - db (Session): 数据库会话对象，由FastAPI的依赖注入系统提供。

    返回:
    - schemas.Bill: 返回删除的账单信息。

    异常:
    - HTTPException: 如果账单不存在，则抛出状态码为404的HTTP异常。
    """
    db_bill = crud.delete_bill(db, bill_id=bill_id)
    if db_bill is None:
        raise HTTPException(status_code=404, detail="Bill not found")
    return db_bill
