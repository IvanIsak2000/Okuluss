import asyncio
from aiogram import Router, F
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from aiogram.fsm.state import StatesGroup, State

from utils.logging.logger import logger

from utils.db.rating import update_supplementation_rate
from utils.db.build_in_supplementation import get_info_from_supplementation_by_id


class RateSupplementation(StatesGroup):
    choose_reaction = State()
    typed_text = State()
    checked = State()


router = Router()


@router.callback_query(
    lambda d: d.data.startswith('react'))
async def rate_supplementation(
        query: types.CallbackQuery,
        state: FSMContext):
    await state.clear()
    reaction_positive = True if '👍' in query.data.split(":", maxsplit=1)[1] else False
    supplementation_id_to_react = query.data.split(':')[-1]

    await logger.info(
        f'Получена оценка юзера: это 👍 - {reaction_positive} от пользователя с id: {query.from_user.id}')
    if reaction_positive:
        await query.message.answer(
                text='''
✍️ Если Вам понравился этот БАД, то напишите
комментарий, который был бы вам полезен до употребления.


<i>⚠️ Бренд и название обязательны</i>

⚡ Я заметил...
⚡ Я бы порекомендовал бы себе вот это...
⚡ Я употреблял по столько-то и вот что получилось и т.д
''',            parse_mode=ParseMode.HTML)
        await state.update_data(
            react=1,
            supplementation_id=supplementation_id_to_react)
        await state.set_state(RateSupplementation.choose_reaction)
    else:
        await query.message.answer(
            text='''
🚨 Если Вам не понравилось такой БАД или
определённый товар, смело пишите донос.

<i>⚠️ Бренд и название обязательны</i>

❗ Мне не понравилось, например вкус
❗ Считаю, что бесполезная дозировка
❗ Заметил нехорошие побочные эффекты и т.д
''',
            parse_mode=ParseMode.HTML)
        await state.update_data(
            react=-1,
            supplementation_id=supplementation_id_to_react)
        await state.set_state(RateSupplementation.choose_reaction)


@router.message(
    RateSupplementation.choose_reaction)
async def getting_text(
        message: types.Message,
        state: FSMContext):

    text = message.text
    if not text.startswith('/'):
        await state.set_state(RateSupplementation.typed_text)
        await message.answer('⏳ Модерирую оценку')

        
        await state.update_data(text=text)
        await logger.info(f'data={await state.get_data()}')

        full_data = await state.get_data()
        supplementation_group = await get_info_from_supplementation_by_id(
                _id=full_data['supplementation_id'])

        await update_supplementation_rate(
            user_id=message.from_user.id,
            username=message.from_user.username,
            supplementation_group=supplementation_group.title,
            rate=full_data['react'])
        await asyncio.sleep(60)    
        await message.answer('✅ Ваша оценка и отзыв приняты!')
