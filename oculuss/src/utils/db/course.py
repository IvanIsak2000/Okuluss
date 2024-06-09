import sqlalchemy
from sqlalchemy import (
    select,
    delete
)
from datetime import datetime

from utils.logging.logger import logger

from utils.db.models import async_session
from utils.db.models import UserCourse
from utils.db.models import time_after_month
from utils.texts import MY_TIMEZONE


async def user_course(message: dict) -> str:
    user = message.from_user
    async with async_session() as session:
        async with session.begin():
            query = select(UserCourse.course_name).where(
                UserCourse.user_id == int(user.id))
            result = await session.execute(query)
            await logger.info(
                f'Получение названия курса для id={user.id}',
                extra={'full_data': message})
            return result.scalar()


async def user_have_course(message: dict) -> bool:
    """True если у юзер есть курс, иначе False"""
    user = message.from_user
    async with async_session() as session:
        async with session.begin():
            try:
                query = select(UserCourse.course_name).where(
                    UserCourse.user_id == int(user.id))
                result = await session.execute(query)
                if result.scalar():
                    return True
                else:
                    await logger.info(
                        f'Нет курса для id={user.id}',
                        extra={'full_data': message})
                    return False
            except sqlalchemy.exc.DataError as e:
                await logger.info(e)
                pass


async def add_user_to_course(
        message: dict,
        course_name: str) -> None:
    """Записать юзера на курс"""
    user = message.from_user
    async with async_session() as session:
        async with session.begin():
            try:
                local_time = datetime.now()
                session.add(UserCourse(
                    user_id=int(user.id),
                    username=user.username,
                    full_name=user.full_name,
                    course_name=course_name,
                    start_time=local_time.astimezone(MY_TIMEZONE),
                    end_time=await time_after_month(local_time)))
                await session.commit() 
                await logger.info(
                    f'Добавлен курс {course_name} для id={user.id}',
                    extra={'full_data': message})
            except sqlalchemy.exc.IntegrityError:
                pass


async def remove_user_from_course(
        message: dict) -> None:
    """Удалить юзера из курса"""
    user = message.from_user
    async with async_session() as session:
        async with session.begin():
            try:
                query = delete(UserCourse).where(
                    UserCourse.user_id == int(user.id))
                await session.execute(query)
                await session.commit()
                await logger.info(
                    f'Удалён курс для id={user.id}',
                    extra={'full_data': message})
            except sqlalchemy.exc.IntegrityError:
                pass


async def get_users_written_in_courses() -> str:
    """Получить юзеров записанных на курсы"""
    async with async_session() as session:
        async with session.begin():
            query = select(UserCourse)
            result = await session.execute(query) 
            return result.scalars().all()
