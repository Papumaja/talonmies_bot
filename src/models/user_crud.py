from typing import List, Tuple
from sqlmodel import Session, select, and_, asc, desc
from pydantic import ValidationError

from .user_model import User


def create_user(session: Session, user_id: int, username: str, firstname: str) -> User:

    user = None
    try:
        user = User(id=user_id, username=username, first_name=firstname)
    except ValidationError as e:
        raise e

    session.add(user)
    session.commit(user)
    session.refresh(user)
    return user


def create_user(session: Session, user: User) -> User:
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def get_user(session: Session, user_id: int) -> User | None:
    return session.get(User, user_id)
