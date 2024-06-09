from aiogram import Router, F
from aiogram import types
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
import redis

from kb.make_inline_keyboard import (
    make_inline_keyboard_to_timetable, 
    make_menu
)
from kb.make_keyboard import make_keyboard
from kb.make_inline_wiki_keyboard import make_inline_wiki_keyboard
from kb.make_inline_keyboard import (
    make_support_keyboard,
    # make_only_course_managing_keyboard,
    # make_stacks_keyboard,
    make_link_to_profile_article,
    make_knowledge_keyboard,
    make_to_menu_keyboard
)
from utils.texts import (
    welcome_main,
    for_wiki,
    timetable_info,
    course_info,
    help_info,
    you_are_not_access_user
)
from utils.db.rating import get_supplementation_rating
from utils.db.user import get_user_experience
from utils.db.accept_record import get_user_accept_history
from utils.db.user import get_user_position_by_experience
from utils.db.stack import get_stacks_titles


router = Router()


@router.message(
    Command('menu'),
    StateFilter(None))
async def menu(message: types.Message, state: FSMContext):
    """Start main handler"""

    await state.clear()
    await message.answer(
        welcome_main.format(
            name=message.from_user.first_name),
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=await make_menu()
    )


@router.callback_query(
    F.data == 'menu'
)
async def show_menu(callback: types.CallbackQuery, state: FSMContext):
    """Show menu"""
    await state.clear()
    await callback.message.answer(
        text=welcome_main.format(
            name=callback.from_user.first_name),
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=await make_menu()    
    )

@router.callback_query(
    F.data == 'profile'
)
async def profile(callback: types.CallbackQuery, state: FSMContext):
    """Вся информация о юзере"""

    await state.clear()
    result = await get_user_accept_history(user_id=callback.from_user.id)
    try:
        percent = result["successful"] / result["common"]*100
    except ZeroDivisionError:
        percent = 0
    await callback.message.edit_text(
        text=f'''
👤 Твой ID: <u>{callback.from_user.id}</u>
🎓 Уровень: {1}
🌀 Опыт: <u>{await get_user_experience(user_id=callback.from_user.id)}</u>
📈 Приёмы: {int(percent)}% ({result["successful"]}✅  {result["passed"]}❌  {result["common"]}⚪ )

🌍 Место: <u>{await get_user_position_by_experience(user_id=callback.from_user.id)}</u>
🏆 Звание <u>Бегемотыч</u>
''',
        parse_mode=ParseMode.HTML,
        reply_markup=await make_link_to_profile_article()
    )


@router.callback_query(
    F.data == 'wiki'
)
async def wiki(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        text=for_wiki,
        reply_markup=await make_inline_wiki_keyboard()
    )


@router.callback_query(
    F.data == 'top'
)
async def _top(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        text=f'''
🔥 Рейтинг БАДов. Голосуйте за свою любимые БАДы в меню wiki\n
{await get_supplementation_rating()}''',
        reply_markup=await make_to_menu_keyboard())


@router.callback_query(
    F.data == 'knowledge'
)
async def knowledge(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        text='🧠 Проверь себя...',
        reply_markup=await make_knowledge_keyboard()
)


@router.callback_query(
    F.data == 'timetable')
async def timetable(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    """Show timetable for user"""
    await callback.message.edit_text(
        text=timetable_info,
        reply_markup=await make_inline_keyboard_to_timetable(user_id=callback.from_user.id),
        parse_mode=ParseMode.MARKDOWN
    )


# @router.callback_query(
#     
#     StateFilter(None),
#     Command('course'))
# async def _course(callback: types.CallbackQuery):
#     await callback.message.edit_text(
#         text=course_info,
#         reply_markup=await make_only_course_managing_keyboard())


@router.callback_query(
    F.data == 'stacks'
)
async def _stacks(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()

    await callback.message.answer(
        text='🧰 Самые полезные стаки, которые только можно найти (смотри клавиатуру)',
        reply_markup=await make_keyboard(
            items=await get_stacks_titles()))


@router.callback_query(
    F.data == 'feedback'
)
async def _help(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        text=help_info,
        reply_markup=await make_support_keyboard()
    )
