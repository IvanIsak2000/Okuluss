from aiogram import Router, F
from aiogram import types
from aiogram.enums import ParseMode
from aiogram.types import URLInputFile
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram import types
from aiogram.fsm.state import StatesGroup, State
from hashlib import blake2b
import random


from utils.logging.logger import logger
from kb.make_inline_keyboard import (
    make_buy_inline_keyboard,
    make_inline_keyboard,
    make_link_keyboard,
    make_support_keyboard
)

from utils.texts import (
    access_info_step_1,
    access_info_step_2,
    buy_by_usdt,
    wallet_link,
    prices
)
from utils.db.models import (
    add_new_access_user,
    hash_was_used,
    add_utilized_hash)
from utils.access.check_hash import CheckHash
from utils.logging.send_alert import send_alert

router = Router()


class BuyStates(StatesGroup):
    getting_user_hash = State()


async def generate_hash() -> str:
    record_hash: str = blake2b(digest_size=10)
    record_hash.update(str(random.randint(0, 10000)).encode('utf-8'))
    return record_hash.hexdigest() 


            

@router.callback_query(
    F.data == 'choose_payment'
)
async def buy(callback: types.CallbackQuery):
    await callback.message.answer(
        text='''
Выбери вариант оплаты
'''        
        ,
        reply_markup=await make_buy_inline_keyboard(),
        parse_mode=ParseMode.HTML)


@router.callback_query(
    lambda d: d.data.startswith('payment_by'))
async def usdt(callback: types.CallbackQuery, state: FSMContext):
    order_hash = await generate_hash()
    await state.update_data(order_hash=order_hash)

    logger.info(
        f'Юзер(id={callback.from_user.id}, username={callback.from_user.username}) выбрал USDT для оплаты, номер заказа: {order_hash}')

    await callback.message.answer(
        text=buy_by_usdt.format(
            wallet_link=wallet_link,
            order_hash=order_hash),
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=await make_inline_keyboard(['✅ Я оплатил']))


@router.callback_query(
    lambda d: d.data.startswith('selected:Яопла'))
async def check_usdt_but(
        callback: types.CallbackQuery,
        state: FSMContext):
    await callback.message.answer(
        text='🪪 Хорошо, теперь отправь Transaction ID (хэш):',
        reply_markup=await make_link_keyboard())
    await state.set_state(BuyStates.getting_user_hash)


@router.message(
    BuyStates.getting_user_hash,
    F.text
)
async def get_user_text(message: types.Message, state: FSMContext):
    await message.answer('👀 Проверяю транзакцию...')

    checker = CheckHash()
    hash_was_checked = await checker.check_hash(
        user_id=message.from_user.id,
        username=message.from_user.username,
        hash=message.text
    )
    full_data = await state.get_data()
    order_hash = full_data['order_hash']

    logger.info(f'hash_was_checked={hash_was_checked}')
    status = hash_was_checked['status']
    logger.info(f'status={status}')
    if status:
        await message.answer(
            '⚜️ Транзакция проверена!\n Добро пожаловать в число избранных: @OkulussBot\nПроверить доступ:\n/access')
        await add_new_access_user(message=message)
        await add_utilized_hash(
            user_id=message.from_user.id,
            username=message.from_user.username,
            order_hash=order_hash,
            hash=message.text)
        logger.info(
            f'✅ Цикл оплаты завершен для пользователя {message.from_user.id}')
    else:
        error_message = hash_was_checked['error_message']
        logger.error(f'{error_message} для пользователя {message.from_user.id}')
        await message.answer(
            text=f'{error_message}',
            reply_markup=await make_support_keyboard())
    # except Exception as e:
        # logger.critical(e)
        # await send_alert(alert_text=f'{e}', level='error')
