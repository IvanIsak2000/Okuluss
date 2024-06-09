import aiogram
from aiogram import Router, F
from aiogram import types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext


from utils.logging.logger import logger
from utils.db.settings import get_moderators
from utils.db.achievements import get_my_achievements


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
                                text='🔙 К меню',
                                callback_data='menu')
                        ]
                    ]
                )
            )


# @router.callback_query(
#     StateFilter(None),
#     lambda d: d.data.startswith('selected:Готовые'))
# async def completed_courses_func(
#         callback: types.CallbackQuery):
#     """Select completed courses"""
#     await callback.message.answer(
#         text=completed_courses_info,
#         reply_markup=await make_courses_keyboard())


@router.callback_query(
    lambda d: d.data.startswith('selected:achievements'))
async def all_achievements(
        callback: types.CallbackQuery):
    
    achievements_list = await get_my_achievements(user_id=callback.from_user.id)
    achievement_counts = {}
    for achievement in achievements_list:
        if achievement.achievement in achievement_counts:
            achievement_counts[achievement.achievement] += 1
        else:
            achievement_counts[achievement.achievement] = 1

    achievement_rows = []

    for k, v in achievement_counts.items():
        achievement_rows.append(f'{k} {v} {v * "⭐"}')
                
    await callback.message.answer(
        text='🎖️ Ваши достижения\n\n' + '\n'.join(
            sorted(
                achievement_rows, key=len)),
        reply_markup=types.InlineKeyboardMarkup(
                    inline_keyboard=[[
                            types.InlineKeyboardButton(
                                text='🔙 К меню',
                                callback_data='menu')]
                    ]
                )
    )
    

@router.callback_query(
    lambda d: d.data.startswith('пропустить'))
async def pass_callback(
        callback: types.CallbackQuery,
        state: FSMContext):
    await state.clear()
    await callback.message.delete()


@router.message(
    F.text.startswith('пропустить'))
async def pass_message(
        message: types.Message,
        state: FSMContext,
        bot: aiogram.Bot):

    await state.clear()
    await message.delete()
    await bot.delete_message(
        chat_id=message.chat.id,
        message_id=message.message_id-1
    )
