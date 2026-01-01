from PIL import Image
import imagehash
from sqlmodel import Session
from io import BytesIO
from telegram import Update
from telegram.ext import (
    ContextTypes,
)
from telegram.ext.filters import MessageFilter

from models.scran_crud import is_valid_scran_hash, create_scran
from models.user_model import User
from database import inject_session
from utils.file_handlers import save_image_to_disk


class ScranFilter(MessageFilter):
    def filter(self, message):
        return (
            message.caption != None
            and "👍" in message.caption
            and "👎" in message.caption
        )


@inject_session
async def validate_save_msg_scrans(
    update: Update, context: ContextTypes.DEFAULT_TYPE, session: Session
):
    # Check this in case user adds emojis to image. But should we handle image removal from scran?
    message = update.message if update.message else update.edited_message

    new_file = await message.effective_attachment[-1].get_file()
    image = BytesIO()
    await new_file.download_to_memory(image)
    pil_img = Image.open(image)
    # We actually dont need to do hash at all as telegram provides already unique id for every photo (and does some hash checking for existing photos even when user uploads it again)
    hash = imagehash.average_hash(pil_img)
    if not is_valid_scran_hash(session, hash):
        print("duplicate hash found")
        return
    # save imgage
    img_name = save_image_to_disk(pil_img)
    # create SCRAN!
    create_scran(
        session,
        user=User(
            id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
        ),
        message=message.caption,
        image_hash=hash,
        scran_image_name=img_name,
        chat_id=update.effective_chat.id,
        file_id=message.effective_attachment[-1].file_id,
    )
    print(f"scran created {img_name}")
