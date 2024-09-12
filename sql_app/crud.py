from sqlalchemy.orm import Session
from sqlalchemy import extract
import jwt
from jwt.exceptions import InvalidTokenError
from . import models, schemas
from typing import List, Optional, Annotated, Union
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext

# openssl rand -hex 32
SECRET_KEY = "047809efa50356f0eab5db18511142382390d4718b1505e591728dc43004ac29"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """获取hash后的密码"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def authenticate_user(db: Session, name: str, hashed_password: str = None):
    user = db.query(models.User).filter(models.User.name == name).first()
    if not user:
        return False
    if hashed_password is not None:
        print(f"Hashed Password: {hashed_password}")
        print(f"User Password: {user.hashed_password}")
        if not verify_password(hashed_password, user.hashed_password):
            return False
    return user



def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        name=user.name,
        email=user.email,
        hashed_password=get_password_hash(user.hashed_password),  # 使用哈希后的密码
        is_active=user.is_active,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        bills = user.bills
        user.total_positive_amount = sum(
            bill.amount for bill in bills if bill.amount > 0
        )
        user.total_handled_negative_amount = sum(
            bill.amount for bill in bills if bill.amount < 0 and bill.handle
        )
        user.total_unhandled_negative_amount = sum(
            bill.amount for bill in bills if bill.amount < 0 and not bill.handle
        )
        user.balance = (
            user.total_positive_amount
            + user.total_handled_negative_amount
            + user.total_unhandled_negative_amount
        )
    return user


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_bill(db: Session, bill: schemas.BillCreate, user_id: int):
    db_bill = models.Bill(**bill.model_dump())
    db_bill.user_id = user_id
    db_bill.bill_date = datetime.strptime(bill.bill_date, "%Y-%m-%d %H:%M:%S")
    db.add(db_bill)
    db.commit()
    db.refresh(db_bill)
    return db_bill


def get_bills(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Bill).offset(skip).limit(limit).all()


def get_bill(db: Session, bill_id: int):
    return db.query(models.Bill).filter(models.Bill.id == bill_id).first()


def update_bill(db: Session, bill_id: int, bill: schemas.BillUpdate):
    db_bill = db.query(models.Bill).filter(models.Bill.id == bill_id).first()
    if db_bill:
        update_data = bill.model_dump(exclude_unset=True)
        if "bill_date" in update_data:
            update_data["bill_date"] = datetime.strptime(
                update_data["bill_date"], "%Y-%m-%d %H:%M:%S"
            )
        for key, value in update_data.items():
            setattr(db_bill, key, value)
        db.commit()
        db.refresh(db_bill)
    return db_bill


def delete_bill(db: Session, bill_id: int):
    db_bill = db.query(models.Bill).filter(models.Bill.id == bill_id).first()
    if db_bill:
        db.delete(db_bill)
        db.commit()
    return db_bill


def get_user_bills(db: Session, user_id: int, month: int):
    return (
        db.query(models.Bill)
        .filter(
            models.Bill.user_id == user_id,
            extract("month", models.Bill.bill_date) == month,
        )
        .all()
    )
