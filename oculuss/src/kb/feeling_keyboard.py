from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types


async def make_feeling_keyboard():
    items = [
        '1️⃣',
        '2️⃣',
        '3️⃣',
        '4️⃣',
        '5️⃣'
    ]
    builder = InlineKeyboardBuilder()
    for item in items:
        builder.row(types.InlineKeyboardButton(
            text=item,
            callback_data=f'feeling_rate:{item}')
        )
    builder.row(types.InlineKeyboardButton(
        text='🔙 К меню',
        callback_data=f'menu'))
    return builder.as_markup()

