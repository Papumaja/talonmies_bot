import pytest
import imagehash
from sqlalchemy.orm import selectinload
from unittest.mock import Mock, MagicMock
from sqlmodel import select, Session
from pydantic import ValidationError
from telegram import Chat
from datetime import datetime, timedelta
from PIL import Image
from pathlib import Path
import uuid

from database import *

from models.scran_crud import create_scran, is_valid_scran_hash
from models.user_model import User
from models.scrandle_participants_model import ScrandleParticipant


from models.scrandle_games_crud import get_unique_matchup, create_scran_match
from handlers.scran_reader import validate_save_msg_scrans


def scranmaker(session: Session, user: User, chat=1) -> Scran:
    create_scran(
        session,
        user=user,
        message="asd",
        chat_id=chat,
        scran_image_name="penis.png",
        image_hash=str(uuid.uuid4()).encode(encoding="utf-8"),
    )


def test_get_matchup_new_items(session: Session):
    user = User(username="asd", id=1)
    user2 = User(username="asd2", id=2)

    scranmaker(session, user)
    scranmaker(session, user2)

    first, second = get_unique_matchup(session, 1)
    assert first != second


def test_get_match_fail_already_matched(session: Session):
    user = User(username="asd", id=1)
    user2 = User(username="asd2", id=2)

    scranmaker(session, user)
    scranmaker(session, user2)
    create_scran_match(session, 1)
    create_scran_match(session, 1)
    participants = session.exec(select(ScrandleParticipant)).all()
    assert (
        len(participants) == 2
    ), "Second game not created as not enought scrans available"


def test_get_match_success_already_matched(session: Session):
    user = User(username="asd", id=1)
    user2 = User(username="asd2", id=2)
    user3 = User(username="asd2", id=3)

    scranmaker(session, user)
    scranmaker(session, user2)
    scranmaker(session, user2)
    scranmaker(session, user3)

    create_scran_match(session, 1)
    create_scran_match(session, 1)
    create_scran_match(session, 1)
    create_scran_match(session, 1)
    create_scran_match(session, 1)

    games = session.exec(
        select(ScrandleGame).options(selectinload(ScrandleGame.participants))
    ).all()
    assert len(games) == 5
    # No game should be against self
    for game in games:
        assert game.participants[0].scran.user_id != game.participants[1].scran.user_id
        assert game.participants[0].scran.id != game.participants[1].scran.id


class AsyncMock(MagicMock):
    async def __call__(self, *args, **kwargs):
        return super(AsyncMock, self).__call__(*args, **kwargs)


@pytest.mark.asyncio
async def test_create_scran_bot(session: Session):
    img = Image.open(Path(__file__).resolve().parent / "data/2024-03-22_22-40.png")

    file_mock = AsyncMock(return_value=img)
    get_file = Mock()
    get_file.get_file = file_mock
    update = Mock()
    update.effective_chat.id = 0
    update.message.effective_attachment = [get_file]
    update.message.from_user.id = 0
    update.message.from_user.username = "löslig"
    update.message.from_user.first_name = "kakka"
    await validate_save_msg_scrans.__wrapped__(
        session=session, update=update, context=None
    )

    scran_db = session.exec(select(Scran)).all()
    assert len(scran_db) == 1


def test_scran_hash(session: Session):
    img = Image.open(Path(__file__).resolve().parent / "data/2024-03-22_22-40.png")
    user = User(username="asd", id=1)
    hash = imagehash.average_hash(img)

    create_scran(
        session,
        user=user,
        message="asd",
        chat_id=1,
        scran_image_name="penis.png",
        image_hash=hash,
    )

    assert not is_valid_scran_hash(session, hash)
