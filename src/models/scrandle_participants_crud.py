from typing import List, Tuple
from sqlmodel import Session, select, update
from sqlalchemy.orm import aliased


from .scrandle_participants_model import ScrandleParticipant


def check_scran_game_exists(session: Session, scran1_id: int, scran2_id: int) -> bool:
    p1 = aliased(ScrandleParticipant)
    p2 = aliased(ScrandleParticipant)

    stmt = (
        select(1)
        .join(p2, p1.id == p2.id)
        .where(p1.scran_id == scran1_id)
        .where(p2.scran_id == scran2_id)
    )

    has_scran = session.exec(stmt).first()
    return has_scran != None


def update_scran_game_score(
    session: Session, participant_id: int, score: int, is_winner: bool = False
):
    part = session.exec(
        update(ScrandleParticipant)
        .where(ScrandleParticipant.id == participant_id)
        .values(score=score, is_winner=is_winner)
    )
    session.commit()
