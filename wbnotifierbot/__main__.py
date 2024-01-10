from datetime import time
import logging
import pytz
from telegram import Chat, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    ContextTypes,
    CommandHandler,
    JobQueue,
    MessageHandler,
    filters,
)
from typing import cast
from wbnotifierbot import config, handlers
from wbnotifierbot.db import close_db
from wbnotifierbot.services.wildberries import wildberries 

COMMAND_HANDLERS = {
    "start": handlers.start,
    "help": handlers.help_,
}

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


if not config.TELEGRAM_BOT_TOKEN:
    raise ValueError(
        "env переменная TELEGRAM_BOT_TOKEN  "
        "не объявлена в .env (должна быть!)"
    )

async def callback_automatically(context: ContextTypes.DEFAULT_TYPE):
    data = await wildberries.start_checking(context)

async def callback_manually(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await context.bot.send_message(chat_id=cast(Chat, update.effective_chat).id, text="Начал проверку данных, подождите..")
    data = await wildberries.start_checking(context, chat_id_for_del=cast(Chat, update.effective_chat).id, msg_id_for_del=msg.message_id)
    
def main():
    application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
    job_queue = application.job_queue
    job_queue.run_daily(callback_automatically, time(0,5, tzinfo=pytz.timezone('Europe/Moscow')), days=(0, 1, 2, 3, 4, 5, 6))
    for command_name, command_handler in COMMAND_HANDLERS.items():
        application.add_handler(CommandHandler(command_name, command_handler))
    application.add_handler(MessageHandler(filters.Regex("^Обновить данные"), callback_manually))
    application.run_polling()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        import traceback

        logger.warning(traceback.format_exc())
    finally:
        close_db()
