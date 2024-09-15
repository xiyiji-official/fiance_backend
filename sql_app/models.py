from markupsafe import Markup
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Float
from sqlalchemy.orm import relationship

from .database import Base
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    nickname = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    bills = relationship("Bill", back_populates="user")  # 添加与Bill的关系

    @property
    def bill_info(self):
        """
        在Admin页面使用的用于格式化显示账单信息的方法
        """
        table_style = """
        <style>
            .bill-table {
                width: 100%;
                border-collapse: collapse;
            }
            .bill-table th, .bill-table td {
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }
            .bill-table th {
                background-color: #f2f2f2;
            }
            .bill-table tr:nth-child(even) {
                background-color: #f9f9f9;
            }
            .bill-table .action-btn {
                padding: 5px 10px;
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 3px;
                cursor: pointer;
                text-decoration: none;
            }
        </style>
        """

        table = '<table class="bill-table">'
        table += "<tr><th>ID</th><th>日期</th><th>摘要</th><th>金额</th><th>已结算</th><th>操作</th></tr>"

        for bill in self.bills:
            table += "<tr>"
            table += f"<td>{bill.id}</td>"
            table += f'<td>{bill.bill_date.strftime("%Y-%m-%d %H:%M:%S")}</td>'
            table += f"<td>{bill.summary}</td>"
            table += f"<td>¥{bill.amount:.2f}</td>"
            table += f'<td>{"是" if bill.handle else "否"}</td>'
            table += f'<td><a href="/admin/bill/details/{bill.id}" class="action-btn">查看详情</a></td>'
            table += "</tr>"

        table += "</table>"

        return Markup(table_style + table)


class Bill(Base):
    __tablename__ = "bills"

    id = Column(Integer, primary_key=True, index=True)  # 主键ID
    bill_date = Column(DateTime, default=datetime.now)  # 创建时间
    summary = Column(String)  # 摘要
    amount = Column(Float)  # 价格，支持正负数
    handle = Column(Boolean, default=False)  # 处理状态，默认为未处理
    user_id = Column(Integer, ForeignKey("users.id"))  # 添加外键

    user = relationship("User", back_populates="bills")  # 添加与User的关系

    @property
    def user_info(self):
        """
        在Admin页面使用的用于格式化显示用户信息的方法
        """
        table_style = """
        <style>
            .user-table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
            }
            .user-table th, .user-table td {
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }
            .user-table th {
                background-color: #f2f2f2;
            }
        </style>
        """

        table = '<table class="user-table">'
        table += "<tr><th>名字</th><th>昵称</th><th>邮箱</th><th>激活状态</th></tr>"
        table += "<tr>"
        table += f"<td>{self.user.name}</td>"
        table += f"<td>{self.user.email}</td>"
        table += f'<td>{"已激活" if self.user.is_active else "未激活"}</td>'
        table += "</tr>"
        table += "</table>"

        return Markup(table_style + table)
