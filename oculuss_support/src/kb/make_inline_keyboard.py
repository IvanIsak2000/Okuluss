from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types

from utils.texts import (
    prices,
    article_link
)


async def make_inline_keyboard(items: list):
    """Построить базовую клавиатуру"""
    builder = InlineKeyboardBuilder()
    for item in items:
        builder.row(types.InlineKeyboardButton(
            text=item,
            callback_data=f'selected:{"".join([i for i in item if i.isdigit() or i.isalpha()])}')
        )
    return builder.as_markup()


async def make_buy_inline_keyboard():
    """Построить клавиатуру покупки"""
    items = prices
    builder = InlineKeyboardBuilder()
    for item in items:
        builder.row(types.InlineKeyboardButton(
            text=item,
            callback_data=f'payment_by:{"".join([i for i in item if i.isdigit() or i.isalpha()])}')
        )
    return builder.as_markup()


async def make_link_keyboard():
    """Построить клавиатуру на ссылку о том, как посмотреть хэш и в конце клава поддержки
    """
    
    items = ['Поддержка']
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(
        text='Как посмотреть хэш?',
        url=article_link))
    for item in items:
        builder.row(types.InlineKeyboardButton(
            text=item,
            callback_data=f'selected:{"".join([i for i in items if i.isdigit() or i.isalpha()])}')
        )
    return builder.as_markup()


async def make_support_keyboard():
    """Создает клавиатуру поддержки"""
    items = ['Поддержка']
    builder = InlineKeyboardBuilder()
    for item in items:
        builder.row(types.InlineKeyboardButton(
            text=item,
            callback_data=f'selected:{"".join([i for i in item if i.isdigit() or i.isalpha()])}')
        )
    return builder.as_markup()


async def make_under_menu_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text='Продолжай',
            callback_data='support'
        )

    )
