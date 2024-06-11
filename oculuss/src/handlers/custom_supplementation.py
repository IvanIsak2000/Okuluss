from aiogram import Router
from aiogram import types
from aiogram.enums import ParseMode
from aiogram.filters import StateFilter


from utils.logging.logger import logger
from kb.make_inline_keyboard import make_inline_keyboard_to_timetable
from kb.supplementation_keyboard import (
    make_supplementation_keyboard,
    keyboard_for_edit_supplementation,
)
from utils.db.custom_supplementation import (
    get_user_custom_supplementation,
    get_user_custom_supplementation_by_hash,
    get_user_custom_supplementation_by_name,
    remove_user_custom_supplementation,
    turn_off_supplementation,
    turn_on_supplementation
)
from kb.make_inline_library_keyboard import make_inline_library_keyboard
from kb.make_inline_keyboard import make_to_menu_keyboard
from utils.other.emoji import send_emoji

router = Router()


@router.callback_query(
    StateFilter(None),
    lambda d: d.data.startswith('selected:show_all_supplementation'))
async def show_all_supp(
        callback: types.CallbackQuery):

    if await make_supplementation_keyboard(user_id=callback.from_user.id) == False:
        await send_emoji(
            callback=callback,
            emoji='👀',
            to_delete=False
        )
        await callback.message.answer(
            text='Ваших добавок не обнаружено!',
            reply_markup=await make_to_menu_keyboard()
        )        
       
    else:
        await send_emoji(
            callback=callback,
            emoji='💊',
        )
        await callback.message.answer(
            text='''
Весь список твоих кастомных добавок.

Для редактирования нажимай на кнопку добавки:
''',
            reply_markup=await make_supplementation_keyboard(
                user_id=int(callback.from_user.id))
        )


@router.callback_query(
    StateFilter(None),
    lambda d: d.data.startswith('supplementation:'))
async def open_supplementation(
        callback: types.CallbackQuery,
        supp_hash_from_editing: str = None):
    """Принимает название добавки и заменяет на окно информации о добавки"""
    try:
        supplementation_hash = callback.data.split(':')[1]
    except IndexError:
        supplementation_hash = supp_hash_from_editing

    user_suppl = await get_user_custom_supplementation_by_hash(
        user_id=int(callback.from_user.id),
        supplementation_hash=supplementation_hash
    )

    await callback.message.edit_text(
        text=f'''
Название: <code>{user_suppl.name}</code>
Дозировка: <code>{user_suppl.dose}</code>
Время приёма: <code>{user_suppl.time}</code>
Осталось: <code>{round(user_suppl.count, 2)}</code>
''',
        parse_mode=ParseMode.HTML,
        reply_markup=await keyboard_for_edit_supplementation(
            user_id=callback.from_user.id,
            supplementation_hash=user_suppl.supplementation_hash))


@router.callback_query(
    StateFilter(None),
    lambda d: d.data.startswith('supplementation_to_remove:'))
async def remove_supplementation(callback: types.CallbackQuery):

    suppl_hash_to_remove = callback.data.split(':')[1]
    await logger.info(f'supp_hash_to_remove: {suppl_hash_to_remove}')
    await remove_user_custom_supplementation(
        message=callback,
        supplementation_hash=suppl_hash_to_remove
    )

    if await make_supplementation_keyboard(user_id=callback.from_user.id) == False:
        await send_emoji(
            callback=callback,
            to_delete=False
        )
        await callback.message.answer(
            text='Удалено!',
            reply_markup= await make_inline_keyboard_to_timetable(user_id=callback.from_user.id)
        )
    else:
        await send_emoji(
            callback=callback,
            to_delete=False
        )
        await callback.message.answer(
            text='Удалено!',
            reply_markup= await make_supplementation_keyboard(
                user_id=callback.from_user.id,
            )
        )

@router.callback_query(
    StateFilter(None),
    lambda d: d.data.startswith('supplementation_to_turn_off:'))
async def turn_off(callback: types.CallbackQuery):
    """
    Отключить БАД
    """

    suppl_hash_to_turn_off = callback.data.split(':')[1]
    await turn_off_supplementation(
        user_id=int(callback.from_user.id),
        supplementation_hash=suppl_hash_to_turn_off
    )
    await open_supplementation(
        callback=callback, 
        supp_hash_from_editing=suppl_hash_to_turn_off
    )
 

@router.callback_query(
    StateFilter(None),
    lambda d: d.data.startswith('supplementation_to_turn_on:'))
async def turn_on(callback: types.CallbackQuery):
    """
    Включить БАД
    """

    suppl_hash_to_turn_on = callback.data.split(':')[1]
    await turn_on_supplementation(
        user_id=int(callback.from_user.id),
        supplementation_hash=suppl_hash_to_turn_on
    )
    await open_supplementation(
        callback=callback,
        supp_hash_from_editing=suppl_hash_to_turn_on
    )
