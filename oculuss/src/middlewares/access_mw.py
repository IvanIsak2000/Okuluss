from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from typing import Callable, Dict, Any, Awaitable

from utils.db.user import is_access_user
from utils.logging.logger import logger

from utils.texts import you_are_not_access_user


class CheckAccessMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject], Awaitable[Dict[str, Any]]],
            event: TelegramObject,
            data: Dict[str, Any]) -> Any:
        if await is_access_user(user_id=event.from_user.id):
            return await handler(event, data)
        else:
            if event.text in ['/start', '/feedback']:
                return event.answer(text=you_are_not_access_user)
