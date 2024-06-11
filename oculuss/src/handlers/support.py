import aiogram
from aiogram import Router, F
from aiogram import types
from aiogram.filters import StateFilter


from utils.logging.logger import logger
from utils.db.settings import get_moderators
from utils.other.emoji import send_emoji


router = Router()


@router.callback_query(
    StateFilter(None),
    lambda d: d.data.startswith('selected:Поддержка'))
async def support_func(callback: types.CallbackQuery):

    await callback.message.answer(
        text=f'Модераторы: \n{await get_moderators(message=callback)}',
        reply_markup=types.InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            types.InlineKeyboardButton(
                                text='< Обратно',
                                callback_data='menu')
                        ]
                    ]
                )
            )