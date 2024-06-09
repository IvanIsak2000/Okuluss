from sqlalchemy import select

from utils.db.models import async_session
from utils.db.models import Moderator, MainModerator


async def get_main_moderator_id() -> int:
    """Получить id главного модераторы для алёртов"""
    async with async_session() as session:
        async with session.begin():
            query = select(
                MainModerator.user_id).where(
                MainModerator.is_active == True)
            result = await session.execute(query)
            return result.scalar()


async def get_moderators(
        message) -> str:
    """Получить список модеров"""
    user = message.from_user
    moderators = []
    async with async_session() as session:
        async with session.begin():
            query = select(Moderator).where(
                Moderator.is_active == True)
            for i in await session.execute(query):
                moderators.append(f'👷 @{i.Moderator.username}')
        return '\n'.join(moderators)
