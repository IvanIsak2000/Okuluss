from sqlalchemy import select, update, func
from collections import OrderedDict
from pydantic import BaseModel


from utils.logging.logger import logger

from utils.db.models import async_session
from utils.db.models import SupplementationAccess


async def is_banned_user(user_id: int) -> bool:
    async with async_session() as session:
        query = select(SupplementationAccess.is_ban).where(
            SupplementationAccess.user_id == user_id)
        result = await session.execute(query)
        banned = result.scalars().first()
        if banned:
            await logger.info(f'У пользователя {user_id} есть бан')
            return True
        return False


async def is_access_user(
        message: dict = None,
        user_id: int = None
) -> bool:
    """Проверка что пользователь имеет доступ

    Если послано сообщение, то отправляет полную информацию в логгирование.
    Если дан только user_id, значит для мониторинга."""

    if message is not None:
        user = message.from_user
        async with async_session() as session:
            async with session.begin():
                query = select(SupplementationAccess).where(
                    SupplementationAccess.user_id == int(user.id))
                result = await session.execute(query)
                if result.scalar():
                    return True
                else:
                    await logger.info(
                        f'Нет доступа у юзера id={user.id}',
                        extra={'full_data': message})
                    return False
    else:
        async with async_session() as session:
            async with session.begin():
                query = select(SupplementationAccess).where(
                    SupplementationAccess.user_id == user_id)
                result = await session.execute(query)
                if result.scalar():
                    return True
                else:
                    await logger.info(
                            f'У пользователя с id={user_id} нет доступа для мониторинга')
                    return False


async def get_access_users() -> list:
    """Получить пользователей с доступом """
    class User(BaseModel):
        user_id: int
        buy_time: str
        end_time: str

    users = []
    async with async_session() as session:
        async with session.begin():
            query = select(SupplementationAccess).where()
            for i in await session.execute(query):
                user = User(
                    user_id=int(i.SupplementationAccess.user_id),
                    buy_time=str(
                        i.SupplementationAccess.buy_time.replace(tzinfo=None)),
                    end_time=str(
                        i.SupplementationAccess.end_time.replace(tzinfo=None)))
                users.append(user)
        return users


async def update_user_experience(
        user_id: int,
        count: int):
    "Обновление звёзд пользователя"
    async with async_session() as session:
        async with session.begin():
            query = update(SupplementationAccess).where(
                SupplementationAccess.user_id == user_id).values(
                    experience=SupplementationAccess.experience+count)
            await session.execute(query)
            await logger.info(f'Обновление опыта {count} для пользователя {user_id}')


async def get_user_experience(
        user_id: int):
    """Получение опыта пользователя"""
    async with async_session() as session:
        async with session.begin():
            query = select(SupplementationAccess).where(
                SupplementationAccess.user_id == user_id)
            for i in await session.execute(query):
                return i.SupplementationAccess.experience

            await logger.info(f'Получение опыта для пользователя {user_id}')


# async def get_users_by_experience():
#     async with async_session() as session:
#         async with session.begin():
#             query = select(SupplementationAccess.user_id,
#                            SupplementationAccess.experience).where(
#                 SupplementationAccess.experience > 0)
#             result = await session.execute(query)
#             return result.all()


async def get_user_position_by_experience(user_id: int):
    async with async_session() as session:
        async with session.begin():
            query = select(SupplementationAccess).order_by(SupplementationAccess.experience.desc())
            dct = OrderedDict()
            for i in await session.execute(query):
                dct[i.SupplementationAccess.user_id] = i.SupplementationAccess.experience

            position = 0            
            for k,v in dct.items():
                position += 1
                if k == user_id:
                    return position