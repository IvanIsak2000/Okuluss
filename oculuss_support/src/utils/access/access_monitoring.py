from pydantic import BaseModel
import aiogram
import aiogram
from aiogram.utils.text_decorations import html_decoration as hd
from datetime import datetime
import pytz 
import asyncio

from utils.logging.logger import logger
from utils.db.models import (
    get_access_users,
    remove_user_from_access
)
from utils.texts import you_are_not_access_user


async def user_access_is_active(bot: aiogram.client.bot.Bot):
    logger.info(f"Проверка доступов...")

    users = await get_access_users()
    deleted_users = []
    notified_users = [] 
    done_users = []

    users_checked = 0
    
    for i in users:
        await asyncio.sleep(0.5)

        end_time_date = i.end_time
        current_now = datetime.now()
        current_time_str = current_now.strftime("%Y-%m-%d %H:%M:%S")
        current_date = datetime.strptime(current_time_str, "%Y-%m-%d %H:%M:%S")
        diff = (end_time_date - current_date).days

        try:
            if 2 >= diff > 0:
                notified_users.append(i.user_id)
                logger.info(f'👮 Напомнил пользователю({i.user_id}) о окончании подписки {diff} дней')
                await bot.send_message(
                    chat_id=i.user_id,
                    text='❗ Ваша подписка закончится менее чем через 2 дня! Пожалуйста заранее продлите доступ через бота поддержки!'
                )

            if diff <= 0:
                logger.info(f'👮 Удалил подписку {diff} дней у пользователя {i.user_id}')
                deleted_users.append(i.user_id)
                await bot.send_message(
                    chat_id=i.user_id,
                    text=f'❌ Подписка закончилась!\n{you_are_not_access_user}',
                )
                await remove_user_from_access(i.user_id)
            users_checked += 1
        except Exception as e:
            if 'chat not found' in str(e):
                logger.error(f'Чат не найден: {e}, user: {i.user_id}')
                continue
                
    logger.info(
        f"👁️‍🗨️ Проверка доступов завершена завершена. Результаты: {users_checked}/{len(users)}")
