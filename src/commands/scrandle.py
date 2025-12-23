from sqlmodel import Session
import re
from pathlib import Path
from telegram import Update, Poll
from PIL import Image
from telegram.helpers import escape_markdown
from telegram.constants import ParseMode
from telegram.ext import (
    ContextTypes,
)
from telegram.error import BadRequest
from ..models.scrandle_games_crud import create_scran_match, get_scran_results
from ..models.scrandle_participants_crud import update_scran_game_score


from ..database import inject_session


@inject_session
async def cmd_scrandle(
    update: Update, context: ContextTypes.DEFAULT_TYPE, session: Session
):
    scrandle = create_scran_match(session, update.effective_chat.id)
    if scrandle == None:
        print("No scrandle candidates found!")
        return

    # Make sure old scran has ended
    await cmd_close_scrandle_poll(update, context)
    vote = []
    questions = []
    # post voted images
    for index, participant in enumerate(scrandle.participants, 1):
        msg = participant.scran.message
        msg = re.sub("(👍|👎)[^]]*(👍|👎)", "", msg)
        # img = load_image_from_diks(participant.scran.image_name)
        # TODO: put to task loop (no awaiting)
        await context.bot.send_photo(
            update.effective_chat.id,
            photo=participant.scran.file_id,
            caption=f"*{index}\\.* {escape_markdown(msg,version=2)}",
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        vote.append(participant.id)
        questions.append(f"{index}. {msg[:40]}")
    # create poll for voting

    poll_msg = await context.bot.send_poll(
        update.effective_chat.id,
        "Kumpi onkaan hyvetimpää?",
        questions,
        is_anonymous=False,
        allows_multiple_answers=False,
    )
    # store poll
    payload = {
        poll_msg.poll.id: {
            "questions": vote,
            "message_id": poll_msg.message_id,
            "chat_id": update.effective_chat.id,
            "answers": {},
        }
    }

    context.bot_data.update(payload)


util_path = Path(__file__).parents[0].resolve() / "utils"


async def cmd_scrandle_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = 'Mättö kuva kisa - Postaa kuva "scranista" ja äänestä herkumpaa!\n\n'
    msg += "Lähetä mieluiten itseotettu kuva herkku mätöstä tähän ryhmään ja laita tekstikenttään emojit 👍/👎 niin olet mukana kisassa.\n\n"
    msg += "Äänestä parempi MÄTTÖ KUVA voittoon! Eniten äänestyksiä voittanut voittaa kompon.\n"
    msg += "Komentoja:\n"
    msg += "/scrandle_top - Näytä pistetilastot\n"
    await context.bot.send_photo(
        update.effective_chat.id,
        caption=msg,
        photo=open(util_path / "mattokuvakisa.jpg", "rb"),
    )


@inject_session
async def handle_scran_poll_update(
    update: Update, context: ContextTypes.DEFAULT_TYPE, session: Session
):
    answer = update.poll_answer
    print("poll update received", answer.option_ids)

    # Store voter and answer. Voter can change answer until poll is closed
    if answer.option_ids:
        context.bot_data[answer.poll_id]["answers"].update(
            {answer.user.id: answer.option_ids[-1]}
        )
    else:
        del context.bot_data[answer.poll_id]["answers"][answer.user.id]

    # Save scores to db when poll is closed


@inject_session
async def cmd_close_scrandle_poll(
    update: Update, context: ContextTypes.DEFAULT_TYPE, session: Session
):
    chat_id = update.effective_chat.id
    # Close poll in that chat (should we check for all polls??)
    poll = next(
        (
            (key, sub)
            for key, sub in context.bot_data.items()
            if sub.get("chat_id") == chat_id
        ),
        None,
    )

    if poll == None:
        return
    poll_id, answered_poll = poll
    try:
        await context.bot.stop_poll(chat_id, answered_poll["message_id"])
    except BadRequest as e:
        # This can be "poll already closed" we dont need to care
        print(e)

    results = [0, 0]  # {[id]: 0 for id in answered_poll["questions"]}
    # count scores
    if isinstance(answered_poll["answers"], dict):
        for answer in answered_poll["answers"].values():
            if answer != None:
                results[answer] += 1

    print(answered_poll)
    # At least 2 answers recorded
    if sum(results) > 1:
        if isinstance(answered_poll["questions"], list):
            for i, res in enumerate(results):
                # If draw, no one wins
                update_scran_game_score(
                    session,
                    answered_poll["questions"][i],
                    score=res,
                    is_winner=(
                        i == results.index(max(results))
                        and not all(results[0] == v for v in results)
                    ),
                )

    del context.bot_data[poll_id]


@inject_session
async def cmd_scrandle_result(
    update: Update, context: ContextTypes.DEFAULT_TYPE, session: Session
):
    stats = get_scran_results(session, update.effective_chat.id)

    msg = "\n".join(
        [
            f"{i}. {user.username} Pisteet: {score}, pelattu: {games_played} kertaa"
            for i, (user, score, games_played) in enumerate(stats, 1)
        ]
    )

    await context.bot.send_message(update.effective_chat.id, text=msg)
