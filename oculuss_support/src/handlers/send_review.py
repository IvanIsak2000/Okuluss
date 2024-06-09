from aiogram import Router, F
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from utils.texts import send_review


from utils.db.models import add_review

from utils.logging.logger import logger
from utils.logging.send_alert import send_alert


router = Router()


class SendReview(StatesGroup):
    send_is_selected = State()
    review_is_typed = State()


@router.callback_query(
    lambda d: d.data.startswith('selected:Оставить'))
async def user_selected_send_review(
        callback: types.CallbackQuery,
        state: FSMContext):
    await callback.message.answer(
        text=send_review)
    await state.set_state(SendReview.send_is_selected)


@router.message(
        SendReview.send_is_selected,
        F.text)
async def writing_review(
        message: types.Message,
        state: FSMContext):

    if message.text is not None or '':
        await add_review(
            message=message,
            review_text=message.text,
        )
        await state.set_state(SendReview.review_is_typed)
        await send_alert(
            f'📫 Пользователь (id={message.from_user.id}, full_name={message.from_user.full_name}) отправил отзыв:\n{message.text}',
            level='info')
        await message.answer('📧 Отзыв отправлен!')
        await state.clear()
