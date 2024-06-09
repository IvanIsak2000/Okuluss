from aiogram import Router, F
from aiogram import types
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder

from utils.db.models import (
    add_know_user,
    get_access_user_data
)

from kb.make_inline_keyboard import (
    make_inline_keyboard,
    make_support_keyboard

)
from utils.db.models import is_access_user, add_new_access_user

from utils.logging.logger import logger
from utils.texts import (
    access_info_step_1,
    access_info_step_2,
    welcome_support,
    help_info,
    you_are_access_user,
    you_are_not_access_user
)

router = Router()


@router.message(Command('menu'))
async def menu_handler(message: types.Message):
    await add_know_user(message=message)
    # await add_new_access_user(message=message)
    if await is_access_user(message=message):
        user = await get_access_user_data(message.from_user.id)

        await message.answer(
            text=f'🏆 Ты уже с нами - @OkulussBot\n\nОкончание {user.end_time}'
        )
    else:
        builder = InlineKeyboardBuilder()
        builder.row(
            types.InlineKeyboardButton(
                text='Продолжай...',
                callback_data='next',
            )
        )
        builder.row(
            types.InlineKeyboardButton(
                text='Мне не интересно',
                callback_data='no_interest'
            )
        )
        await message.answer(
            text='''
⚗️ Из каждого утюга кричать БАДы, видишь как каждый 
успешный человек принимает БАДЫ, 
но ТЫ не понимаешь чё за херню они говорят?

🧩 Заебался самостоятельно высматривать по одной 
добавки на миллионе маркетплейсов и неделями ждать, 
чтобы собрать полезный стак?

🔭 Не понимаешь что такое ГАМК? Рапэ? Ежовик?

🥱 Забываешь принять половину своих добавок?

🔔 Не успеваешь отслеживать заканчивающиеся добавки? 

''',    
        reply_markup=builder.as_markup(),
        parse_mode=ParseMode.MARKDOWN_V2)



@router.callback_query(
    F.data == 'no_interest'
)
async def no_interest_handler(callback: types.CallbackQuery):
    await callback.message.answer(
        text='Тогда зачем ты пришёл сюда!? Проваливай, не мешай другим людям.'
    )


@router.callback_query(
    F.data == 'next'
)
async def next_handler(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text='Какое?',
            callback_data='to_access'
        )

    )
    await callback.message.answer(
        text='👀 Превосходно\n\nПоэтому Я хочу предложить тебе особое предложение...',
        reply_markup=builder.as_markup(),
    )


@router.callback_query(
    F.data == 'to_access'
)
async def to_access_handler(callback: types.CallbackQuery):
    builder  = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text='Но, какова цена? Не уж то миллион?',
            callback_data='to_price'
        )
    )
    await callback.message.answer(
        text=access_info_step_1,
        reply_markup=builder.as_markup(),
        parse_mode=ParseMode.HTML
    )


@router.callback_query(
    F.data == 'to_price'
)
async def get_second_access_info_step(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text='Я достоин',
            callback_data='choose_payment'
        )
    )

    await callback.message.answer(
        text=access_info_step_2,
        reply_markup=builder.as_markup()
    )
        