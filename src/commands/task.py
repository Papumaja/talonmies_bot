import datetime

from telegram import Update, constants
from telegram.ext import CallbackContext

TASK_HELP_TEXT = """Käyttö: 
    /task create <nimi> <intervalli>
    /task rename <nimi> <uusi nimi>
    /task setinterval <nimi> <intervalli>
    /task join <nimi>
    /task start <nimi>
    /task stop <nimi>
    /task remove <nimi>
"""

def str_to_time(string: str):
    """Supports formats
    mm:ss
    hh:mm:ss
    dd:hh:mm:ss
    """
    try:
        parts = [int(p) for p in string.split(':')]
    except Exception:
        raise ValueError("Epähyvä aikamääre")

    n_parts = len(parts)
    if n_parts > 4 or n_parts < 2: raise ValueError("Epähyvä aikamääre")
    if n_parts == 2:
        return datetime.timedelta(minutes=parts[0], seconds=parts[1])
    elif n_parts == 3:
        return datetime.timedelta(hours=parts[0], minutes=parts[1], seconds=parts[2])
    elif n_parts == 4:
        return datetime.timedelta(days=parts[0], hours=parts[1], minutes=parts[2], seconds=parts[3])


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


async def warning_wrong_number_of_args(update: Update, context: CallbackContext.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Väärä määrä argumentteja, pöljä.")

async def warning_no_tasks(update: Update, context: CallbackContext.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Ei tehtäviä!")

async def warning_unknown(update: Update, context: CallbackContext.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Häh?")

async def task_create(update: Update, context: CallbackContext.DEFAULT_TYPE):
    args = context.args
    if len(args) != 3:
        await warning_wrong_number_of_args(update, context)
        return

    name, interval_str = args[1:]
    try:
        interval = str_to_time(interval_str)
    except ValueError:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Epähyvä aikamääre")
        return

    if 'tasks' in context.chat_data:
        if name in context.chat_data['tasks']:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Tehtävä {name} on jo olemassa!")
            return
        context.chat_data['tasks'][name] = Task(name, interval)
    else:
        context.chat_data['tasks'] = {name: Task(name, interval)}
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Tehtävä {name} luotu!")
    


async def task_rename(update: Update, context: CallbackContext.DEFAULT_TYPE):
    args = context.args
    if len(args) != 3:
        await warning_wrong_number_of_args(update, context)
        return

    name, new_name = args[1:]
    if 'tasks' in context.chat_data:
        if name in context.chat_data['tasks']:
            task = context.chat_data['tasks'].pop(name, None)
            task.name = new_name
            context.chat_data['tasks'][new_name] = task
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Tehtävä {name} uudelleennimetty {new_name}")
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Tehtävää {name} ei ole olemassa!")
            return
    else:
        await warning_no_tasks(update, context)
        return
        

async def task_remove(update: Update, context: CallbackContext.DEFAULT_TYPE):
    args = context.args
    if len(args) != 2:
        await warning_wrong_number_of_args(update, context)
        return

    name = args[1]
    if 'tasks' in context.chat_data:
        if name in context.chat_data['tasks']:
            task = context.chat_data['tasks'].pop(name, None)
            task.stop()
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Tehtävä {name} poistettu.")
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Tehtävää {name} ei ole olemassa!")
            return
    else:
        await warning_no_tasks(update, context)
        return


async def task_setinterval(update: Update, context: CallbackContext.DEFAULT_TYPE):
    args = context.args
    if len(args) != 3:
        await warning_wrong_number_of_args(update, context)
        return

    name, interval_str = args[1:]
    try:
        new_interval = str_to_time(interval_str)
    except ValueError:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Epähyvä aikamääre")
        return

    if 'tasks' in context.chat_data:
        if name in context.chat_data['tasks']:
            context.chat_data['tasks'][name].set_interval(new_interval)
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Tehtävän {name} uusi intervalli on {new_interval}")
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Tehtävää {name} ei ole olemassa!")
            return
    else:
        await warning_no_tasks(update, context)
        return


async def task_join(update: Update, context: CallbackContext.DEFAULT_TYPE):
    args = context.args
    if len(args) != 2:
        await warning_wrong_number_of_args(update, context)
        return

    name = args[1]
    user = update.effective_user
    if user is None:
        await warning_unknown(update, context)
        return

    if 'tasks' in context.chat_data:
        if name in context.chat_data['tasks']:
            context.chat_data['tasks'][name].add_user(user)
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Tervetuloa, {user.name}. Olette nyt vastuussa tehtävässä \"{name}\"")
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Tehtävää {name} ei ole olemassa!")
            return
    else:
        await warning_no_tasks(update, context)
        return


async def task_start(update: Update, context: CallbackContext.DEFAULT_TYPE):
    args = context.args
    if len(args) != 2:
        await warning_wrong_number_of_args(update, context)
        return

    name = args[1]
    if 'tasks' in context.chat_data:
        if name in context.chat_data['tasks']:
            context.chat_data['tasks'][name].start(context, update.effective_chat.id)
            interval = context.chat_data['tasks'][name].interval
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Tehtävä {name} aloitettu. Seuraava muistutus {interval} kuluttua.")
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Tehtävää {name} ei ole olemassa!")
            return
    else:
        await warning_no_tasks(update, context)
        return


async def task_stop(update: Update, context: CallbackContext.DEFAULT_TYPE):
    args = context.args
    if len(args) != 2:
        await warning_wrong_number_of_args(update, context)
        return

    name = args[1]
    if 'tasks' in context.chat_data:
        if name in context.chat_data['tasks']:
            context.chat_data['tasks'][name].stop()
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Tehtävä {name} pysäytetty.")
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Tehtävää {name} ei ole olemassa!")
            return
    else:
        await warning_no_tasks(update, context)
        return


COMMANDS = {
    'create': task_create,
    'rename': task_rename,
    'setinterval': task_setinterval,
    'join': task_join,
    'start': task_start,
    'stop': task_stop,
    'remove': task_remove
}
async def cmd_task(update: Update, context: CallbackContext.DEFAULT_TYPE):
    args = context.args
    if len(args) == 0:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=TASK_HELP_TEXT)
        return
    
    if args[0] in COMMANDS:
        await COMMANDS[args[0]](update, context)