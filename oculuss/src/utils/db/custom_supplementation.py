import sqlalchemy
from sqlalchemy import (
    select,
    delete,
    update
)
from datetime import datetime
from pydantic import BaseModel
import datetime


from utils.logging.logger import logger
from utils.db.models import async_session
from utils.db.models import UserCustomSupplementation
from utils.db.accept_record import get_record_info_by_hash


async def add_new_user_custom_supplementation(
        message: dict,
        name: str,
        supplementation_hash: str, 
        dose: float,
        time: str,
        count: float
) -> None:
    # try:
    _user = message.from_user
    async with async_session() as session:
        async with session.begin():
            user = UserCustomSupplementation(
                user_id=_user.id,
                supplementation_hash=supplementation_hash,
                name=name,
                dose=dose,
                time=time,
                count=count,
                CONSTANT_COUNT=count,
                is_active=True)
            session.add(user)
            await session.commit()
            await logger.info(
                f'БАД {name} успешно добавлен для пользователя {_user.id}',
                extra={
                    'full_data': message,
                    'supp_name': name,
                    'dose': dose,
                    'time': time})
    # except Exception as e:
    #     await logger.critical(
    #         f'Добавление с ошибкой: {e}', extra={'full_data': message})   
    #     raise e


async def get_user_custom_supplementation(
        message: dict = None,
        user_id: int = None
) -> list | None:
    """Получить БАды пользователя по message или по user_id"""

    class UserSupplementation(BaseModel):
        user_id: int
        name: str
        supplementation_hash: str
        dose: float
        description: str | None
        time: str
        count: float
        accept: bool = None
        is_active: bool

    try:
        if message is not None:
            async with async_session() as session:
                user = message.from_user
                custom_supplementation = []
                async with async_session() as session:
                    query = select(
                        UserCustomSupplementation).where(
                            UserCustomSupplementation.user_id == user.id).order_by(
                                UserCustomSupplementation.time)
                    for i in await session.execute(query):
                        data = UserSupplementation(
                            user_id=user.id,
                            supplementation_hash=i.UserCustomSupplementation.supplementation_hash,
                            name=i.UserCustomSupplementation.name,
                            dose=i.UserCustomSupplementation.dose,
                            time=str(i.UserCustomSupplementation.time)[0:5],
                            count=i.UserCustomSupplementation.count,
                            description=i.UserCustomSupplementation.description,
                            is_active=i.UserCustomSupplementation.is_active
                        )
                        custom_supplementation.append(data)
                    await logger.info(
                        f'Получение пользовательских БАДов для пользователя {user.id}',
                        extra={'full_data': message})
                    return custom_supplementation
        else:
            custom_supplementation = []
            async with async_session() as session:
                query = select(
                    UserCustomSupplementation).where(
                        UserCustomSupplementation.user_id == user_id).order_by(
                            UserCustomSupplementation.time)
                for i in await session.execute(query):
                    data = UserSupplementation(
                        user_id=user_id,
                        supplementation_hash=i.UserCustomSupplementation.supplementation_hash,
                        name=i.UserCustomSupplementation.name,
                        dose=i.UserCustomSupplementation.dose,
                        time=str(i.UserCustomSupplementation.time)[0:5],
                        count=i.UserCustomSupplementation.count,
                        description=i.UserCustomSupplementation.description,
                        is_active=i.UserCustomSupplementation.is_active)
                    custom_supplementation.append(data)
                return custom_supplementation
    except Exception as e:
        await logger.critical(
            f'Получение с ошибкой: {e}', extra={'full_data': message})
        raise e
    

async def get_user_custom_supplementation_by_hash(
        user_id: int,
        supplementation_hash: str
) -> list:
    """Получить информацию только об одном пользовательском БАДе по хэшу"""
    await logger.info(f'get_user_custom_supplementation_by_hash {user_id} {supplementation_hash}')
    class UserSupplementation(BaseModel):
        user_id: int
        supplementation_hash: str
        name: str
        dose: float
        description: str | None
        time: str
        count: float
        accept: bool = None
        is_active: bool

    try:
        async with async_session() as session:
            query = select(UserCustomSupplementation).where(
                (UserCustomSupplementation.supplementation_hash == supplementation_hash) &
                (UserCustomSupplementation.user_id == user_id)
            ).order_by(
                UserCustomSupplementation.time)
            for i in await session.execute(query):
                return UserSupplementation(
                    user_id=user_id,
                    supplementation_hash=i.UserCustomSupplementation.supplementation_hash,
                    name=i.UserCustomSupplementation.name,
                    dose=i.UserCustomSupplementation.dose,
                    time=str(i.UserCustomSupplementation.time)[0:5],
                    count=i.UserCustomSupplementation.count,
                    description=i.UserCustomSupplementation.description,
                    is_active=i.UserCustomSupplementation.is_active
                )
    except Exception as e:
        await logger.critical(
            f'Получение добавки по имени с ошибкой: {e}')
        raise e
    

async def get_user_custom_supplementation_by_name(
    user_id: int,
    supplementation_name: str
) -> list:
    """Получить информацию только об одном пользовательском БАДе по имени"""

    await logger.info(f'get_user_custom_supplementation_by_name {user_id} {supplementation_name}')

    class UserSupplementation(BaseModel):
        user_id: int
        supplementation_hash: str
        name: str
        dose: float
        description: str | None
        time: str
        count: float
        accept: bool = None
        is_active: bool

    try:
        async with async_session() as session:
            query = select(UserCustomSupplementation).where(
                (UserCustomSupplementation.name == supplementation_name) &
                (UserCustomSupplementation.user_id == user_id)
            ).order_by(
                UserCustomSupplementation.time)
            for i in await session.execute(query):
                return UserSupplementation(
                    user_id=user_id,
                    supplementation_hash=i.UserCustomSupplementation.supplementation_hash,
                    name=i.UserCustomSupplementation.name,
                    dose=i.UserCustomSupplementation.dose,
                    time=str(i.UserCustomSupplementation.time)[0:5],
                    count=i.UserCustomSupplementation.count,
                    description=i.UserCustomSupplementation.description,
                    is_active=i.UserCustomSupplementation.is_active
                )
    except Exception as e:
        await logger.critical(
            f'Получение добавки по имени с ошибкой: {e}')
        raise e
    

async def remove_user_custom_supplementation(
        message: dict,
        supplementation_hash: str
):
    """Удалить пользовательский БАД"""
    try:
        user = message.from_user
        async with async_session() as session:
            async with session.begin():
                try:
                    query = delete(UserCustomSupplementation).where(
                        (UserCustomSupplementation.user_id == user.id) &
                        (UserCustomSupplementation.supplementation_hash == supplementation_hash))
                    await session.execute(query)
                    await session.commit()
                    await logger.info(
                        f'БАД {supplementation_hash} успешно удален пользователем {user.id}',
                        extra={
                            'full_data': message
                        })
                except sqlalchemy.exc.IntegrityError as e:
                    await logger.critical(
                        f'Ошибка добавления БАДов: {e}',
                        extra={'full_data': message})
                    await session.rollback()
    except Exception as e:
        await logger.info(
            f'Удаление  добавки с ошибкой: {e}', extra={
                'full_data': message
            })
        raise e


async def remove_ended_user_supplementation(
    user_id: int,
    supplementation_hash: str
):
    """Удаление БАДа по окончанию"""

    async with async_session() as session:
        async with session.begin():
            query = delete(UserCustomSupplementation).where(
                (UserCustomSupplementation.user_id == user_id) &
                (UserCustomSupplementation.supplementation_hash == supplementation_hash))
            await session.execute(query)
            await session.commit()
            await logger.info(f'Закончился БАД {supplementation_hash} для {user_id}')


async def is_active_supplementation(
    user_id: int, 
    supplementation_hash: str
) -> bool:
    await logger.info(f'is_active_supplementation {user_id} {supplementation_hash}')
    async with async_session() as session:
        async with session.begin():
            query = select(UserCustomSupplementation).where(
                (UserCustomSupplementation.user_id == user_id) &
                (UserCustomSupplementation.supplementation_hash == supplementation_hash)
            )
            for i in await session.execute(query):
                return i.UserCustomSupplementation.is_active


async def turn_on_supplementation(
    user_id: int, 
    supplementation_hash: str
):
    async with async_session() as session:
        async with session.begin():
            query = update(UserCustomSupplementation).where(
                (UserCustomSupplementation.user_id == user_id) &
                (UserCustomSupplementation.supplementation_hash == supplementation_hash)
            ).values(is_active = True)  
            await session.execute(query)


async def turn_off_supplementation(
    user_id: int, 
    supplementation_hash: str):
    async with async_session() as session:
        async with session.begin():
            query = update(UserCustomSupplementation).where(
                (UserCustomSupplementation.user_id == user_id) &
                (UserCustomSupplementation.supplementation_hash == supplementation_hash)
            ).values(is_active = False)   
            await session.execute(query)
                               

async def minus_accept_count(
        user_id: int,
        record_hash:  str
):
    """
    Отнять принятое количество от количество
    """
    await logger.info(f'minus_accept_count {user_id} {record_hash}')
    data = await get_record_info_by_hash(record_hash=record_hash)
    await logger.info(f'data is {data}')
    for name in data.supplementation_names:
        async with async_session() as session:
            async with session.begin():
                # try:

                supplementation = await get_user_custom_supplementation_by_name(
                    user_id=user_id,
                    supplementation_name=name
                )
                await logger.info(f'supplementation is {supplementation}')
                await logger.info(f'Отнять дозы {supplementation.dose} БАДа {supplementation.name} для {user_id}')

                query = update(UserCustomSupplementation).where(
                    (UserCustomSupplementation.name == supplementation.name) &
                    (UserCustomSupplementation.user_id == user_id)
                    ).values(
                        count=UserCustomSupplementation.count-float(supplementation.dose)
                    )
                await session.execute(query)
                await session.commit()
                await logger.info(
                    f'Вычтен приём: доза {supplementation.dose} БАДа {supplementation.name} для {supplementation.user_id}')
                
                # except AttributeError:
                #     await logger.info(
                #         f'Похоже пользователь {user_id} сначала удалил БАД {name}, а потом получил по нему уведомление\n Exception: {e}')


async def get_user_supplementation_count(user_id: int) -> int:
    """Получить количество БАДов пользователя"""
    count = 0 

    async with async_session() as session:
        async with session.begin():
            query = select(UserCustomSupplementation).where(
                UserCustomSupplementation.user_id == user_id)
            for i in await session.execute(query):
                count += 1
    return count                                 
