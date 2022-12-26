from datetime import timedelta
from telegram import Update, constants
from telegram.ext import CallbackContext
from .utils.task import send_reminder

async def button_handler(update: Update, context: CallbackContext.DEFAULT_TYPE):
    query = update.callback_query
    msg_id = query.message.message_id
    if msg_id not in context.chat_data['notifications']:
        return

    data = context.chat_data['notifications'][msg_id]
    await query.answer()
    if query.from_user.id == data['user'].id:
        # Cancel reminder job for this notification
        resend_job_name = data['resend_job']
        resend_jobs = context.job_queue.get_jobs_by_name(resend_job_name)
        if len(resend_jobs) > 0:
            [job.schedule_removal() for job in resend_jobs]
        # Remove the notification as it has been reacted to
        context.chat_data['notifications'].pop(msg_id)

        user = query.from_user
        task = data['task']
        if query.data == 'y':
            if user.id not in context.chat_data['scores']:
                context.chat_data['scores'][user.id] = 0
            context.chat_data['scores'][user.id] += task.score_value
            await query.edit_message_text(
                text=f"Hyvä, {user.mention_markdown_v2(name=user.name)}, hoitaa homman\! :\)\n"
                f" \+ {task.score_value} XP",
                parse_mode=constants.ParseMode.MARKDOWN_V2
            )
        else:
            await query.edit_message_text(
                text=f"{user.mention_markdown_v2(name=user.name)} on estynyt :\(",
                parse_mode=constants.ParseMode.MARKDOWN_V2
            )
            # Send to the next user
            chat_id = query.message.chat_id
            resend_job = context.job_queue.run_once(send_reminder, timedelta(seconds=0), chat_id=chat_id, context=[task, chat_id])

