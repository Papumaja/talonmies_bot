from typing import List, Tuple
from sqlmodel import Session, select, and_, col, func, case
from sqlalchemy.orm import aliased


from .scrandle_games_model import ScrandleGame
from .scran_model import Scran
from .user_model import User

from .scrandle_participants_model import ScrandleParticipant


def find_matchup_new_scrans(
    session: Session, chat_id: int
) -> tuple[Scran, Scran] | None:
    scran1 = aliased(Scran)
    scran2 = aliased(Scran)
    subq_participating_scrans = select(ScrandleParticipant.scran_id)

    stmt = (
        select(scran1, scran2)
        .where(col(scran1.id).notin_(subq_participating_scrans))
        .where(col(scran2.id).notin_(subq_participating_scrans))
        .where(scran1.user_id != scran2.user_id)
        .where(scran1.id != scran2.id)
        .where(and_(scran1.chat_id == chat_id, scran2.chat_id == chat_id))
        .limit(1)
    )
    res = session.exec(stmt).first()
    return res


def find_matchup_competed(session: Session, chat_id: int) -> tuple[Scran, Scran] | None:

    # find scran which already competed
    scran_challenger_stmt = (
        select(Scran)
        .outerjoin(ScrandleParticipant, Scran.id == ScrandleParticipant.scran_id)
        .where(Scran.chat_id == chat_id)
        .group_by(Scran.id)
        .order_by(func.count(ScrandleParticipant.scran_id).asc(), func.random())
        .limit(1)
    )

    scran_challenger = session.exec(scran_challenger_stmt).first()
    if scran_challenger == None:
        return None

    challenger_games_subq = select(ScrandleParticipant.game_id).where(
        ScrandleParticipant.scran_id == scran_challenger.id
    )

    past_opponents_subq = select(ScrandleParticipant.scran_id).where(
        col(ScrandleParticipant.game_id).in_(challenger_games_subq)
    )

    Opponent = aliased(Scran)
    stmt = (
        select(Opponent)
        .where(Opponent.user_id != scran_challenger.user_id)
        .where(Opponent.id != scran_challenger.id)
        .where(Opponent.chat_id == chat_id)
        .where(col(Opponent.id).notin_(past_opponents_subq))
        .outerjoin(ScrandleParticipant, Opponent.id == ScrandleParticipant.scran_id)
        .group_by(Opponent.id)
        .order_by(func.count(ScrandleParticipant.game_id).asc())
        .limit(1)
    )
    opponent = session.exec(stmt).first()
    if opponent == None:
        return None
    return (opponent, scran_challenger)


def get_unique_matchup(session: Session, chat_id: int) -> tuple[Scran, Scran] | None:
    # Return None if cant find two unique scrandles for game
    # 1. if scran is not in any game from unique users
    # 2. scran with least games from unique users

    new_matchup_pair = find_matchup_new_scrans(session, chat_id)
    if new_matchup_pair != None:
        return new_matchup_pair

    competed_pair = find_matchup_competed(session, chat_id)
    if competed_pair != None:
        return competed_pair
    return None


def create_scran_match(session: Session, chat_id: int) -> ScrandleGame | None:
    match_scrans = get_unique_matchup(session, chat_id)
    if match_scrans == None:
        return None

    game = ScrandleGame(
        participants=[
            ScrandleParticipant(scran=match_scrans[0]),
            ScrandleParticipant(scran=match_scrans[1]),
        ]
    )
    session.add(game)
    session.commit()
    session.refresh(game)
    return game


def get_scran_results(session: Session, chat_id: int) -> tuple[User, int, int]:
    stmt = (
        select(
            User,
            func.count(
                case((ScrandleParticipant.is_winner == True, 1)),
            ),
            func.count(ScrandleParticipant.game_id),
        )
        .join(Scran, Scran.user_id == User.id)
        .join(ScrandleParticipant, Scran.id == ScrandleParticipant.scran_id)
        .where(Scran.chat_id == chat_id)
        .group_by(User.id)
        .order_by(func.count(case((ScrandleParticipant.is_winner == True, 1))).desc())
    )
    results = session.exec(stmt).all()
    return results
