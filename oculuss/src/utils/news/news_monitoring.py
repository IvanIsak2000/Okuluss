import aiogram
from aiogram import types
from aiogram.enums import ParseMode
from datetime import datetime
import random
import asyncio

from utils.logging.logger import logger
from utils.db.user import (
    get_access_users,
    is_access_user,
    is_banned_user
)
from utils.db.news import (
    get_news, 
    news_was_posted
)


class NewsMonitoring():
    def __init__(self, bot: aiogram.Bot, dp: aiogram.Dispatcher):
        self.bot = bot
        self.dp = dp
                
    async def send_news(self, user_id: int, text: str):
        await self.bot.send_message(
            chat_id=user_id, 
            text=text, 
            parse_mode=ParseMode.HTML
        )
        await logger.info(f'Новость отправлена для {user_id}')
                    

    async def news_monitoring(self):
        # targets = await get_access_users()
        targets = [5261974343, 5818860026]
        news = await get_news()
        if news is not None:
            await logger.info(f'news is {news}')
            for target in targets:
                await asyncio.sleep(0.1)
                if await is_access_user(user_id=target):
                    if not await is_banned_user(user_id=target):
                        await self.send_news(
                            user_id=target, 
                            text=news.text
                        )

            await news_was_posted(
                news_id=news.id
            )
