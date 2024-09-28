from telegram import CallbackQuery, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, ConversationHandler, CallbackQueryHandler
import os
import service as svc
import utils
from constants import Encoders, WasherLoad, DryerTime, Status, DEFAULT_CYCLE_TIME

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Start")


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = svc.get_status()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode="HTML")


async def use(update: Update, context: ContextTypes.DEFAULT_TYPE):
    machines = svc.get_machines()
    keyboard = [[InlineKeyboardButton(machine["label"], callback_data=machine["value"])] for machine in machines]
    keyboard.append([InlineKeyboardButton("Cancel", callback_data="cancel")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Please select a machine:", reply_markup=reply_markup)

async def use_machine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    machine = query.data
    machine_label = utils.get_display_label(machine)
    
    await query.answer()
    # TODO: Handle machine error
    if svc.is_machine_in_use(machine):
        # Ask if user is sure they want to override
        keyboard = [[InlineKeyboardButton(f"Use {machine_label}", callback_data=utils.encode_machine(machine, Encoders.CONFIRM_ENCODER))], [InlineKeyboardButton("Cancel", callback_data="cancel")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=f"{machine_label} is currently in use, are you sure you want to override?", reply_markup=reply_markup)
    else:
        await get_cycle_time(update, context, query, machine)

async def get_cycle_time(update: Update, context: ContextTypes.DEFAULT_TYPE, query: CallbackQuery, machine: str):
    if utils.is_washer(machine):
        keyboard = [[InlineKeyboardButton(load.name.capitalize(), callback_data=utils.encode_machine(f"{machine}__{load.name}", Encoders.CYCLE_ENCODER))] for load in WasherLoad]
        keyboard.append([InlineKeyboardButton("Cancel", callback_data="cancel")])
        # Ask for duration
        await query.edit_message_text(text=f"Please select the wash cycle:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif utils.is_dryer(machine):
        keyboard = [[InlineKeyboardButton("{} Minutes".format(time.value), callback_data=utils.encode_machine(f"{machine}__{time.name}", Encoders.CYCLE_ENCODER))] for time in DryerTime]
        keyboard.append([InlineKeyboardButton("Cancel", callback_data="cancel")])
        # Ask for duration
        await query.edit_message_text(text=f"Please select the dryer time:", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await query.edit_message_text(text=f"Error!")

async def confirm_use_machine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    # TODO: Handle machine error
    machine = utils.decode_machine(query.data, Encoders.CONFIRM_ENCODER)
    await query.answer()
    await get_cycle_time(update, context, query, machine)

async def use_machine_helper(update: Update, context: ContextTypes.DEFAULT_TYPE, query: CallbackQuery, machine: str, cycle_time: int = DEFAULT_CYCLE_TIME):
    svc.use_machine(machine, update.effective_chat.id, update.effective_user.username, cycle_time)
    context.job_queue.run_once(alarm, cycle_time * 60, chat_id=update.effective_chat.id, data=machine)
    await query.edit_message_text(text=f"You are now using {utils.get_display_label(machine)}!")

async def set_duration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    res = utils.decode_machine(query.data, Encoders.CYCLE_ENCODER)
    machine, load = res.split("__")
    if utils.is_washer(machine):
        cycle = WasherLoad[load].value
    elif utils.is_dryer(machine):
        cycle = DryerTime[load].value
    else:
        cycle = DEFAULT_CYCLE_TIME
    await query.answer()
    await use_machine_helper(update, context, query, machine, cycle)

async def alarm(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    if svc.is_machine_used_by(job.data, job.chat_id) and svc.is_machine_in_use(job.data):
        svc.set_status(job.data, Status.DONE)
        await context.bot.send_message(chat_id=job.chat_id, text=f'Your laundry in {utils.get_display_label(job.data)} is done!')

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Get all done machines and show options
    machines = svc.get_machines_with_options([Status.DONE])
    if not machines:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="There are no machines that are done!")
        return
    keyboard = [[InlineKeyboardButton(machine["label"], callback_data=utils.encode_machine(machine["value"], Encoders.PING_ENCODER))] for machine in machines]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Please select a machine to ping user:", reply_markup=reply_markup)

async def ping_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    machine = utils.decode_machine(query.data, Encoders.PING_ENCODER)
    user_id = svc.get_user_id(machine)
    await query.answer()
    await context.bot.send_message(chat_id=user_id, text=f"Please clear your laundry in {utils.get_display_label(machine)} immediately as there are other users waiting!")
    await query.edit_message_text(text=f"User has been notified!")


async def done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Show only machines registered to user
    machines = svc.get_machines_with_options([Status.DONE], update.effective_chat.id)
    if not machines:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="There are no machines used by you that are done!")
        return
    keyboard = [[InlineKeyboardButton(machine["label"], callback_data=utils.encode_machine(machine["value"], Encoders.DONE_ENCODER))] for machine in machines]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Please select the machine that you are done using:", reply_markup=reply_markup)

async def done_machine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    machine = utils.decode_machine(query.data, Encoders.DONE_ENCODER)
    svc.set_status(machine, Status.AVAILABLE)
    await query.answer()
    await query.edit_message_text(text=f"Your laundry in {utils.get_display_label(machine)} has been cleared!")

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    machines = svc.get_machines_with_options([Status.IN_USE, Status.DONE], update.effective_chat.id)
    if not machines:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="You are not using any machines!")
        return
    keyboard = [[InlineKeyboardButton(machine["label"], callback_data=utils.encode_machine(machine["value"], Encoders.CLEAR_ENCODER))] for machine in machines]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Please select the machine that you want to cancel:", reply_markup=reply_markup)

async def clear_machine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    machine = utils.decode_machine(query.data, Encoders.CLEAR_ENCODER)
    svc.set_status(machine, Status.AVAILABLE)
    await query.answer()
    await query.edit_message_text(text=f"Your booking of {utils.get_display_label(machine)} has been cleared!")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="Your laundry cycle has been cancelled!")

async def refund(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="To request for a refund, please fill in the form here: https://forms.gle/VrghaVuxPmicVu9b9.")

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="To seek assistance on any Washer & Dryer related issues, please contact Fresh Laundry Pte Ltd at +65 9655 3600 or @freshlaundrysg on Telegram. Alternatively, you can also contact your nearest RA.")

def setup_bot():
    print("Setting up Bot...")
    application = ApplicationBuilder().token(os.getenv("TELEGRAM_TOKEN")).build()
    
    # TODO: Convert to conversation handler
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    status_handler = CommandHandler('status', status)
    application.add_handler(status_handler)

    use_handler = CommandHandler('use', use)
    application.add_handler(use_handler)

    ping_handler = CommandHandler('ping', ping)
    application.add_handler(ping_handler)

    done_handler = CommandHandler('done', done)
    application.add_handler(done_handler)

    clear_handler = CommandHandler('clear', clear)
    application.add_handler(clear_handler)

    refund_handler = CommandHandler('refund', refund)
    application.add_handler(refund_handler)

    help_handler = CommandHandler('help', help)
    application.add_handler(help_handler)

    use_machine_handler = CallbackQueryHandler(use_machine, utils.is_machine)
    application.add_handler(use_machine_handler)

    confirm_use_machine_handler = CallbackQueryHandler(confirm_use_machine, pattern=f"^\\{Encoders.CONFIRM_ENCODER.value}\\w+")
    application.add_handler(confirm_use_machine_handler)

    duration_handler = CallbackQueryHandler(set_duration, pattern=f"^{Encoders.CYCLE_ENCODER.value}\\w+")
    application.add_handler(duration_handler)

    cancel_handler = CallbackQueryHandler(cancel, pattern='cancel')
    application.add_handler(cancel_handler)

    ping_user_handler = CallbackQueryHandler(ping_user, pattern=f"^{Encoders.PING_ENCODER.value}\\w+")
    application.add_handler(ping_user_handler)

    done_machine_handler = CallbackQueryHandler(done_machine, pattern=f"^{Encoders.DONE_ENCODER.value}\\w+")
    application.add_handler(done_machine_handler)

    clear_machine_handler = CallbackQueryHandler(clear_machine, pattern=f"^{Encoders.CLEAR_ENCODER.value}\\w+")
    application.add_handler(clear_machine_handler)

    return application
    
def run_bot_polling():
    application = setup_bot()
    print("Starting Bot...")    
    application.run_polling()

async def process_webhook_update(request):
    application = setup_bot()
    await application.initialize()
    await application.process_update(
        Update.de_json(data=request.get_json(force=True), bot=application.bot)
    )
    await application.shutdown()
    return "OK"

# def run_bot_webhook():
#     setup_bot()
#     print("Starting Bot...")    
#     application.run_webhook()
#     return application.bot
