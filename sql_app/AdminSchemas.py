from sqladmin import ModelView
from sqladmin.authentication import AuthenticationBackend
from sql_app import crud
from sql_app.models import User, Bill
from fastapi import Request
from sql_app.database import SessionLocal


class UserAdmin(ModelView, model=User):
    """
    用于在Admin页面中管理用户
    """
    name = "用户"
    name_plural = "用户"
    icon = "fa-user-circle-o"
    column_list = [User.id, User.name, User.nickname, User.email, User.is_active]
    column_details_list = [
        User.id,
        User.name,
        User.nickname,
        User.email,
        User.hashed_password,
        User.is_active,
        "bill_info",
    ]
    column_searchable_list = [User.name]
    column_sortable_list = [User.id, User.name, User.is_active]
    column_labels = {
        User.id: "ID",
        User.name: "用户名",
        User.nickname: "昵称",
        User.email: "邮箱",
        User.hashed_password: "密码",
        User.is_active: "是否激活",
        "bill_info": "账单",
    }
    can_export = False


class BillAdmin(ModelView, model=Bill):
    """
    用于在Admin页面中管理账单明细
    """
    name = "账单明细"
    name_plural = "账单明细"
    icon = "fa-money"
    column_list = [Bill.id, Bill.bill_date, Bill.summary, Bill.amount, Bill.handle]
    column_details_list = [
        "user_info",
        Bill.id,
        Bill.bill_date,
        Bill.summary,
        Bill.amount,
        Bill.handle,
    ]
    column_searchable_list = [Bill.summary]
    column_sortable_list = [
        Bill.id,
        Bill.bill_date,
        Bill.summary,
        Bill.amount,
        Bill.handle,
    ]
    column_labels = {
        Bill.id: "ID",
        Bill.bill_date: "账单日期",
        Bill.summary: "摘要",
        Bill.amount: "金额",
        Bill.handle: "是否已结算",
        "user_info": "用户",
    }


class AdminAuth(AuthenticationBackend):
    """
    用于在Admin页面中引入认证机制
    """
    async def login(self, request: Request) -> bool:
        db = SessionLocal()
        form = await request.form()
        username, password = form["username"], form["password"]
        result = crud.authenticate_user(db=db, name=username, hashed_password=password)
        if not result:
            db.close()
            return False
        request.session.update({"token": "youcanuseit"})
        db.close()
        return True

    async def logout(self, request: Request) -> bool:
        # 通常就清除session就可以了
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")
        if not token:
            return False
        if token != "youcanuseit":
            return False
        return True
