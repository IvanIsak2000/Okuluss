from sqlalchemy import update, select
from datetime import datetime

from utils.db.models import Stack
from utils.logging.logger import logger
from utils.db.models import async_session
from utils.texts import MY_TIMEZONE


async def stack_is_exist(title: str) -> bool:
    async with async_session() as session:
        async with session.begin():
            query = select(Stack.title).where(
                Stack.title == title)
        res = await session.execute(query)
        if res.scalar():
            return True
        else:
            return False


async def get_stacks_titles() -> list:
    lst = []
    async with async_session() as session:
        async with session.begin():
            query = select(Stack)
            for i in await session.execute(query):
                lst.append(i.Stack.title)
    return lst

async def get_stack_description(title: str) -> str:
    """Получение описания стака по имени

    Args:
        title (str)

    Returns:
        str
    """
    async with async_session() as session:
        async with session.begin():
            query = select(Stack).where(Stack.title == title)
            for i in await session.execute(query):
                return i.Stack.description


async def get_supplementation_from_stack(
    stack_title: str) -> list:
    async with async_session() as session:
        async with session.begin():
            query = select(
                Stack
            ).where(
                Stack.title == stack_title
            
            )
        for i in await session.execute(query):
            return i.Stack.supplementation_names
                            
                                
async def get_stack_link(title: str) -> str:
    async with async_session() as session:
        async with session.begin():
            query = select(Stack).where(Stack.title == title)
            for i in await session.execute(query):
                return i.Stack.link


