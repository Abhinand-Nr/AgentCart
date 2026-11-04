from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.errors import ConflictError, UnauthorizedError
from app.models import User
from app.security import hash_password, verify_password


def register(db: Session, email: str, password: str) -> User:
    email = email.strip().lower()

    if db.scalar(select(User).where(User.email == email)):
        raise ConflictError("An account with this email already exists")

    user = User(email=email, password_hash=hash_password(password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ConflictError("An account with this email already exists")
    db.refresh(user)
    return user

def authenticate(db: Session, email: str, password: str) -> User:
    user = db.scalar(select(User).where(User.email == email.strip().lower()))
    if user is None or not verify_password(password, user.password_hash):
        raise UnauthorizedError("Wrong email or password")
    return user