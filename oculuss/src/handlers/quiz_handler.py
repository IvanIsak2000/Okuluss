from aiogram import Router, html
from aiogram import types
from aiogram.enums import ParseMode
from aiogram.filters import StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from hashlib import blake2b
import random

from utils.logging.logger import logger
from utils.db.quiz import (
    select_random_poll,
    quiz_hash_is_exist, 
    new_quiz_is_available,
    is_correct_quiz,
    add_new_quiz,
    fill_quiz
)
from kb.make_inline_keyboard import (
    quiz_answers
)
from utils.db.user import update_user_experience

router = Router()


class QuizStates(StatesGroup):
    send_quiz = State()
    quiz_answer = State()


async def generate_quiz_hash() -> str:
    record_hash: str = blake2b(digest_size=7)
    record_hash.update(str(random.randint(0, 10000)).encode('utf-8'))
    return record_hash.hexdigest() 


@router.callback_query(
    StateFilter(None),
    lambda d: d.data.startswith('knowledge:Вопрос'))
async def knowledge_callback(callback: types.CallbackQuery, state: FSMContext):
    "Пока установлено через 24 часа, то есть новый вопрос можно получить только ровно через день"
    await state.clear()

    await logger.info(
        f'Доступность опроса: {await new_quiz_is_available(user_id=callback.from_user.id):} для пользователя {callback.from_user.id}')
    
    res = await new_quiz_is_available(user_id=callback.from_user.id)
    if res == True or res == None:
    # if 1:
        q = await select_random_poll()
        quiz_hash = await generate_quiz_hash()
        new_quiz = await callback.message.edit_text(
            text=f'❓ Вопрос: {q["question"]}',
            reply_markup=await quiz_answers(q['options'], quiz_hash=quiz_hash)
        )
        await logger.info(
            f'new_quiz:{new_quiz}')
            
        await add_new_quiz(
            quiz_hash=quiz_hash,
            correct_id=int(q['correct_option']),
            message=callback,
            correct=None,
            message_id=int(new_quiz.message_id)
        )
        await state.set_state(QuizStates.send_quiz)
    else:
        await callback.message.answer(
            text='🧙‍♂️ Мудрец составляет вопрос, придите через день...')


@router.callback_query(
    StateFilter(QuizStates.send_quiz),
    lambda d: d.data.startswith('quiz_answer:')
)
async def get_quiz_answer(
        callback_query: types.CallbackQuery, state: FSMContext):

    await state.set_state(QuizStates.quiz_answer)

    quiz_answer = int(callback_query.data.split(':')[1].split(',')[0])
    quiz_hash = callback_query.data.split(':')[-1]
    
    # await logger.info(f'Ответ:{quiz_answer}')
    # await logger.info(f'quiz_hash:{quiz_hash}')

    if await quiz_hash_is_exist(quiz_hash=quiz_hash):
        if await is_correct_quiz(quiz_hash=quiz_hash, suggested_id=quiz_answer):
            await update_user_experience(
                user_id=callback_query.from_user.id,
                count=50
            
            )
            await callback_query.message.edit_text(
                text='💥 Верно\nДобавлено +50 опыта 🌀',
                reply_markup=types.InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            types.InlineKeyboardButton(
                                text='🔙 К меню',
                                callback_data=f'menu')
                            
                        ]
                    ]
                )
            )
            await fill_quiz(
                quiz_hash=quiz_hash,
                correct=True)
        else:
            quotes = [
                'Чему бы ты ни учился, ты учишься для себя.'
            ]
            quote = random.choice(quotes)
            await callback_query.message.edit_text(
                text=f'🟥 Не правильно, попробуй в следующий раз\n{html.quote(quote)}',
                reply_markup=types.InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            types.InlineKeyboardButton(
                                text='🔙 К меню',
                                callback_data=f'menu')
                            
                        ]
                    ]
                ),
                parse_mode=ParseMode.HTML
            )
            await fill_quiz(
                quiz_hash=quiz_hash,
                correct=False)
    await state.clear()
