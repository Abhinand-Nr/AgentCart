import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.errors import UnauthorizedError
from app.models import User
from app.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    try:
        user_id = decode_access_token(token)
    except jwt.PyJWTError:
        raise UnauthorizedError("Invalid or expired token")

    user = db.get(User, user_id)
    if user is None:
        raise UnauthorizedError("User no longer exists")
    return user