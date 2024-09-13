from datetime import datetime
from pydantic import BaseModel, model_validator
from typing import Optional, List, Union

class BillBase(BaseModel):
    bill_date: str  # 修改为 bill_date
    summary: str
    amount: float  # 修改为 float
    handle: bool

class BillCreate(BillBase):
    user_id: Optional[int] = None

class BillUpdate(BaseModel):
    bill_date: Optional[str] = None 
    summary: Optional[str] = None
    amount: Optional[float] = None  
    handle: Optional[bool] = None

class Bill(BillBase):
    id: int
    user_id: int  # 添加 user_id
    bill_date: datetime

    class Config:
        from_attributes = True

    @model_validator(mode='after')
    def extract_month_and_date(cls, values):
        if isinstance(values.bill_date, datetime):
            values.bill_date = values.bill_date.strftime("%Y-%m-%d %H:%M:%S")
        return values

class UserBase(BaseModel):
    name: str
    nickname: str
    email: str
    is_active: bool

class UserCreate(UserBase):
    hashed_password: str

class User(UserBase):
    id: int
    bills: List[Bill] = []  # 添加与 Bill 的关系
    # 余额
    balance: Optional[float] = 0
    total_positive_amount: Optional[float] = 0
    total_handled_negative_amount: Optional[float] = 0
    total_unhandled_negative_amount: Optional[float] = 0

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None