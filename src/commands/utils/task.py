import datetime

from telegram import constants
from telegram.ext import CallbackContext

async def send_reminder(context: CallbackContext):
    task = context.job.context[0]
    chat_id = context.job.context[1]
    n_users = len(task.users)
    if n_users < 1:
        return
    if task.currentIndex >= n_users:
        task.currentIndex = 0

    user = task.users[task.currentIndex]
    await context.bot.send_message(chat_id=chat_id,
                                   text=f"{user.mention_markdown_v2(name=user.name)}, {task.name} vaatii huomiotasi\!",
                                   parse_mode=constants.ParseMode.MARKDOWN_V2)
    
    task.currentIndex += 1


class Task:

    def __init__(self, name, interval):
        self.name = name
        self.set_interval(interval)
        self.users = []
        self.currentIndex = 0
        self.running = False
        self.job = None
    
    def set_interval(self, interval):
        self.interval = interval
        self.grace_period = datetime.timedelta(minutes=5) # Default of 5 minutes
        # TODO: Command for setting grace period separatedly
        if self.grace_period > self.interval: self.grace_period = self.interval
    
    def add_user(self, user):
        self.users.append(user)
    
    def start(self, context, chat_id):
        self.job = context.job_queue.run_repeating(send_reminder, self.interval, context=[self, chat_id], chat_id=chat_id)
        self.running = True
    
    def stop(self):
        if self.job is not None:
            self.job.schedule_removal()
        self.running = False
