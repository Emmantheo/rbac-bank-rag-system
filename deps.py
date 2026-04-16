from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.security import decode_access_token, security_scheme
from db.session import get_db
from models.user import User


def get_current_user(credentials=Depends(security_scheme), db: Session = Depends(get_db)) -> User:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='missing token')

    payload = decode_access_token(credentials.credentials)
    username = payload.get('sub')
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='invalid token payload')

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='user not found')
    return user
