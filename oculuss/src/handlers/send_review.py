from aiogram import Router
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram import types
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import StateFilter
import asyncio

from utils.texts import send_review
from utils.db.review import add_review
from utils.logging.logger import logger


router = Router()


class SendReview(StatesGroup):
    send_is_selected = State()
    review_is_typed = State()


@router.callback_query(
    StateFilter(None),
    lambda d: d.data.startswith('selected:Оставить'))
async def user_selected_send_review(
        callback: types.CallbackQuery,
        state: FSMContext):
    await callback.message.answer(
        text=send_review)
    await state.set_state(SendReview.send_is_selected)


@router.message(
    SendReview.send_is_selected)
async def writing_review(
        message: types.Message,
        state: FSMContext):

    if message.text is not None or '':

        await logger.info(
            f'User with id={message.from_user.id} name={message.from_user.full_name} review text is {message.text}')

        await state.set_state(SendReview.review_is_typed)
        await add_review(
            message=message,
            review_text=message.text,
        )
        await message.answer(
            text='Отправляю...'
        )
        await asyncio.sleep(10)
        await message.answer('📧 Отзыв отправлен!')
        await logger.info(
            message=f'📫 Пользователь (id={message.from_user.id}, full_name={message.from_user.full_name}) отправил отзыв:\n{message.text}',
            send_alert=True)

    else:
        await message.answer('Некорректный текст!')
        await logger.info(
            f'User with id={message.from_user.id}, \
            name={message.from_user.full_name} rewrite review text is \
            {message.text}')
    await state.clear()
