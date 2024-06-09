from aiogram import Router, F, html
from aiogram import types
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext


from kb.make_inline_keyboard import make_to_menu_keyboard

router = Router()


@router.callback_query(
    F.data == 'tasks'
)
async def get_task_menu(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    
    fake_tasks = '\n'.join([
        '💡 Собрать 10 опыта за день',
        '💡 Правильно ответить на вопрос',
        html.strikethrough('💡 Оценить один БАД')
    ])
    await callback.message.edit_text(
        text=f'📌 Выполняйте ежедневные задания и получайте опыт\n\n{fake_tasks}\n\nПолучите +100 опыта',
        reply_markup=await make_to_menu_keyboard(),
        parse_mode=ParseMode.HTML
    )