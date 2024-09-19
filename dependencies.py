from datetime import timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt import InvalidTokenError
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from sql_app import crud, schemas
from sql_app.database import SessionLocal

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, crud.SECRET_KEY, algorithms=[crud.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无法验证凭据",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token_data = schemas.TokenData(username=username)
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无法验证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = crud.authenticate_user(db, name=token_data.username)
    if not user["status"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=user["message"],
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user["user"]

async def get_current_active_user(
    current_user: schemas.UserBase = Depends(get_current_user),
):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="非活跃用户")
    return current_user