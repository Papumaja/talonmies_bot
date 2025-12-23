from typing import Optional, List, TYPE_CHECKING, Dict, Any

from sqlmodel import Field, SQLModel, Relationship, Column, BINARY


if TYPE_CHECKING:
    from .user_model import User
    from .scrandle_participants_model import ScrandleParticipant


class ScranBase(SQLModel):
    message: str | None = ""
    image_name: str = ""
    img_hash: bytes = Field(
        sa_column=Column(BINARY, unique=True, index=True, default=None)
    )
    file_id: str = ""


class Scran(ScranBase, table=True):
    __tablename__ = "scran"
    id: Optional[int] = Field(default=None, primary_key=True)

    # in which chat scran was posted
    chat_id: Optional[int] = Field(default=None, index=True)

    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    user: Optional["User"] = Relationship(back_populates="scrans")

    participating: List["ScrandleParticipant"] = Relationship(
        sa_relationship_kwargs={"cascade": "all,delete,delete-orphan"},
        back_populates="scran",
    )
