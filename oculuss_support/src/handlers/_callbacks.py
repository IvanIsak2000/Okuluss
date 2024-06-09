from aiogram import Router
from aiogram import types

from utils.logging.logger import logger

from utils.db.models import get_moderators

router = Router()


@router.callback_query(
    lambda d: d.data.startswith('selected:Поддержка'))
async def support_func(callback: types.CallbackQuery):
    logger.info(
        f'Пользователь (id={callback.from_user.id}) выбрал поддержку',
        extra={
            'user_id': callback.from_user.id,
            'nickname': callback.from_user.username,
            'full_name': callback.from_user.full_name,
            'premium': callback.from_user.is_premium})
    messages = await get_moderators(
        message=callback)
    await callback.message.answer(
        text=f'Модераторы: \n{messages}')
