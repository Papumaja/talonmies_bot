from sqlmodel import create_engine, SQLModel, Session, Relationship
import functools
from .models.scran_model import Scran
from .models.scrandle_games_model import ScrandleGame
from .models.scrandle_participants_model import ScrandleParticipant
from .models.user_model import User

sqlite_file_name = "database.db"

db_url = f"sqlite:///{sqlite_file_name}"

engine_args = {"connect_args": {"check_same_thread": False}}

engine = create_engine(db_url, pool_size=20, **engine_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    return Session(engine)


def inject_session(fn):

    @functools.wraps(fn)
    async def wrapper(*args, **kwargs):
        with get_session() as s:
            kwargs["session"] = s
            return await fn(*args, **kwargs)

    return wrapper
