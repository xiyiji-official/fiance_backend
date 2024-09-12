from datetime import timedelta
import json
from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from jwt import InvalidTokenError
from sqlalchemy.orm import Session
from typing import List, Annotated
from passlib.context import CryptContext


from sql_app import crud, models, schemas
from sql_app.database import SessionLocal, engine

from bs4 import BeautifulSoup
from docxtpl import DocxTemplate

## 引用模板，用于生成docx文件
doc = DocxTemplate("./muban.docx")  ## 请修改为自己的模板路径

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  # 定义OAuth2的认证方案
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

origins = [
    "http://localhost",
    "http://localhost:8000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


## 模板内容，请更新为您的模板内容
models: str = "{time}&emsp;&emsp;&emsp;{name}<br/>会议负责人：<br/>会议分类：<br/>关注内容：<br/><br/>{url}<br/>"


# 数据库依赖
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, crud.SECRET_KEY, algorithms=[crud.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = crud.authenticate_user(db, name=token_data.username)
    if not user:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: schemas.UserBase = Depends(get_current_user),
):
    """
    获取当前活跃用户
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="非活跃用户")
    return current_user


@app.post("/token")
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
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="错误的用户名或密码",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=crud.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = crud.create_access_token(
        data={"sub": user.name}, expires_delta=access_token_expires
    )
    return schemas.Token(access_token=access_token, token_type="bearer")


@app.get("/current_users/short_info", response_model=schemas.UserBase)
async def read_users_me(
    current_user: Annotated[schemas.UserBase, Depends(get_current_active_user)],
):
    """
    获取当前活跃用户
    """
    return current_user


@app.post("/users/signup", response_model=schemas.User)
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


@app.get("/users/all_info", response_model=List[schemas.User])
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


@app.get("/current_users/long_info", response_model=schemas.User)
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


@app.post("/current_users/add_bills/", response_model=schemas.Bill)
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


@app.get("/bills/", response_model=List[schemas.Bill])
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


@app.get("/bills/{bill_id}", response_model=schemas.Bill)
def read_bill(bill_id: int, db: Session = Depends(get_db)):
    """
    读取单个账单信息

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


@app.put("/bills/{bill_id}", response_model=schemas.Bill)
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


@app.delete("/bills/{bill_id}", response_model=schemas.Bill)
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


@app.get("/current_users/month_bills/", response_model=List[schemas.Bill])
def get_user_bills(
    current_user: Annotated[schemas.User, Depends(get_current_active_user)],
    month: int = Query(..., description="Month (1-12)"),
    db: Session = Depends(get_db),
):
    """
    获取当前用户的账单

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


@app.get("/reference/")
def read_reference(weekday: str | None = None):
    f = open("config.json", "r", encoding="UTF-8")
    config = json.load(f)
    if weekday is not None:
        for i in config["reference"]:
            if i["name"] == weekday:
                data = i["content"]
                return data
    else:
        data = config["reference"]
        return data


@app.post("/meeting/settings/")
def settings(item: dict):
    global models
    models = item["item"]
    return "成功设置"


@app.post("/meeting/")
def meeting(item: dict):
    data = item["item"]
    soup = BeautifulSoup(data, "html.parser")
    table = soup.find("table")
    temple = []
    try:
        for row in table.find_all("tr"):
            cell = row.find_all("td")
            try:
                time = (  # noqa: F841
                    (cell[0].text)
                    .replace(" ", "")
                    .replace("\n", "")
                    .replace(":", "：")
                    .split("-")[0]
                )
            except Exception as e:  # noqa: F841
                time = ""  # noqa: F841
            try:
                name = (cell[1].text).replace(" ", "").replace("\n", "").split("【")[0]  # noqa: F841
            except Exception as e:  # noqa: F841
                name = ""  # noqa: F841
            try:
                url = cell[2].find("a").get("href")  # noqa: F841
            except Exception as e:  # noqa: F841
                url = ""  # noqa: F841
            temple.append(eval(f'f"{models}"'))
    except Exception as e:
        print(e)
        return {"data": "没有可解析内容"}
    return {"data": temple}


@app.post("/render/")
def renderDocx(item: dict):
    doc.render(item)
    doc.save("result.docx")
    return FileResponse("result.docx")
