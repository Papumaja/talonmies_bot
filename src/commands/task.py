from telegram import Update
from telegram.ext import CallbackContext

from .utils.task import Task
from .utils.warnings import *
from .utils.helpers import *

TASK_HELP_TEXT = """Käyttö: 
    /task create <nimi> <intervalli>
    /task rename <nimi> <uusi nimi>
    /task setinterval <nimi> <intervalli>
    /task setgrace <nimi> <intervalli>
    /task join <nimi>
    /task start <nimi>
    /task stop <nimi>
    /task remove <nimi>
    /task list
"""


async def task_create(update: Update, context):
    args = context.args
    if len(args) != 3:
        await warning_wrong_number_of_args(update, context)
        return

    name, interval_str = args[1:]
    try:
        interval = str_to_time(interval_str)
    except ValueError:
        await context.bot.send_message(chat_id=update.effective_chat.id,
            text="Epähyvä aikamääre")
        return

    if 'tasks' in context.chat_data:
        if name in context.chat_data['tasks']:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                text=f"Tehtävä {name} on jo olemassa!")
            return
        context.chat_data['tasks'][name] = Task(name, interval)
    else:
        context.chat_data['tasks'] = {name: Task(name, interval)}
        context.chat_data['notifications'] = {}
        context.chat_data['scores'] = {}
        context.chat_data['users'] = {}
    await context.bot.send_message(chat_id=update.effective_chat.id,
        text=f"Tehtävä {name} luotu!")
    


async def task_rename(update: Update, context):
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
            await context.bot.send_message(chat_id=update.effective_chat.id,
                text=f"Tehtävä {name} uudelleennimetty {new_name}")
        else:
            await warning_no_task(update, context)
            return
    else:
        await warning_no_tasks(update, context)
        return
        

async def task_remove(update: Update, context):
    args = context.args
    if len(args) != 2:
        await warning_wrong_number_of_args(update, context)
        return

    name = args[1]
    if 'tasks' in context.chat_data:
        if name in context.chat_data['tasks']:
            task = context.chat_data['tasks'].pop(name, None)
            task.stop(context)
            await context.bot.send_message(chat_id=update.effective_chat.id,
                text=f"Tehtävä {name} poistettu.")
        else:
            await warning_no_task(update, context)
            return
    else:
        await warning_no_tasks(update, context)
        return


async def task_setinterval(update: Update, context):
    args = context.args
    if len(args) != 3:
        await warning_wrong_number_of_args(update, context)
        return

    name, interval_str = args[1:]
    try:
        new_interval = str_to_time(interval_str)
    except ValueError:
        await context.bot.send_message(chat_id=update.effective_chat.id,
            text="Epähyvä aikamääre")
        return

    if 'tasks' in context.chat_data:
        if name in context.chat_data['tasks']:
            context.chat_data['tasks'][name].set_interval(new_interval,
                context=context, chat_id=update.effective_chat.id)
            await context.bot.send_message(chat_id=update.effective_chat.id,
                text=f"Tehtävän {name} uusi intervalli on {new_interval}. Seuraava muistutus {new_interval} kuluttua.")
        else:
            await warning_no_task(update, context)
            return
    else:
        await warning_no_tasks(update, context)
        return


async def task_setgrace(update: Update, context):
    args = context.args
    if len(args) != 3:
        await warning_wrong_number_of_args(update, context)
        return

    name, interval_str = args[1:]
    try:
        grace_interval = str_to_time(interval_str)
    except ValueError:
        await context.bot.send_message(chat_id=update.effective_chat.id,
            text="Epähyvä aikamääre")
        return

    if 'tasks' in context.chat_data:
        if name in context.chat_data['tasks']:
            context.chat_data['tasks'][name].grace_period = grace_interval
            await context.bot.send_message(chat_id=update.effective_chat.id,
                text=f"Tehtävän {name} uusi armonaika on {grace_interval}")
        else:
            await warning_no_task(update, context)
            return
    else:
        await warning_no_tasks(update, context)
        return


async def task_join(update: Update, context):
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

        if user.id not in context.chat_data['scores']:
            context.chat_data['scores'][user.id] = 0

        if user.id not in context.chat_data['users']:
            context.chat_data['users'][user.id] = user.name

        if name in context.chat_data['tasks']:
            context.chat_data['tasks'][name].add_user(user)
            await context.bot.send_message(chat_id=update.effective_chat.id,
                text=f"Tervetuloa, {user.name}. Olette nyt vastuussa tehtävässä \"{name}\"")
        else:
            await warning_no_task(update, context)
            return
    else:
        await warning_no_tasks(update, context)
        return


async def task_start(update: Update, context):
    args = context.args
    if len(args) != 2:
        await warning_wrong_number_of_args(update, context)
        return
    
    if update.effective_user.first_name == 'Lauri':
        await context.bot.send_message(chat_id=update.effective_chat.id,
            text=f"Haista Lauri vittu")
        return

    name = args[1]
    if 'tasks' in context.chat_data:
        if name in context.chat_data['tasks']:
            if context.chat_data['tasks'][name].running:
                await context.bot.send_message(chat_id=update.effective_chat.id,
                    text=f"Tehtävä on jo käynnissä.")
                return

            context.chat_data['tasks'][name].start(context, update.effective_chat.id)
            interval = context.chat_data['tasks'][name].interval
            await context.bot.send_message(chat_id=update.effective_chat.id,
                text=f"Tehtävä {name} aloitettu. Seuraava muistutus {interval} kuluttua.")
        else:
            await warning_no_task(update, context)
            return
    else:
        await warning_no_tasks(update, context)
        return


async def task_hetinyt(update: Update, context):
    args = context.args
    if len(args) != 2:
        await warning_wrong_number_of_args(update, context)
        return

    name = args[1]
    if 'tasks' in context.chat_data:
        if name in context.chat_data['tasks']:
            context.chat_data['tasks'][name].now(context, update.effective_chat.id)
        else:
            await warning_no_task(update, context)
            return
    else:
        await warning_no_tasks(update, context)
        return


async def task_stop(update: Update, context):
    args = context.args
    if len(args) != 2:
        await warning_wrong_number_of_args(update, context)
        return

    name = args[1]
    if 'tasks' in context.chat_data:
        if name in context.chat_data['tasks']:
            context.chat_data['tasks'][name].stop(context)
            await context.bot.send_message(chat_id=update.effective_chat.id,
                text=f"Tehtävä {name} pysäytetty.")
        else:
            await warning_no_task(update, context)
            return
    else:
        await warning_no_tasks(update, context)
        return


async def task_list(update: Update, context):
    args = context.args
    if len(args) != 1:
        await warning_wrong_number_of_args(update, context)
        return

    if 'tasks' in context.chat_data:
        tasks = context.chat_data['tasks'].values()
        tasks_strs = [f'  Nimi: {t.name}\n  '\
            +f'Intervalli: {t.interval}\n  '\
            +f'Ajossa: {str(t.running)}\n  '\
            +f'Käyttäjät: {", ".join([u.first_name for u in t.users])}'\
                for t in tasks]
        list_str = \
            "Lista taskeista:\n----------\n"\
           +"\n----------\n".join(tasks_strs)
        
        await context.bot.send_message(chat_id=update.effective_chat.id,
            text=list_str)

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
    'remove': task_remove,
    'hetinyt': task_hetinyt,
    'list': task_list
}
async def cmd_task(update: Update, context):
    args = context.args
    if len(args) == 0:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=TASK_HELP_TEXT)
        return
    
    if args[0] in COMMANDS:
        await COMMANDS[args[0]](update, context)