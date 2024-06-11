import aiogram
from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import ReplyKeyboardRemove
from aiogram.fsm.state import StatesGroup, State
from aiogram.enums import ParseMode
import random
from aiogram.utils.formatting import (
    Bold,
    as_list,
    as_marked_section,
    as_key_value
)
from hashlib import blake2b
from datetime import datetime, time


from utils.logging.logger import logger
from kb.make_inline_keyboard import (
    make_inline_keyboard_to_timetable,
    make_yes_no_keyboard,
    make_inline_keyboard,
    make_inline_cancel_keyboard,
    make_timelist_keyboard,
    make_inline_keyboard_to_timetable
)
from utils.db.custom_supplementation import (
    get_user_custom_supplementation,
    remove_user_custom_supplementation
)
from utils.db.custom_supplementation import (
    add_new_user_custom_supplementation
)
from utils.texts import (
    step_1,
    step_2,
    step_3
)
from utils.other.exceptions import (
    SupplementationNameIsNotValid,
    SupplementaryDoseIsNotValid,
    SupplementationCountIsNotValid
)


class AddSupplementation(StatesGroup):
    name_selected = State()
    dose_selected = State()
    time_selected = State()
    count_selected = State()
    confirm_state = State()

    error_state = State()


router = Router()


async def generate_supplementation_hash() -> str:
    record_hash: str = blake2b(digest_size=10)
    record_hash.update(str(random.randint(0, 10000)).encode('utf-8'))
    return record_hash.hexdigest() 


async def answer_error(
        message: types.Message,
        state: FSMContext,
        error_class: Exception,
        error_message: str):
    """Отправляет ошибку и стерает state"""
    if error_class is SupplementationNameIsNotValid:
        await logger.error(
            message=f'Юзер с id={message.from_user.id} не правильно ввёл название БАДа. Дополнительно: {error_message}')
        text = f'❌ При заполнение вы допустили ошибку в имени, \
            требуется ввести по примеру: GABA.\nДополнительно: {error_message}'
    elif error_class is SupplementaryDoseIsNotValid:
        await logger.error(
            message=f'Юзер с id={message.from_user.id} не правильно ввёл дозу. Дополнительно: {error_message}')
        text = f'❌ Неправильно введена дозировка, требуется ввести по примеру: 0,5 или 0.5.\nДополнительно: {error_message}'
    elif error_class is SupplementationCountIsNotValid:
        await logger.info(
            message=f'Юзер с id={message.from_user.id} не правильно ввёл количество. Дополнительно: {error_message}',
            send_alert=True)
        text = f'❌ Неправильно введено количество, требуется ввести по примеру: 60 или 90.9\nДополнительно: {error_message}'
    elif error_class is None and error_message:
        await logger.critical(f'❌ Непредвиденная ошибка! Дополнительно: {error_message}')
        text = f'❌ Непредвиденная ошибка!\n Дополнительно: {error_message}'
        
    await state.clear()
    await message.answer(
        text=text,
        reply_markup=await make_inline_keyboard_to_timetable(user_id=message.from_user.id))


@router.callback_query(
    StateFilter(None),
    lambda d: d.data.startswith('selected:add_supplement'))
async def ask_name(
        callback: types.CallbackQuery,
        state: FSMContext):
    """Starting and ask name"""

    await callback.message.answer(
        text=step_1,
        parse_mode=ParseMode.HTML
    )
    await state.set_state(AddSupplementation.name_selected)


@router.message(
    AddSupplementation.name_selected)
async def ask_dose(
        message: types.Message,
        state: FSMContext):
    """Get name and ask dose"""
    name = message.text
    try:
        await state.update_data(name=name)
        await message.answer(
            text=step_2,
            parse_mode=ParseMode.HTML
        )
        await state.set_state(AddSupplementation.dose_selected)
        # else:
        #     await answer_error(
        #         message=message,
        #         state=state,
        #         error_class=SupplementationNameIsNotValid,
        #         error_message=message.text)
    except Exception as e:
        await answer_error(
            message=message,
            state=state,
            error_class=SupplementationNameIsNotValid,
            error_message=str(e))


@router.message(
    AddSupplementation.dose_selected)
async def ask_time(
        message: types.Message,
        state: FSMContext):
    """Get dose and ask time"""
    dose = message.text.replace(',', '.')
    try:
        float(dose)
        await state.update_data(dose=dose)
        await message.answer(
            text=step_3,
            parse_mode=ParseMode.HTML,
            reply_markup=await make_timelist_keyboard())
        await state.set_state(AddSupplementation.dose_selected)

    except ValueError:
        await answer_error(
            message=message,
            state=state,
            error_class=SupplementaryDoseIsNotValid,
            error_message=message.text)
    except Exception as e:
        await answer_error(
            message=message,
            state=state,
            error_class=SupplementaryDoseIsNotValid,
            error_message=str(e))


@router.callback_query(
    AddSupplementation.dose_selected)
async def ask_count(
        callback: types.CallbackQuery,
        state: FSMContext):
    """Get time and ask count"""
    data = callback.data
    user_time = data.split(':', maxsplit=1)[1]
    await state.update_data(time=user_time)
    await callback.message.delete()
    try:
        await callback.message.answer(
            text='✅ Время выбрано',
            reply_markup=ReplyKeyboardRemove())
        await callback.message.answer(
            text='⚙️ Шаг 4/4:\nВведите количество БАДа, чтобы из него можно было вычесть суточный приём. Например, 60 или 99.9'
        )
        await state.set_state(AddSupplementation.count_selected)
    except Exception as e:
        await answer_error(
            message=callback.message,
            state=state,
            error_class=None,
            error_message=str(e))


@router.message(
    AddSupplementation.count_selected)
async def get_count_and_confirming(
        message: types.Message,
        state: FSMContext,
        bot: aiogram.Bot):
    """Confirming"""
    user_count = message.text
    try:
        float(user_count)
        await state.update_data(count=user_count)
        full_data = await state.get_data()

        builder = InlineKeyboardBuilder()
        builder.row(
            types.InlineKeyboardButton(
                text=f'{full_data["name"][0:10]} {full_data["time"]} {full_data["dose"]}',
                callback_data='supplementation_name_test'
            )
        )
        msg = await message.answer(
            text='тест вывода названия бада',
            reply_markup=builder.as_markup()
        )   
        
        await bot.delete_message(
            chat_id=message.chat.id,
            message_id=msg.message_id
        )

        content = as_list(
            as_marked_section(
                Bold('Итого:'),
                as_key_value('Добавка', str(full_data['name'])),
                as_key_value('Дозировка в (мг)', float(full_data['dose'])),
                as_key_value('Время приёма', full_data['time']),
                as_key_value('Количество', float(full_data['count']))
            ),
            sep='\n\n')

        await message.answer(**content.as_kwargs())
        await message.answer(
            text='Подтвердить?',
            reply_markup=await make_yes_no_keyboard())
        await state.set_state(AddSupplementation.confirm_state)
        
    except ValueError:
        await answer_error(
            message=message,
            state=state,
            error_class=SupplementationCountIsNotValid,
            error_message=message.text
        )
    except Exception as e:
        await answer_error(
            message=message,
            state=state,
            error_class=None,
            error_message=str(e)
        )


@router.callback_query(
    AddSupplementation.confirm_state,
    lambda d: d.data.startswith('confirm:Да'))
async def confirm_is_true(
        callback: types.CallbackQuery,
        state: FSMContext):
    """New supplementation is confirmed"""
    # try:
    full_data = await state.get_data()      
    await add_new_user_custom_supplementation(
        message=callback,
        supplementation_hash=await generate_supplementation_hash(),
        name=full_data['name'],
        dose=float(full_data['dose'].replace(',', '.')),
        time=datetime.strptime(full_data['time'], '%H:%M'),
        count=float(full_data['count']))
    await state.clear()
    await callback.message.answer(
        '🏆 Добавка успешно добавлена',
        reply_markup=await make_inline_keyboard_to_timetable(user_id=callback.from_user.id))
    await logger.info(
        f'Подтверждённое добавление добавки от юзера(id={callback.from_user.id}), full_data={full_data}')
    # except Exception as e:
    #     await answer_error(
    #         message=callback.message,
    #         state=state,
    #         error_class=None,
    #         error_message=str(e))


@router.callback_query(
    AddSupplementation.confirm_state,
    lambda d: d.data.startswith('confirm:Нет'))
async def confirm_is_false(
        callback: types.CallbackQuery,
        state: FSMContext):
    """New supplementation is not confirmed"""

    await callback.message.answer(
        text='❗Добавление отменено',
        reply_markup=await make_inline_keyboard_to_timetable(user_id=callback.from_user.id))
    await state.clear()


@router.callback_query(
    lambda d: d.data.startswith('selected:Закрыть'))
async def clear(
        callback: types.CallbackQuery,
        state: FSMContext):
    """Clear supplementation add """
    await state.clear()
    await callback.message.answer(
        'Очищено! Если хотите добавить приём нажмите ниже:',
        reply_markup=await make_inline_keyboard_to_timetable(user_id=callback.from_user.id))
