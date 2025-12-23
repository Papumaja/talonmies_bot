from typing import Optional, List, TYPE_CHECKING

from sqlmodel import Field, SQLModel, Relationship


if TYPE_CHECKING:
    from .scran_model import Scran


class UserBase(SQLModel):
    first_name: str | None = ""
    username: str | None = ""


class User(UserBase, table=True):
    __tablename__ = "user"
    id: Optional[int] = Field(default=None, primary_key=True)
    # user_groups: List["UserGroup"] = Relationship(
    #    back_populates="members",
    #    link_model=UserGroupMembersLink,
    # )
    # game_sessions: List["GameSession"] = Relationship(
    #    back_populates="participants",
    #    link_model=SessionParticipantsLink,
    # )
    scrans: List["Scran"] = Relationship(back_populates="user")
