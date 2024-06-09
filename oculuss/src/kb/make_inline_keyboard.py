from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types


from utils.texts import (
    course_names,
    only_course_sections
)
from utils.db.custom_supplementation import get_user_supplementation_count


async def remove_symbols(item: str):
    return "".join([i for i in item if i.isdigit() or i.isalpha()])


async def make_inline_keyboard(items: list):
    builder = InlineKeyboardBuilder()
    for item in items:
        builder.row(types.InlineKeyboardButton(
            text=item,
            callback_data=f'selected:{await remove_symbols(item)}')
        )
    builder.row(types.InlineKeyboardButton(
        text='🔙 К меню',
        callback_data=f'menu'))
    return builder.as_markup()


async def make_inline_keyboard_to_timetable(user_id: int):
    timetable_sections = [
    {
        'text': '➕ Добавить приём',
        'callback': 'add_supplement'
    },
    {
        'text': f'🔎 Посмотреть ({await get_user_supplementation_count(user_id)})',
        'callback': 'show_all_supplementation'
    }
]

    items = timetable_sections
    builder = InlineKeyboardBuilder()
    for item in items:
        builder.row(types.InlineKeyboardButton(
            text=item['text'],
            callback_data=f'selected:{item["callback"]}')
        )
    builder.row(types.InlineKeyboardButton(
        text='🔙 К меню',
        callback_data=f'menu'))
    return builder.as_markup()


# async def make_only_course_managing_keyboard():
#     items = only_course_sections
#     builder = InlineKeyboardBuilder()
#     for item in items:
#         builder.row(types.InlineKeyboardButton(
#             text=item,
#             callback_data=f'selected:{await remove_symbols(item)}')
#         )
#     return builder.as_markup()


async def make_inline_cancel_keyboard():
    items = ['🚫 Закрыть']
    builder = InlineKeyboardBuilder()
    for item in items:
        builder.row(types.InlineKeyboardButton(
            text=item,
            callback_data=f'selected:{await remove_symbols(item)}')
        )
    return builder.as_markup()


async def make_inline_select_course_keyboard(
        course_title: str,
        course_name: str):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(
        text=course_title,
        callback_data=f'course_name:{course_name}'))
    builder.row(types.InlineKeyboardButton(
        text='🔙 К меню',
        callback_data=f'menu'))
    return builder.as_markup()


async def make_yes_no_keyboard():
    items = ['✅ Да', '❌ Нет']
    builder = InlineKeyboardBuilder()
    for item in items:
        builder.row(types.InlineKeyboardButton(
            text=item,
            callback_data=f'confirm:{await remove_symbols(item)}')
        )
    builder.row(types.InlineKeyboardButton(
        text='🔙 К меню',
        callback_data=f'menu'))
    return builder.as_markup()


async def make_timelist_keyboard():
    hourly_times = []
    for h in range(0, 24):
        hourly_times.append(f'{h:02d}:00')
    items = hourly_times
    builder = InlineKeyboardBuilder()
    for item in items:
        builder.row(types.InlineKeyboardButton(
            text=item,
            callback_data=f'time:{item}')
        )
    return builder.as_markup()


# async def make_courses_keyboard():
#     items = course_names
#     builder = InlineKeyboardBuilder()
#     for item in items:
#         builder.row(types.InlineKeyboardButton(
#             text=item,
#             callback_data=f'selected:{await remove_symbols(item)}')
#         )
#     return builder.as_markup()


async def make_stacks_keyboard(stacks: list):
    items = stacks
    builder = InlineKeyboardBuilder()
    for item in items:
        builder.row(types.InlineKeyboardButton(
            text=item,
            callback_data=f'stack:{await remove_symbols(item)}')
        )
    builder.row(types.InlineKeyboardButton(
        text='🔙 К меню',
        callback_data=f'menu'))
    return builder.as_markup()


async def make_support_keyboard():
    """Создает клавиатуру поддержки"""
    items = ['Оставить отзыв', 'Поддержка']
    builder = InlineKeyboardBuilder()
    for item in items:
        builder.row(types.InlineKeyboardButton(
            text=item,
            callback_data=f'selected:{await remove_symbols(item)}')
        )
    builder.row(types.InlineKeyboardButton(
        text='🔙 К меню',
        callback_data=f'menu'))
    return builder.as_markup()


async def make_link_to_profile_article():
    profile_link = 'https://telegra.ph/CHto-takoe-profil-04-14'
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(
        text='Что такое профиль?',
        url=profile_link))
    builder.row(
        types.InlineKeyboardButton(
            text='Достижения',
            callback_data=f'selected:achievements'))
    builder.row(types.InlineKeyboardButton(
        text='🔙 К меню',
        callback_data=f'menu'))
    return builder.as_markup()


async def make_knowledge_keyboard():
    "Создать клавиатуру"
    items = ['Вопрос от мудреца']
    builder = InlineKeyboardBuilder()
    for item in items:
        builder.row(types.InlineKeyboardButton(
            text=item,
            callback_data=f'knowledge:{await remove_symbols(item)}'))
    builder.row(types.InlineKeyboardButton(
        text='🔙 К меню',
        callback_data=f'menu'))
    return builder.as_markup()


async def quiz_answers(
    options: list, quiz_hash: int):
    items = options
    index = 0 
    builder = InlineKeyboardBuilder()
    for item in items:

        builder.row(types.InlineKeyboardButton(
            text=item,
            callback_data=f'quiz_answer:{index},quiz_hash:{quiz_hash}'))
        index += 1
    builder.row(types.InlineKeyboardButton(
        text='🔙 К меню',
        callback_data=f'menu'))
    return builder.as_markup()


async def make_menu():

    builder = InlineKeyboardBuilder()

    builder.row(
        types.InlineKeyboardButton(
            text='👤 Лик',
            callback_data='profile')
    )

    builder.row(
        types.InlineKeyboardButton(
            text='📚 Википедия',
            callback_data='wiki'
        ),
        # types.InlineKeyboardButton(
        #     text='⚗️ Топ БАДов',
        #     callback_data='top'
        # ),
        types.InlineKeyboardButton(
            text='📦 Стаки',
            callback_data='stacks'
        )
    )

    builder.row(
        types.InlineKeyboardButton(
            text='🪬 Святилище',
            callback_data='knowledge'
        )
    )

    builder.row(
        types.InlineKeyboardButton(
            text='📅 Часовня',
            callback_data='timetable'
        ),
                types.InlineKeyboardButton(
            text='🎯 Задачи',
            callback_data='tasks'   
        )
    )

    builder.row(
        types.InlineKeyboardButton(
            text='⛑️ Обратная связь',
            callback_data='feedback'
        )
    )
    return builder.as_markup()


async def make_to_menu_keyboard():
    builder = InlineKeyboardBuilder()
    
    builder.row(types.InlineKeyboardButton(
        text='🔙 К меню',
        callback_data=f'menu')
    )

    return builder.as_markup()