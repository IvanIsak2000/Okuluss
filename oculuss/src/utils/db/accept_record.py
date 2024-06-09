from sqlalchemy import update, select
from utils.logging.logger import logger
from pydantic import BaseModel

from utils.db.models import async_session
from utils.db.models import UserAcceptRecording

# TODO: добавить локальное время в каждую запись


async def add_open_record_of_taking(
        record_hash: str,
        user_id: int,
        supplementation_names: list,
        supplementation_dict: dict,
        record_time: str,
        open_time: str,
        message_id: int,
        accept: bool = None):
    """Добавить приём БАДа юзера в историю без результат приёма"""
    await logger.info(f'all paramets: {record_hash}, {user_id}, {supplementation_names}, {supplementation_dict}, {record_time}, {open_time}, {message_id}, {accept}')
    async with async_session() as session:
        async with session.begin():
            try:
                session.add(UserAcceptRecording(
                    record_hash=record_hash,
                    user_id=user_id,
                    supplementation_names=supplementation_names,
                    supplementation_dict=supplementation_dict,
                    record_time=record_time,
                    open_time=open_time.replace(tzinfo=None),
                    message_id=message_id,
                    accept=accept))
                await session.commit()
                await logger.info(
                    f'Новая незаполнения запись для {user_id}, hash: {record_hash}')
            except Exception as e:
                await logger.critical(e)


async def update_accept_record(
        record_hash: str,
        user_id: int,
        accept: bool):
    await logger.info(f'для обновления: {record_hash}, {user_id}, {accept}')
    async with async_session() as session:
        async with session.begin():
            stmt = update(UserAcceptRecording).where(
                (UserAcceptRecording.user_id == user_id) &
                (UserAcceptRecording.record_hash == record_hash)).values(
                    accept=accept)
            await session.execute(stmt)


async def get_user_accept_history(user_id: int) -> dict[int, int]:
    async with async_session() as session:
        async with session.begin():
            query = select(UserAcceptRecording).where(
                UserAcceptRecording.user_id == user_id)

            successful_accept = 0
            passed_accept = 0
            common = 0

            for i in await session.execute(query):
                if i.UserAcceptRecording.accept == True:
                    successful_accept += 1
                else:
                    passed_accept += 1
                common += 1

            return {
                'common': common,
                'successful': successful_accept,
                'passed': passed_accept}


async def get_record_info_by_hash(
    record_hash: str
):

    class RecordInfo(BaseModel):
        record_hash: str
        # open_time: datetime.datetime
        supplementation_names: list
        supplementation_dict: dict

    async with async_session() as session:
        async with session.begin():
            query = select(UserAcceptRecording).where(
                UserAcceptRecording.record_hash == record_hash)
            for i in await session.execute(query):
                res = RecordInfo(
                    record_hash=i.UserAcceptRecording.record_hash,
                    # open_time=i.UserAcceptRecording.open_time,
                    supplementation_names=i.UserAcceptRecording.supplementation_names,
                    supplementation_dict=i.UserAcceptRecording.supplementation_dict
                )
                return res