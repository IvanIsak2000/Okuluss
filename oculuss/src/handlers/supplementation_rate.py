import asyncio
from aiogram import Router, F
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import StateFilter


from utils.logging.logger import logger
from utils.db.rating import update_supplementation_rate
from utils.db.build_in_supplementation import get_info_from_supplementation_by_id
from utils.other.emoji import send_emoji
from kb.make_inline_keyboard import make_to_menu_keyboard
from utils.db.rating import get_supplementation_rating


class RateSupplementation(StatesGroup):
    choose_reaction = State()
    moderating = State()


router = Router()


@router.callback_query(
    StateFilter(None),
    lambda d: d.data.startswith('react'))
async def rate_supplementation(
        query: types.CallbackQuery,
        state: FSMContext):

    reaction_positive = True if '👍' in query.data.split(":", maxsplit=1)[1] else False
    supplementation_id_to_react = query.data.split(':')[-1]

    await logger.info(
        f'Получена оценка юзера: это 👍 - {reaction_positive} от пользователя с id: {query.from_user.id}')
    if reaction_positive:
        await query.message.answer(
                text='''
✍️ Если Тебе понравился этот БАД, то напиши
отзыв, который был бы полезен Тебе самому.


<i>⚠️ Бренд и название обязательны</i>

⚡ Я заметил...
⚡ Пить лучше днём, так как ...
⚡ Я употреблял по столько-то и вот что получилось и т.д
''',            parse_mode=ParseMode.HTML)
        await state.update_data(
            react=1,
            supplementation_id=supplementation_id_to_react)
        await state.set_state(RateSupplementation.choose_reaction)
    else:
        await query.message.answer(
            text='''
🚨 Если Тебе не понравился такой БАД или
определённый товар, смело пиши донос.

<i>⚠️ Бренд и название обязательны</i>

❗ Мне не понравился вкус...
❗ 2 грамма меня не берут ...
❗ У такого производителя не качественный товар... 
''',
            parse_mode=ParseMode.HTML
        )
        await state.update_data(
            react=-1,
            supplementation_id=supplementation_id_to_react)
        await state.set_state(RateSupplementation.choose_reaction)


@router.message(
    RateSupplementation.choose_reaction
)
async def getting_text(
        message: types.Message,
        state: FSMContext
):

    text = message.text
    if not text.startswith('/'):
        await state.set_state(RateSupplementation.moderating)

        emoji_msg = await send_emoji(
            message=message,
            emoji='⌛',
        )
        moderation_msg = await message.answer(
            'Модерирую оценку'
        )

        
        await state.update_data(text=text)

        full_data = await state.get_data()
        supplementation_group = await get_info_from_supplementation_by_id(
                _id=full_data['supplementation_id'])

        await update_supplementation_rate(
            user_id=message.from_user.id,
            username=message.from_user.username,
            supplementation_group=supplementation_group.title,
            rate=full_data['react'])

        await asyncio.sleep(10)

        await moderation_msg.delete()

        await send_emoji(
            message=message,
            emoji='✅',
            to_delete=False
        )
        await message.answer('Ваша оценка и отзыв приняты!')
        await state.clear()


@router.callback_query(
    RateSupplementation.moderating
)
async def if_moderating(
        callback: types.CallbackQuery,
        state: FSMContext
):
    await callback.message.answer(
        text='Дождитесь предыдущей модерации!'
    )


@router.callback_query(
    F.data == 'top'
)
async def _top(callback: types.CallbackQuery, state: FSMContext):
    await send_emoji(
        callback=callback,
        emoji='🔥'
    )
    await state.clear()
    await callback.message.answer(
        text=f'''
Рейтинг БАДов. Голосуйте за свою любимые БАДы в меню Библиотеки

🔥 Десятка лучших по мнению пользователей
{await get_supplementation_rating()}''',
        reply_markup=await make_to_menu_keyboard())