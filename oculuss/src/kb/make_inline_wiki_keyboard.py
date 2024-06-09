from aiogram import types
from aiogram.types import InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from utils.logging.logger import logger



async def remove_symbols(item: str):
    return "".join([i for i in item if i.isdigit() or i.isalpha()])


async def make_under_supplementation_keyboard(
    message = None,
    callback = None):
    if message:
        await logger.info(f'текст сообщения для кнопок {message.text}')
        reaction = ['👍', '👎']

        builder = InlineKeyboardBuilder()
        builder.row(
            types.InlineKeyboardButton(
                text=reaction[0], callback_data=f'react:{reaction[0]},{message.text}'),
            types.InlineKeyboardButton(
                text=reaction[1], callback_data=f'react:{reaction[1]},{message.text}'))
        builder.row(
            InlineKeyboardButton(
                text='💊 Поиск по добавкам',
                switch_inline_query_current_chat='wiki'))
        builder.row(
            InlineKeyboardButton(
                text='🔙 К меню',
                callback_data=f'menu')
        )
        return builder.as_markup()
    else:
        await logger.info(f'текст сообщения для кнопок {callback.data}')
        reaction = ['👍', '👎']

        builder = InlineKeyboardBuilder()
        builder.row(
            types.InlineKeyboardButton(
                text=reaction[0], callback_data=f'react:{reaction[0]},{callback.data}'),
            types.InlineKeyboardButton(
                text=reaction[1], callback_data=f'react:{reaction[1]},{callback.data}'))
        builder.row(
            InlineKeyboardButton(
                text='💊 Поиск по добавкам',
                switch_inline_query_current_chat='wiki'))
        builder.row(
            InlineKeyboardButton(
                text='🔙 К меню',
                callback_data=f'menu')
        )
        return builder.as_markup()


async def make_inline_wiki_keyboard():
    builder = InlineKeyboardBuilder()

    builder.row(
        types.InlineKeyboardButton(
            text='💊 Поиск по добавкам',
            switch_inline_query_current_chat='wiki'
            )
    )
        
    builder.row(
        types.InlineKeyboardButton(
            text='⚗️ Топ БАДов',
            callback_data='top'
            )
    )

    builder.row(
        types.InlineKeyboardButton(
            text='🔙 К меню',
            callback_data=f'menu'
            )
    )
    return builder.as_markup()