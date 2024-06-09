from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from typing import Callable, Dict, Any, Awaitable

from utils.db.user import is_banned_user
from utils.logging.logger import logger


class MessageLoggingMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]) -> Any:
        await logger.info(
            message=f'event.text: {event.text} от id={event.from_user.id}, username={event.from_user.username}',
            extra={
                'user_id': event.from_user.id,
                'username': event.from_user.username,
                'first_name': event.from_user.first_name,
                'last_name': event.from_user.last_name})
        return await handler(event, data)
