import sqlalchemy
from sqlalchemy import select
from pydantic import BaseModel

from utils.logging.logger import logger

from utils.db.models import async_session
from utils.db.models import Supplementation


class SupplInfo(BaseModel):
    """Класс pydantic с информацией"""
    id: int
    title: str
    description: str | None
    slug: str
    link: list
    image_link: str
    likes: int
    dislikes: int


async def get_supplementation(
        message: dict = None) -> list:
    """Get build-in supplementation"""
    lst = []
    if message is not None:
        async with async_session() as session:
            query = select(Supplementation).order_by(Supplementation.title)
            for i in await session.execute(query):
                one_supplement = Supplementation(
                    id=i.Supplementation.id,
                    title=i.Supplementation.title,
                    description=i.Supplementation.description,
                    slug=i.Supplementation.slug,
                    link=i.Supplementation.link,
                    image_link=i.Supplementation.image_link,
                    likes=i.Supplementation.likes,
                    dislikes=i.Supplementation.dislikes)
                lst.append(one_supplement)
            return lst

    else:
        async with async_session() as session:
            lst = []
            query = select(Supplementation)
            for i in await session.execute(query):
                one_supplement = Supplementation(
                    id=i.Supplementation.id,
                    title=i.Supplementation.title,
                    description=i.Supplementation.description,
                    slug=i.Supplementation.slug,
                    link=i.Supplementation.link,
                    image_link=i.Supplementation.image_link,
                    likes=int(i.Supplementation.likes),
                    dislikes=int(i.Supplementation.dislikes))
                lst.append(one_supplement)
            return lst


async def get_info_from_supplementation_by_id(_id: int):
    """Получить всю информацию о БАДе по id"""
    async with async_session() as session:
        query = select(Supplementation).where(
            Supplementation.id == int(_id))
        for i in await session.execute(query):
            res = SupplInfo(
                id=i.Supplementation.id,
                title=i.Supplementation.title,
                description=i.Supplementation.description,
                slug=i.Supplementation.slug,
                link=i.Supplementation.link,
                image_link=i.Supplementation.image_link,
                likes=int(i.Supplementation.likes),
                dislikes=int(i.Supplementation.dislikes))
            return res


async def get_supplementation_id_by_name(
    name: str
) -> int:
    await logger.info(f'Получение встроенно БАДа по имени: {name}')
    async with async_session() as session:
        async with session.begin():
            query = select(Supplementation).where(
                Supplementation.title == name
            )
            for i in await session.execute(query):
                return i.Supplementation.id     
