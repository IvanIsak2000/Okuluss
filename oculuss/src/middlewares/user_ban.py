from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from typing import Callable, Dict, Any, Awaitable

from utils.db.user import is_banned_user
from utils.logging.logger import logger

import asyncio


class CheckUserWasBannedMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]) -> Any:
        user_id = event.from_user.id
        if await is_banned_user(user_id):
            await logger.info(f'Вывел пользователю с id: {user_id}, что он забанен')
            await asyncio.sleep(delay=10)
            await event.answer("🛑 Ваш аккаунт был заблокирован по решению Главнокомандующего 🧙‍♂️")
        else:
            return await handler(event, data)
