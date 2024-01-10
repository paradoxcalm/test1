from wbnotifierbot.db import execute, fetch_one


async def is_user_admin(telegram_user_id: int) -> bool:
    is_admin = await fetch_one(
        "select is_admin from bot_users where telegram_user_id=:telegram_user_id",
        {"telegram_user_id": telegram_user_id},
    )
    if is_admin is None:
        is_admin = False
        await execute(
        "insert or ignore into bot_users (telegram_user_id) values (:telegram_user_id)",
        {"telegram_user_id": telegram_user_id},
        autocommit=True
        )
    return is_admin['is_admin']
