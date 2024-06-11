import aiogram
from aiogram import Router, F
from aiogram import types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext


from utils.logging.logger import logger
from utils.db.settings import get_moderators
from utils.db.achievements import get_my_achievements
from utils.other.emoji import send_emoji


router = Router()



@router.callback_query(
    lambda d: d.data.startswith('selected:achievements'))
async def all_achievements(
        callback: types.CallbackQuery):
    await send_emoji(
        callback=callback,
        emoji='🏆'
    )
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
                                text='< Обратно',
                                callback_data='menu')]
                    ]
                )
    )
    

@router.callback_query(
    lambda d: d.data.startswith('пропустить'))
async def pass_callback(
        callback: types.CallbackQuery,
        state: FSMContext):
    await send_emoji(
        callback=callback,
    )
    await state.clear()
    await callback.message.delete()


@router.message(
    F.text.startswith('пропустить'))
async def pass_message(
        message: types.Message,
        state: FSMContext,
        bot: aiogram.Bot):
    await send_emoji(
        message=message,

    )

    await state.clear()
    await message.delete()
    await bot.delete_message(
        chat_id=message.chat.id,
        message_id=message.message_id-1
    )
