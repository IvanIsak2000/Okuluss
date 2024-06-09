import sqlalchemy
from datetime import datetime
from utils.logging.logger import logger

from utils.db.models import async_session
from utils.db.models import Review


async def add_review(
        message: dict,
        review_text: str):

    user = message.from_user
    async with async_session() as session:
        async with session.begin():
            # try:
            local_time = datetime.now()
            session.add(Review(
                user_id=int(user.id),
                username=user.username,
                review_text=review_text,
                send_time=local_time))
            await session.commit()
            await logger.info(
                f'Новый отзыв от {user.id} текст={review_text}',
                extra={'full_data': message})
            # except sqlalchemy.exc.IntegrityError:
            #     session.rollback()
