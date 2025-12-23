from typing import Optional, List, TYPE_CHECKING, Dict, Any
from datetime import datetime, UTC, date

from sqlmodel import Field, SQLModel, Relationship, JSON, Column, func


if TYPE_CHECKING:
    from .user_model import User
    from .scrandle_participants_model import ScrandleParticipant


class ScrandleGameBase(SQLModel):
    pass


class ScrandleGame(ScrandleGameBase, table=True):
    __tablename__ = "scrandlegame"
    id: Optional[int] = Field(default=None, primary_key=True)

    participants: List["ScrandleParticipant"] = Relationship(
        sa_relationship_kwargs={"cascade": "all,delete,delete-orphan"},
        back_populates="game",
    )

    # user_groups: List["UserGroup"] = Relationship(
    #    back_populates="members",
    #    link_model=UserGroupMembersLink,
    # )
    # game_sessions: List["GameSession"] = Relationship(
    #    back_populates="participants",
    #    link_model=SessionParticipantsLink,
    # )
