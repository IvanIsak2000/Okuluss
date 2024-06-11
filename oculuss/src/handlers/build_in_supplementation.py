import asyncio
from aiogram import Router, F
from aiogram import types
from aiogram.enums import ParseMode
from aiogram.types import InlineQuery, InlineQueryResultArticle
from aiogram.types import InputTextMessageContent, URLInputFile
from aiogram.filters import StateFilter
from urllib.parse import urlparse
from aiogram.utils.markdown import hlink


from utils.db.build_in_supplementation import (
    get_supplementation,
    get_info_from_supplementation_by_id
)
from kb.make_inline_library_keyboard import make_under_supplementation_keyboard
from utils.logging.logger import logger


router = Router()


@router.inline_query(
    F.query == 'library',
    StateFilter(None))
async def get_supplementation_as_library_list(
        query: InlineQuery):
    """Получение inline запроса от пользователям"""
    supplementation_item = await get_supplementation(message=query)

    supplementation_dict = []

    for item in supplementation_item:
        message_text = f"id:{item.id}"
        message_content = InputTextMessageContent(message_text=message_text)
        one_supplement = InlineQueryResultArticle(
            id=str(item.id),
            title=item.title,
            thumbnail_url=item.image_link,
            input_message_content=message_content)
        supplementation_dict.append(one_supplement)
    await query.answer(supplementation_dict)


@router.message(
    F.text.startswith('id'),
    StateFilter(None))
async def supplementation_answers_func(message: types.Message):
    """Ответ пользователю сообщения с полной информацией о БАДе"""

    await asyncio.sleep(1)
    await logger.info(f'Из поиска перехватил id: {message.text} для пользователя id={message.from_user.id}')
    await message.delete()

    supplementation_item = await get_info_from_supplementation_by_id(
        _id=message.text.split('id:')[1])

    base_text = f'''
    <u><i>*Возможный пример товара</i></u>

    🧬 <b>{supplementation_item.title}</b> 🧬

    📚 {supplementation_item.description}\n
    '''

    links = '\n'.join([hlink(title=f"{urlparse(link).netloc}", url=link) for link in supplementation_item.link])
    base_text += '🛒 Где можно найти:\n' + links

    await message.answer_photo(
        photo=URLInputFile(url=supplementation_item.image_link),
        caption=base_text,
        reply_markup=await make_under_supplementation_keyboard(
            message=message),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True
    )


@router.callback_query(
    lambda d: d.data.startswith('id:')
)
async def get_supplementation_from_callback(callback: types.CallbackQuery):
    
    await asyncio.sleep(1)
    await logger.info(f'Из поиска по callback перехватил id: {callback.data} для пользователя id={callback.from_user.id}')
    
    # await callback.message.delete()
    # убрал потому что неудобно снова открыть стакавого состава БАДов
 
    supplementation_item = await get_info_from_supplementation_by_id(
        _id=callback.data.split('id:')[1])
    base_text = f'''
    <u><i>*Возможный пример товара</i></u>

    🧬 <b>{supplementation_item.title}</b> 🧬

    📚 {supplementation_item.description}\n
    '''
    links = '\n'.join([hlink(title=f"{urlparse(link).netloc}", url=link) for link in supplementation_item.link])
    base_text += '🛒 Где можно найти:\n' + links

    await callback.message.answer_photo(
        photo=URLInputFile(url=supplementation_item.image_link),
        caption=base_text,
        reply_markup=await make_under_supplementation_keyboard(
            callback=callback),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True
    )
