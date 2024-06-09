from aiogram import types
from aiogram.types import InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from utils.db.stack import (
    stack_is_exist,
    get_supplementation_from_stack,
    get_stack_link
)

from utils.db.build_in_supplementation import (
    get_supplementation_id_by_name
)


async def make_under_stack_keyboard(
    stack_title: str
):

    builder = InlineKeyboardBuilder()

    supplementation = await get_supplementation_from_stack(
        stack_title=stack_title
    )

    for i in supplementation:
        builder.row(
            types.InlineKeyboardButton(
                text=i,
                callback_data=f'id:{await get_supplementation_id_by_name(name=i)}'
            )
        )
    builder.row(
        types.InlineKeyboardButton(
            text='📦 Заказать весь стак',
            url=await get_stack_link(title=stack_title)
        )
    
    )
    return builder.as_markup()

