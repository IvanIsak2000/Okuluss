from aiogram import Router
from aiogram import types
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from utils.db.stack import (
    stack_is_exist,
    get_stack_description
)
from kb.stack_keyboard import make_under_stack_keyboard
from utils.other.emoji import send_emoji

router = Router()


@router.message()
async def stack_handler(message: types.Message):
    if await stack_is_exist(title=message.text):
        stack_description = await get_stack_description(title=message.text)
        await send_emoji(
            message=message,
            emoji='🧰'

        )
        await message.answer(
            text=stack_description,
            reply_markup=await make_under_stack_keyboard(
                stack_title=message.text
                )
            )
                
