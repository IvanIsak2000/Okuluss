import sqlalchemy
from sqlalchemy import select, update
from pydantic import BaseModel

from utils.logging.logger import logger

from utils.db.models import async_session
from utils.db.models import Supplementation, SupplementationRateVote
       

async def add_user_vote_to_history(
        user_id: int,
        username: str,
        supplementation_group: str,
        rate: int):
    """Добавление оценки, отзыва в таблицу SupplementationRateVote"""
    if rate == 1 or rate == -1:
        async with async_session() as session:
            async with session.begin():
                session.add(SupplementationRateVote(
                    supplementation_group=supplementation_group,
                    voted_id=user_id,
                    voted_name=username,
                    rate=rate))
                await logger.info(
                    f'Добавление оценки: {user_id}, {supplementation_group}, {rate}')
    else:
        raise ValueError(f'Неверный рейтинг: {rate}')


async def update_supplementation_rate(
        user_id: int,
        username: str,
        supplementation_group: str,
        rate: int):
    await logger.info(f'изменения рейтинга: {user_id}, {supplementation_group}, {rate}, {type(rate)}, {rate==1}')
    async with async_session() as session:
        async with session.begin():
            if rate == 1:
                query = update(Supplementation).where(
                    Supplementation.title == supplementation_group).values(
                    likes=Supplementation.likes+1)
                await session.execute(query)
                await logger.info(f'+1 рейтинга: {supplementation_group} от {user_id}')
                await add_user_vote_to_history(
                    user_id=user_id,
                    username=username,
                    supplementation_group=supplementation_group,
                    rate=rate)
            else:
                if rate == -1:
                    query = update(Supplementation).where(
                        Supplementation.title == supplementation_group).values(
                        dislikes=Supplementation.dislikes+1)
                    await session.execute(query)
                    await logger.info(f'-1 рейтинга: {supplementation_group} от {user_id}')
                    await add_user_vote_to_history(
                        user_id=user_id,
                        username=username,
                        supplementation_group=supplementation_group,
                        rate=rate)
    

async def get_supplementation_rating() -> str:
    """Получение рейтинга добавок"""
    lst = []
    async with async_session() as session:
        query = select(Supplementation).order_by(
            Supplementation.likes.desc())
        for i in await session.execute(query):
            lst.append(
                f'{i.Supplementation.title}\n👍 {i.Supplementation.likes} 👎 {i.Supplementation.dislikes}')
        return '\n'.join(lst)
        await logger.info(f'Получение рейтинга добавок. Результат: {lst}')


     
