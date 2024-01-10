from typing import cast, TextIO

import telegram
from telegram import Chat, ReplyKeyboardMarkup, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes


async def send_response(
    response: str,
    document: TextIO | None = None,
    update: Update| None = None,
    context: ContextTypes.DEFAULT_TYPE| None = None,
    chat_id: int | None = None,
    inline_keyboard: InlineKeyboardMarkup | None = None,
    reply_keyboard: ReplyKeyboardMarkup | None = None,
) -> None:
    if document is None:
        if chat_id is None:
            args = {
                "chat_id": _get_chat_id(update),
                "disable_web_page_preview": False,
                "text": response,
                "parse_mode": telegram.constants.ParseMode.HTML,
            }
        else:
            args = {
                "chat_id": chat_id,
                "disable_web_page_preview": False,
                "text": response,
                "parse_mode": telegram.constants.ParseMode.HTML,
            }
        if inline_keyboard:
            args["reply_markup"] = inline_keyboard
        elif reply_keyboard:
            args["reply_markup"] = reply_keyboard
        await context.bot.send_message(**args)
    else:
        if chat_id is None:
            args = {
                "chat_id": _get_chat_id(update),
                "document": document,
                "caption": response,
                "parse_mode": telegram.constants.ParseMode.HTML,
            }
        else:
            args = {
                "chat_id": chat_id,
                "document": document,
                "caption": response,
                "parse_mode": telegram.constants.ParseMode.HTML,
            }
        if inline_keyboard:
            args["reply_markup"] = inline_keyboard
        elif reply_keyboard:
            args["reply_markup"] = reply_keyboard
        
        await context.bot.send_document(**args)

def _get_chat_id(update: Update) -> int:
    return cast(Chat, update.effective_chat).id
