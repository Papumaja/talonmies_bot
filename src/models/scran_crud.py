from typing import List, Tuple
from sqlmodel import Session, select, and_, asc, desc
from pydantic import ValidationError
from imagehash import ImageHash

from .scran_model import Scran

from .user_crud import create_user, get_user
from .user_model import User


def create_scran(
    session: Session,
    user: User,
    chat_id: int,
    message: str,
    scran_image_name: str,
    image_hash: ImageHash | bytes,
    file_id: str,
) -> Scran:

    db_user = get_user(session, user.id)
    if db_user == None:
        create_user(session, user)
    if isinstance(image_hash, ImageHash):
        image_hash = bytes.fromhex(str(image_hash))
    scran = None
    try:
        scran = Scran(
            message=message,
            user_id=user.id,
            image_name=scran_image_name,
            img_hash=image_hash,
            chat_id=chat_id,
            file_id=file_id,
        )
    except ValidationError as e:
        raise e

    session.add(scran)
    session.commit()
    session.refresh(scran)
    return scran


def is_valid_scran_hash(session: Session, hash: bytes | ImageHash) -> bool:
    if isinstance(hash, ImageHash):
        hash = bytes.fromhex(str(hash))
    stmt = select(1).where(Scran.img_hash == hash)
    is_scran = session.exec(stmt).first()
    return is_scran == None
