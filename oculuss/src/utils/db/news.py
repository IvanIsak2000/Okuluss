from sqlalchemy import update, select
from pydantic import BaseModel


from utils.db.models import News
from utils.logging.logger import logger
from utils.db.models import async_session


async def get_news():   
    class _News(BaseModel):
        id: int
        text: str
        posted: bool


    async with async_session() as session:
        async with session.begin():
            query = select(
                News
            ).where(
                News.posted == False
            ).order_by(News.id.desc())
            for i in await session.execute(query):
                return _News(
                    id=i.News.id,
                    text=i.News.text,
                    posted=i.News.posted
                
                )

async def news_was_posted(news_id: int):
    async with async_session() as session:
        async with session.begin():
            query = update(
                News
            ).where(
                News.id == news_id
            ).values(
                posted=True
            )
            await session.execute(query)
            await session.commit()
            await logger.info(f"Новость {news_id} успешно записана как отправленная ")
