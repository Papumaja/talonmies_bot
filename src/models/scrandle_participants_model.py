from typing import Optional, TYPE_CHECKING
from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel, Relationship


if TYPE_CHECKING:
    from .scran_model import Scran
    from .scrandle_games_model import ScrandleGame


class ScrandleParticipantBase(SQLModel):
    score: int = 0
    is_winner: bool = False


class ScrandleParticipant(ScrandleParticipantBase, table=True):
    __table_args__ = (
        UniqueConstraint("scran_id", "game_id"),
        # ForeignKeyConstraint(["scran_id", "game_id"], ["scran.id", "scrandlegame.id"]),
    )
    id: Optional[int] = Field(default=None, primary_key=True)
    scran_id: Optional[int] = Field(default=None, foreign_key="scran.id")
    scran: Optional["Scran"] = Relationship(back_populates="participating")

    game_id: Optional[int] = Field(default=None, foreign_key="scrandlegame.id")
    game: Optional["ScrandleGame"] = Relationship(back_populates="participants")
