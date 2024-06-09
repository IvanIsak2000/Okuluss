# from aiogram import Router
# from aiogram import types
# from aiogram.enums import ParseMode
# from datetime import timedelta

# from utils.logging.logger import logger

# from kb.make_inline_keyboard import (
#     make_inline_select_course_keyboard,
#     make_yes_no_keyboard,
#     make_courses_keyboard,
#     make_inline_keyboard,
#     make_inline_keyboard_to_timetable,
#     make_only_course_managing_keyboard
# )

# from utils.db.course import (
#     add_user_to_course,
#     user_course,
#     remove_user_from_course,
#     user_have_course
# )

# from filters.no_course import (
#     HaveCourse,
#     HaveNotCourse
# )

# from utils.texts import depression_info


# router = Router()


# # @router.callback_query(
# #         
# #         HaveCourse(),
# #         lambda d: d.data.startswith('selected:Удалить'))
# # async def delete_course(callback: types.CallbackQuery):
# #     await callback.message.answer(
# #         f'🗑️ Вы удалены с курса: {await user_course(message=callback)}. \
# # Можете выбрать курс для записи ниже:',
# #         reply_markup=await make_only_course_managing_keyboard())
# #     await remove_user_from_course(message=callback)
# #     await logger.info(f'User {callback.from_user.id} removed from monitoring')

      
# # @router.callback_query(
# #         
# #         lambda d: d.data.startswith('selected:Мой'))
# # async def my_course(callback: types.CallbackQuery):
# #     if await user_have_course(message=callback):
# #         await callback.message.answer(
# #             f'📚 Ваш текущий активный курс: \
# # {await user_course(message=callback)}',
# #             reply_markup=await make_inline_keyboard(['❌ Удалить курс']),
# #             parse_mode=ParseMode.MARKDOWN)
# #     else:
# #         await callback.message.answer(
# #             text='У вас не выбран курс!',
# #             reply_markup=await make_only_course_managing_keyboard())


# # @router.callback_query(
# #         
# #         HaveNotCourse(),
# #         lambda d: d.data.startswith('selected:'))
# # async def selecting_course(callback: types.CallbackQuery):
# #     course_name = callback.data.split(':')[1]
# #     await logger.info(
# #         f'User with id={callback.from_user.id} selected the course: \
# # {course_name} to write')
# #     if 'Депрессия' in course_name:
# #         await callback.message.edit_text(
# #             text=depression_info,
# #             reply_markup=await make_inline_select_course_keyboard(
# #                 course_title='Записаться на курс',
# #                 course_name='Депрессия'))


# # @router.callback_query(
# #         
# #         HaveCourse(),
# #         lambda d: d.data.startswith('selected:'))
# # async def user_already_have_course(callback: types.CallbackQuery):
# #     await callback.message.edit_text(
# #         text='⚠️ Вы уже записаны на курс! Стереть все данные об прошлом курсе?',
# #         reply_markup=await make_yes_no_keyboard())


# # @router.callback_query(
# #         
# #         HaveNotCourse(),
# #         lambda d: d.data.startswith('course_name:'))
# # async def user_selected_course(callback: types.CallbackQuery):

# #     user_write_in_course = callback.data.split(':')[1]
# #     await add_user_to_course(
# #         message=callback,
# #         course_name=user_write_in_course,
# #     )
# #     await callback.message.edit_text(
# #         text=f'✅ Теперь вы записаны на курс: {user_write_in_course}\n\
# # Ваше расписание расписано по дням.\nПервый опрос пришлём \
# # завтра утром!',
# #         reply_markup=await make_only_course_managing_keyboard())


# # @router.callback_query(
# #         
# #         HaveCourse(),
# #         lambda d: d.data.startswith('confirm:'))
# # async def confirm_to_remove(callback: types.CallbackQuery):
# #     confirm = callback.data.split('confirm:')[1]
# #     await logger.info(f'Confirm: {confirm}')
# #     if confirm == 'Да':
# #         await remove_user_from_course(message=callback)
# #         await callback.message.edit_text(
# #             text='☑️ Вы успешно удалены! Теперь можете записаться на любой курс',
# #             reply_markup=await make_only_course_managing_keyboard())
# #     else:
# #         await callback.message.edit_text(
# #             text='📌 Вы остались на прежнем курсе',
# #             reply_markup=await make_courses_keyboard())
