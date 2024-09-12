from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Float
from sqlalchemy.orm import relationship

from .database import Base
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    bills = relationship("Bill", back_populates="user")  # 添加与Bill的关系


class Bill(Base):
    __tablename__ = "bills"

    id = Column(Integer, primary_key=True, index=True)  # 主键ID
    bill_date = Column(DateTime, default=datetime.now)  # 创建时间
    summary = Column(String)  # 摘要
    amount = Column(Float)  # 价格，支持正负数
    handle = Column(Boolean, default=False)  # 处理状态，默认为未处理
    user_id = Column(Integer, ForeignKey("users.id"))  # 添加外键

    user = relationship("User", back_populates="bills")  # 添加与User的关系


