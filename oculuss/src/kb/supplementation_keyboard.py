from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.keyboard import InlineKeyboardMarkup
from aiogram import types
from typing import Union
from typing import Union

from utils.logging.logger import logger
from utils.db.custom_supplementation import (
    is_active_supplementation, 
    get_user_custom_supplementation
)


async def make_supplementation_keyboard(
    user_id: int) -> Union[bool, InlineKeyboardMarkup]:
    """
    Создать клавиатуру для отображения всех БАДов юзера
    Note: если у юзера нет БАДов, то возвращает False
    """

    items = await get_user_custom_supplementation(user_id=user_id)
    if items == []:
        return False
    else:
        builder = InlineKeyboardBuilder()
        for item in items:
            name = f'{item.name[0:10]}...' if len(item.name) > 10 else f'{item.name}'
            builder.row(types.InlineKeyboardButton(
                text=f'{name} {item.time} {item.dose} {"🟢" if item.is_active else "🔴"}',
                callback_data=f"supplementation:{item.supplementation_hash}"))
        builder.row(types.InlineKeyboardButton(
            text='< Обратно',
            callback_data=f'menu'))
        return builder.as_markup()
 

async def keyboard_for_accepting_supplements(record_hash: str):
    "Создать клаву для принятия/непринятия БАДа"    

    builder = InlineKeyboardBuilder()

    builder.row(
        types.InlineKeyboardButton(
            text='✅ Принял всё',
            callback_data=f'record_of_accept:{record_hash}'),
        types.InlineKeyboardButton(
            text='➡️ Пропустить всё',
            callback_data=f'record_of_pass:{record_hash}')
    )
    return builder.as_markup()


async def keyboard_for_edit_supplementation(
    user_id: int,
    supplementation_hash: str):
    """Клава под БАДом для редактирования"""

    builder = InlineKeyboardBuilder()
    items = supplementation_hash
    if await is_active_supplementation(
        user_id=user_id, 
        supplementation_hash=supplementation_hash):
        builder.row(types.InlineKeyboardButton(
            text="⏸️ Отключить",
            callback_data=f"supplementation_to_turn_off:{supplementation_hash}"))
    else:
        builder.row(types.InlineKeyboardButton(
            text="▶️ Включить",
            callback_data=f"supplementation_to_turn_on:{supplementation_hash}"))

    builder.row(types.InlineKeyboardButton(
        text="🗑️ Удалить",
        callback_data=f"supplementation_to_remove:{supplementation_hash}"))

    builder.row(types.InlineKeyboardButton(
        text="◀️ назад",
        callback_data=f"selected:show_all_supplementation"))
    return builder.as_markup()
