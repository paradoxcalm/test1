
from telegram import Chat, ReplyKeyboardMarkup, Update 
from telegram.ext import ContextTypes
from typing import cast
from wbnotifierbot.handlers.response import send_response
from wbnotifierbot.services.check_user_is_admin import is_user_admin
from wbnotifierbot.templates import render_template


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [["Обновить данные🔁"]]
    reply_markup=ReplyKeyboardMarkup(reply_keyboard, is_persistent=True, resize_keyboard=True)
    if await is_user_admin(cast(Chat, update.effective_chat).id) == 1:
        await send_response(response=render_template(
                                            "start_4_admin.j2", 
                                             data={"name":update.message.from_user.username}
                            ),update=update, context=context, reply_keyboard=reply_markup
        )
    else:
        await send_response(response=render_template("start.j2", data={"name":update.message.from_user.username}), update=update, context=context )
