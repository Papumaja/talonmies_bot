from telegram import Update
from telegram.ext import CallbackContext

from .utils.task import Task
from .utils.warnings import *
from .utils.helpers import *

TASK_HELP_TEXT = """Käyttö: 
    /task create <nimi> <intervalli>
    /task rename <nimi> <uusi nimi>
    /task setinterval <nimi> <intervalli>
    /task join <nimi>
    /task start <nimi>
    /task stop <nimi>
    /task remove <nimi>
"""


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