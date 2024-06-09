from secrets import choice
from sqlalchemy import update, select
from datetime import datetime

from utils.db.models import UserQuiz
from utils.logging.logger import logger
from utils.db.models import async_session
from utils.texts import MY_TIMEZONE

async def select_random_poll() -> dict:
    questions = [
        {
            'question': 'Тормозной нейромедиатор',
            'options': ['GABA', 'GAMMA E', 'Таурин'],
            'correct_option': 0
        },
        {
            'question': 'Мощная антиоксидантная защита',
            'options': ['L-ОптиЦинк', 'Витамин D', 'GAMMA E'],
            'correct_option': 2
        }] 
    return choice(questions)


async def add_new_quiz(
    quiz_hash: str,
    correct_id: int = False,
    message: dict = None,
    message_id: int = None,
    correct: bool = None
) -> None:
    user = message.from_user
    async with async_session() as session:
        async with session.begin():
            session.add(
                UserQuiz(
                    quiz_hash=quiz_hash,
                    correct_id=correct_id,
                    open_time=datetime.now(),
                    user_id=user.id,
                    username=user.username,
                    message_id=message_id,
                    correct=correct
                    ))
            await session.commit()


async def quiz_hash_is_exist(
    quiz_hash: str
):
    await logger.info(f'Проверка на существование вопроса {quiz_hash}')
    async with async_session() as session:
        async with session.begin():
            query = select(
                UserQuiz).where(
                    UserQuiz.quiz_hash == quiz_hash)
            res = await session.execute(query)
            if res.scalar():
                return True
            else:
                return False


async def is_correct_quiz(
    quiz_hash: str,
    suggested_id: int
) -> bool:
    """Получить правильный ответ на опрос для сравнения ответа от пользователя"""
    async with async_session() as session:
        async with session.begin():
            query = select(
                UserQuiz).where(
                    UserQuiz.quiz_hash == quiz_hash)
            for i in await session.execute(query):
                await logger.info(f'Получение правильного ответа на опрос {quiz_hash}, ответ {i.UserQuiz.correct_id}')
                await logger.info(f'suggested_id: {suggested_id} i.UserQuiz.correct_id: {i.UserQuiz.correct_id} {suggested_id == i.UserQuiz.correct_id}')
                return suggested_id == int(i.UserQuiz.correct_id)


async def fill_quiz(
    quiz_hash: str,
    correct: bool) -> None:
    """Дополняет ответ пользователя"""
    async with async_session() as session:
        async with session.begin():
            query = update(UserQuiz).where(
                UserQuiz.quiz_hash == quiz_hash).values(
                    correct=correct)
            await session.execute(query)
            await logger.info(f'Добавление данных для опроса {quiz_hash}  правильный ответ: {correct}')


async def new_quiz_is_available(user_id: int) -> bool:
    """Проверка на то что прошло 24 часа для нового опроса

    Args:
        user_id (int): id пользователя для запроса

    Returns:
        bool: возвращает True, если прошло более 24-ёх часов после предыдущего открытого опроса
    """
    async with async_session() as session:
        async with session.begin():
            query = select(UserQuiz).where(
                UserQuiz.user_id == user_id).order_by(UserQuiz.id.desc())
            for i in await session.execute(query):
                await logger.info(
                    message=f'Проверка на то что прошло более 24 часов после предыдущего открытого опроса {i.UserQuiz.open_time}')
                now_time = datetime.now().astimezone(MY_TIMEZONE)
                time_diff = now_time - i.UserQuiz.open_time
                if time_diff.total_seconds() >= 24 * 3600:
                    return True
                return False