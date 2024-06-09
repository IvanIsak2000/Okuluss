import sqlalchemy
import aiogram
from sqlalchemy import (
    select,
    delete,
    update
)
from pydantic import BaseModel
import datetime

from utils.logging.logger import logger 
from utils.db.models import async_session
from utils.db.models import *
from utils.gamification.achievement.achievements import get_only_title_description
from utils.db.user import *
from utils.texts import MY_TIMEZONE


async def send_new_achievement_unblocked(
    bot: aiogram.Bot,
    user_id: int,
    achievement: str,
    level_to: int):
    """Отправить пользователю сообщение что новое достижение было открыто"""
    
    await bot.send_message(
        chat_id=user_id,
        text=f'🎉 Открыто новое достижение: {achievement} {level_to}')   
    await logger.info(f'Сообщение что открыто достижение {achievement} {level_to} для пользователя {user_id} отправлено ')


async def add_new_achievement_record_in_history(
    bot: aiogram.Bot,
    user_id: int,
    achievement_set_to: str,
    level_to: int,
):
    async with async_session() as session:
        async with session.begin():
            try:
                session.add(UserAchievementHistory(
                    user_id=user_id,
                    achievement_set_to=achievement_set_to,
                    level_to=level_to,
                    set_time=datetime.datetime.now(tz=MY_TIMEZONE)
                ))
                await session.commit()
                await logger.info(
                    f'Запись о достижении {achievement_set_to} для пользователя {user_id}')
                await send_new_achievement_unblocked(   
                    bot=bot,
                    user_id=user_id,
                    achievement=achievement_set_to,
                    level_to=level_to
                )
            except sqlalchemy.exc.IntegrityError:
                pass
                         
async def set_new_achievement(
    bot: aiogram.Bot,
    user_id: int,
    achievement: str,
    level_to: int) -> None:
    async with async_session() as session:
        async with session.begin():
            try:
                session.add(UserAchievement(
                    user_id=user_id,
                    achievement=achievement,
                    level=level_to)
                )
                await session.commit()
                await add_new_achievement_record_in_history(
                    bot=bot,
                    user_id=user_id,
                    achievement_set_to=achievement,
                    level_to=level_to
                )
                
            except sqlalchemy.exc.IntegrityError:
                pass

       

async def get_my_achievements(
    user_id: int) -> list:

    class AchievementLevels(BaseModel):
        user_id: int
        achievement: str
        level: int

    achievements_list = []
    async with async_session() as session:
        async with session.begin():
            query = select(UserAchievement).where(
                UserAchievement.user_id == user_id).order_by(UserAchievement.achievement, UserAchievement.level)
            for a in await session.execute(query):
                achievements_list.append(
                    AchievementLevels(
                        user_id=a.UserAchievement.user_id,
                        achievement=a.UserAchievement.achievement,
                        level=a.UserAchievement.level))
            return achievements_list                                    
            

async def get_base_subscription(
    user_id: int) -> bool:
 ...


async def get_accept_count(
    user_id: int) -> int:
    lst = []
    async with async_session() as session:
        async with session.begin():
            query = select(UserAcceptRecording).where(
                (UserAcceptRecording.user_id == user_id) &
                (UserAcceptRecording.accept == True)
            )
            for i in await session.execute(query):
                lst.append(i.UserAcceptRecording.accept)
            return len(lst)                 


async def get_correct_quiz(
    user_id: int) -> int:
    """Получение количества правильных ответов на опросы"""
    lst = []
    async  with async_session() as session:
        async with session.begin():
            query = select(UserQuiz).where(
                (UserQuiz.user_id == user_id) &
                (UserQuiz.correct == True)
            )
            for i in await session.execute(query):  
                lst.append(i.UserQuiz.correct)
            return len(lst)


async def get_user_data_for_achievement() -> list:
    """Получить все данные пользователя для достижений"""
    class User(BaseModel):
        user_id: int
        accept_record: int
        correct_quiz: int
        experience: int

    users = await get_access_users()
    users_list = []
    async with async_session() as session:
        async with session.begin():
            for user in users:
                users_list.append(
                    User(
                        user_id=user.user_id,
                        accept_record=await get_accept_count(user.user_id),
                        correct_quiz=await get_correct_quiz(user.user_id),
                        experience=await get_user_experience(user.user_id)
                    )
                )
            return users_list
            