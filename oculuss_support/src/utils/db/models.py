import sqlalchemy
from sqlalchemy import update
from sqlalchemy import (
    MetaData,
    String,
    BigInteger,
    select,
    delete,
    String,
    Boolean,
    Integer,
    DateTime)
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from pydantic import BaseModel

from utils.config import DSN
from utils.logging.logger import logger
from utils.texts import MY_TIMEZONE

from datetime import timedelta

meta = MetaData()
Base = declarative_base(metadata=meta)

engine = create_async_engine(DSN)
async_session = async_sessionmaker(engine)


class KnowUser(Base):
    __tablename__ = 'know_user'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, unique=True)
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    username: Mapped[str] = mapped_column(String)
    full_name: Mapped[str] = mapped_column(String)
    join_time: Mapped[str] = mapped_column(DateTime(timezone=True))


class SupplementationAccess(Base):
    __tablename__ = "supplementation_access"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    username: Mapped[str] = mapped_column(String)
    full_name: Mapped[str] = mapped_column(String)
    buy_time: Mapped[int] = mapped_column(DateTime(timezone=True))
    end_time: Mapped[int] = mapped_column(DateTime(timezone=True))
    is_ban: Mapped[bool] = mapped_column(Boolean, default=False)
    experience: Mapped[int] = mapped_column(Integer, default=0)


class UtilizedHash(Base):
    __tablename__ = "utilized_hash"
    id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    username: Mapped[str] = mapped_column(String)
    hash: Mapped[str] = mapped_column(String)
    order_hash: Mapped[str] = mapped_column(String)
    time: Mapped[str] = mapped_column(DateTime(timezone=True))


class Moderator(Base):
    __tablename__ = "moderator"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    username: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean)


class MainModerator(Base):
    __tablename__ = "main_moderator"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    username: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean)


class Review(Base):
    __tablename__ = "review"
    id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    username: Mapped[str] = mapped_column(String)
    review_text: Mapped[str] = mapped_column(String)
    send_time: Mapped[str] = mapped_column(DateTime(timezone=True))


async def init_db():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(meta.create_all)
            logger.info('All databases are created')
    except Exception as e:
        if "already exists" in str(e):
            logger.info('✅ Databases are already initialized')
        else:
            logger.critical(f'Databases crashed: {e}')


# TODO: изменить время на UTC
async def time_after_month(_time: datetime):
    return _time + timedelta(days=30)


async def add_know_user(
        message: dict):
    _user = message.from_user
    async with async_session() as session:
        async with session.begin():
            try:
                local_time = datetime.now()
                user = KnowUser(
                    user_id=_user.id,
                    username=_user.username,
                    full_name=_user.full_name,
                    join_time=local_time)
                session.add(user)
                await session.commit()
                logger.info(
                    f'New user with id={_user.id}\
                        name={_user.full_name} added',
                    extra={'full_data': message})
            except sqlalchemy.exc.IntegrityError:
                logger.info(
                    'User is known',
                    extra={'full_data': message})


async def get_know_users():
    """Получения пройденных пользователей"""
    async with async_session() as session:
        async with session.begin():
            logger.info('Request to get know users')
            return await session.query(KnowUser).all()


async def is_banned_user(user_id: int) -> bool:
    async with async_session() as session:
        async with session.begin():
            query = select(SupplementationAccess.is_ban).where(
                SupplementationAccess.user_id == user_id)
            result = await session.execute(query)
            if result.scalar():
                logger.info(f'Юзер с id={user_id} забанен')
                return True
            else:
                logger.info(f'Юзер с id={user_id} не забанен')
                return False


async def is_access_user(
        message: dict = None,
        user_id: int = None) -> bool:
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
                    logger.info(
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
                    logger.info(
                            f'У пользователя с id={user_id} нет доступа для мониторинга')
                    return False


async def add_new_access_user(
        message: dict):
    """Добавление нового пользователя доступа"""
    user = message.from_user
    local_time = datetime.now()
    async with async_session() as session:
        async with session.begin():
            # try:
            if await is_access_user(message=message):
                update_access = update(
                    SupplementationAccess).where(
                    SupplementationAccess.user_id == user.id).values(
                        buy_time=local_time.replace(tzinfo=None),
                        end_time=(
                            await time_after_month(
                                _time=local_time)).replace(tzinfo=None))
                logger.info(f'Обновлён доступ для пользователя {user.id}')
                await session.execute(update_access)
            else:
                session.add(SupplementationAccess(
                    user_id=user.id,
                    username=user.username,
                    full_name=user.full_name,
                    buy_time=local_time.replace(tzinfo=None),
                    end_time=(await time_after_month(
                            _time=local_time)).replace(
                                tzinfo=None
                    )))
                await session.commit()
                logger.info(
                    f'Новый пользователь с доступом {user.id} добавлен',
                    extra={'full_data': message})
                # except sqlalchemy.exc.IntegrityError:
                #     await session.rollback()


async def get_access_users() -> list:
    """Получить пользователей с доступом """
    class User(BaseModel):
        user_id: int
        buy_time: datetime
        end_time: datetime

    users = []
    async with async_session() as session:
        async with session.begin():
            query = select(SupplementationAccess).where()
            for i in await session.execute(query):
                user = User(
                    user_id=int(i.SupplementationAccess.user_id),
                    buy_time=i.SupplementationAccess.buy_time.replace(tzinfo=None),
                    end_time=i.SupplementationAccess.end_time.replace(tzinfo=None))
                users.append(user)
        return users


async def remove_user_from_access(user_id: int):
    """Удалить доступ у пользователя"""
    async with async_session() as session:
        async with session.begin():
            try:
                query = delete(SupplementationAccess).where(
                    SupplementationAccess.user_id == user_id
                )
                await session.execute(query)
                await session.commit()
                logger.info(
                    f'User with id={user_id} removed from access')
            except sqlalchemy.exc.IntegrityError:
                await session.rollback()


async def get_access_user_data(user_id: int) -> dict:
    """Получить данные о доступе пользователя"""
    class User(BaseModel):
        user_id: int
        buy_time: datetime
        end_time: datetime

    async with async_session() as session:
        async with session.begin():
            query = select(SupplementationAccess).where(SupplementationAccess.user_id == user_id)
            for i in await session.execute(query):
                user = User(
                    user_id=int(i.SupplementationAccess.user_id),
                    buy_time=i.SupplementationAccess.buy_time.astimezone(tz=MY_TIMEZONE).strftime("%Y-%m-%d %H:%M:%S"),
                    end_time=i.SupplementationAccess.end_time.astimezone(tz=MY_TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")
                )
                return user


async def add_review(
        message: dict,
        review_text: str):

    user = message.from_user
    async with async_session() as session:
        async with session.begin():
            try:
                local_time = datetime.now()
                session.add(Review(
                    user_id=int(user.id),
                    username=user.username,
                    review_text=review_text,
                    send_time=local_time))
                await session.commit()
                logger.info(
                    f'New user`s review with id={int(user.id)},\
                    text="{review_text}" successfully added',
                    extra={'full_data': message})
            except sqlalchemy.exc.IntegrityError:
                await session.rollback()


async def get_main_moderator_id() -> int:
    """Получить id главного модератора"""
    async with async_session() as session:
        async with session.begin():
            query = select(
                MainModerator.user_id).where(
                MainModerator.is_active==True)
            result = await session.execute(query)
            return result.scalar()


async def get_moderators(
        message) -> str:
    user = message.from_user
    moderators = []
    async with async_session() as session:
        async with session.begin():
            query = select(Moderator).where(
                Moderator.is_active==True)
            for i in await session.execute(query):
                moderators.append(f'👷 @{i.Moderator.username}')
        logger.info(
            f'User with id={user.id} completed request to get moderators',
            extra={'full_data': message})
        return '\n'.join(moderators)


async def add_utilized_hash(
        user_id: int,
        username: str,
        hash: str,
        order_hash: str) -> None:
    async with async_session() as session:
        async with session.begin():
            # try:
            local_time = datetime.now()
            session.add(UtilizedHash(
                user_id=user_id,
                username=username,
                hash=hash,
                order_hash=order_hash,
                time=local_time))
            await session.commit()
            logger.info(
                f'Утилизирован hash={hash} от {user_id}')
            # except sqlalchemy.exc.IntegrityError:
            #     await session.rollback()


async def hash_was_used(
        hash: str) -> bool:
    async with async_session() as session:
        async with session.begin():
            query = select(UtilizedHash).where(
                UtilizedHash.hash == hash)
            result = await session.execute(query)
            if result.scalar():
                logger.info(
                    f'Hash {hash} was used')
                return True
            logger.info(
                f'Hash {hash} was not used')
            return False
