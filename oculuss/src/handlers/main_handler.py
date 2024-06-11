from aiogram import Router, F
from aiogram import types
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types
from aiogram.types import URLInputFile


from kb.make_inline_keyboard import (
    make_inline_keyboard_to_timetable, 
    make_menu
)
from kb.make_keyboard import make_keyboard
from kb.make_inline_library_keyboard import make_inline_library_keyboard
from kb.make_inline_keyboard import (
    make_support_keyboard,
    make_link_to_profile_article,
    make_knowledge_keyboard,
    make_to_menu_keyboard
)
from utils.texts import (
    welcome_main,
    for_library,
    timetable_info,
    course_info,
    help_info,
    you_are_not_access_user
)
from utils.db.user import get_user_experience
from utils.db.accept_record import get_user_accept_history
from utils.db.user import get_user_position_by_experience
from utils.db.stack import get_stacks_titles
from utils.other.emoji import send_emoji
from utils.db.quiz import new_quiz_is_available

router = Router()
start_text = '''
👽 Приветствую Тебя, путник

С этой минуты Я Твой менеджер по добавкам.
Можешь: изучать добавки, оценивать их, 
приобретать готовые стаки, 
проверять свои знания в Храме, 
участвовать в рейтинге лучших и ещё всякого.
'''

@router.message(Command('start'))
async def start(
    message: types.Message,
    state: FSMContext
):
    await state.clear()
    await send_emoji(
        message=message,
    )
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text='В меню',
            callback_data='menu'
        )
    )
    await message.answer(
        text=start_text,
        reply_markup=builder.as_markup()
    )


@router.callback_query(
    F.data =='start'
)
async def start_callback(
    callback: types.CallbackQuery,
    state: FSMContext
):
    await state.clear()
    await send_emoji(
        callback=callback,
    )
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text='Дальше...',
            callback_data='menu'
        )
    )
    await callback.message.answer(
        text=start_text,
        reply_markup=builder.as_markup()
    )


@router.callback_query(
    F.data == 'menu'
)
async def menu(callback: types.CallbackQuery, state: FSMContext):
    """Вся информация о юзере плюс кнопки меню"""

    await send_emoji(
        callback=callback,
        emoji='🦍'
    )
    await state.clear()

    result = await get_user_accept_history(user_id=callback.from_user.id)
    try:
        percent = f'{int(result["successful"] / result["common"]*100)}%'
    except ZeroDivisionError:
        percent = '-'

    await callback.message.answer_photo(
        photo=URLInputFile(url='https://s3.timeweb.cloud/5e7808f1-s3store/logos/menu_logo.jpeg'),
        caption=f'''
<strong>Ник:</strong> <a href="https://t.me/{callback.from_user.username}">{callback.from_user.username}</a>
<strong>ID:</strong> <code>{callback.from_user.id}</code>
<strong>Клан:</strong> не доступен (требуется 10 Lvl)

<strong>🏆 Звание:</strong> Маскарян
<strong>🏅 Место:</strong> {await get_user_position_by_experience(user_id=callback.from_user.id)} место

<strong>⭐ Lvl:</strong> {1}
<strong>🌀 Твой опыт:</strong> {await get_user_experience(user_id=callback.from_user.id)}
<strong>💎 Твоя репутация приёмов:</strong> {percent} [успешные - {result['successful']} пропущенные - {result['passed']}

Опыт показывает количество очков за каждое совершённое успешное 
действия, Твой уровень напрямую зависит от твоего Опыта
Репутация отражает количество успешных приёмы.

''',
        parse_mode=ParseMode.HTML,
        reply_markup=await make_menu(),
        disable_web_page_preview=True
    )


@router.callback_query(
    F.data == 'library'
)
async def library(callback: types.CallbackQuery, state: FSMContext):
    await send_emoji(
        callback=callback,
        emoji='📚'
    )
    await state.clear()
    await callback.message.answer(
        text=for_library,
        reply_markup=await make_inline_library_keyboard()
    )


@router.callback_query(
    F.data == 'knowledge'
)
async def knowledge(callback: types.CallbackQuery, state: FSMContext):
    await send_emoji(
        callback=callback,
        emoji='🏛️'
    )
    await state.clear()

    res = await new_quiz_is_available(user_id=callback.from_user.id)

    if res == True or res == None:
    # if 1:
        await callback.message.answer(
            text='''
Приходите каждый день в Храм для проверки своих знаний 
о добавках.

За каждый верный ответ - начислю опыта
''',
            reply_markup=await make_knowledge_keyboard()
        )
    else:
        await callback.message.answer(
            text='🧙‍♂️ Мудрец уже ушёл из Храма, приходи через 24 часа',
            reply_markup=await make_to_menu_keyboard()
        )


@router.callback_query(
    F.data == 'timetable')
async def timetable(callback: types.CallbackQuery, state: FSMContext):
    await send_emoji(
        callback=callback,
        emoji='⌛'
    )
    await state.clear()
    """Show timetable for user"""
    await callback.message.answer(
        text=timetable_info,
        reply_markup=await make_inline_keyboard_to_timetable(user_id=callback.from_user.id),
        parse_mode=ParseMode.MARKDOWN
    )


@router.callback_query(
    F.data == 'stacks'
)
async def _stacks(callback: types.CallbackQuery, state: FSMContext):
    await send_emoji(
        callback=callback,
        emoji='🧰'
    )
    await state.clear()
    await callback.message.answer(
        text='''
Самые полезные стаки, которые только можно найти (смотри клавиатуру). 

В конце каждого стака есть кнопка для заказа полного стака (обычно это Ozon корзина )''',
        reply_markup=await make_keyboard(
            items=await get_stacks_titles()))


@router.callback_query(
    F.data == 'clans'
)
async def clans(callback: types.CallbackQuery, state: FSMContext):
    await send_emoji(
        callback=callback,
    )
    await state.clear()
    await callback.message.answer(
        text='''
<strong>🛡️ Кланы</strong>

Вступайте и создавайте кланы, участвуйте в клановых 
состязаниях и захватите мир.

⚠️ Кланы не доступны (требуется 10 Lvl)
''',
    parse_mode=ParseMode.HTML,
    reply_markup=await make_to_menu_keyboard()
    )


@router.callback_query(
    F.data == 'feedback'
)
async def _help(callback: types.CallbackQuery, state: FSMContext):
    await  send_emoji(
        callback=callback,
        emoji='🪖'
    )
    await state.clear()
    await callback.message.answer(
        text=help_info,
        reply_markup=await make_support_keyboard()
    )
