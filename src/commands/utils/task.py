import random
import datetime

from telegram import constants, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from scoreboard import get_xp


async def clear_notification(context: CallbackContext, notification_id):
    if notification_id not in context.chat_data['notifications']: return

    notification = context.chat_data['notifications'].pop(notification_id)
    user = notification['user']
    message = notification['message']

    await context.bot.edit_message_text(
        text=f"{user.mention_markdown_v2(name=user.name)} ei saavutettu\.",
        parse_mode=constants.ParseMode.MARKDOWN_V2,
        chat_id=context.job.data[1],
        message_id = message.message_id
    )

    resend_job_name = notification['resend_job']
    resend_jobs = context.job_queue.get_jobs_by_name(resend_job_name)
    if len(resend_jobs) > 0:
        [job.schedule_removal() for job in resend_jobs]


async def send_reminder(context: CallbackContext):
    task = context.job.data[0]
    chat_id = context.job.data[1]
    n_users = len(task.users)
    if n_users < 1:
        return
    if task.currentIndex >= n_users:
        task.currentIndex = 0

    # If there is a pending previous reminder, clear it
    if task.previous_notification is not None:
        if task.previous_notification in context.chat_data['notifications']:
            await clear_notification(context, task.previous_notification)

    user = task.users[task.currentIndex]
    buttons = [[
        InlineKeyboardButton("Ei pysty!", callback_data="n"),
        InlineKeyboardButton("Eiku", callback_data="e"),
        InlineKeyboardButton("Hoidossa!", callback_data="y")
    ]]
    message = await context.bot.send_message(chat_id=chat_id,
        text=f"{user.mention_markdown_v2(name=user.name)}, {task.name} vaatii huomiotasi\!",
        parse_mode=constants.ParseMode.MARKDOWN_V2,
        reply_markup=InlineKeyboardMarkup(buttons))
    # Resend the reminder after the grace period ends
    resend_job = context.job_queue.run_once(send_reminder, task.grace_period,
        chat_id=chat_id, name=f'{message.message_id}_resend')
    context.chat_data['notifications'][message.message_id] = {
        'message': message, 'task': task, 'user': user, 'resend_job': resend_job.name
    }
    task.previous_notification = message.message_id

    task.currentIndex += 1


class Task:

    def __init__(self, name, interval):
        self.name = name
        self.set_interval(interval)
        self.users = []
        self.currentIndex = 0
        self.running = False
        self.previous_notification = None
        self.job = None

    def get_score(self):
        return random.randint(50, self.score_value)
    
    def set_interval(self, interval, context=None, chat_id=None):
        self.interval = interval
        # TODO: Command for setting grace period separatedly
        self.grace_period = datetime.timedelta(minutes=5) # Default of 5 minutes
        if self.grace_period > self.interval: self.grace_period = self.interval / 2
        # Gamification score
        self.score_value = get_xp(self.interval.total_seconds())

        # Restart the job
        if context is not None and chat_id is not None:
            self.stop(context)
            self.start(context, chat_id)
    
    def add_user(self, user):
        self.users.append(user)
    
    def start(self, context, chat_id):
        job = context.job_queue.run_repeating(send_reminder, self.interval, data=[self, chat_id], chat_id=chat_id)
        self.job = job.name
        self.running = True
    
    def now(self, context, chat_id):
        context.job_queue.run_once(send_reminder, 0, data=[self, chat_id], chat_id=chat_id)

    def get_job(self, context):
        jobs = context.job_queue.get_jobs_by_name(self.job)
        if len(jobs) < 1:
            self.job = None
            return None
        else:
            return jobs[0]
    
    def stop(self, context):
        if self.get_job(context) is not None:
            self.get_job(context).schedule_removal()
        if self.previous_notification is not None:
            context.job_queue.run_once(lambda ctx: clear_notification(*(ctx.job.data)), 0, data=[context, self.previous_notification])
                
        self.running = False
