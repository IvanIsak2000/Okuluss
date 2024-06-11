from sqlalchemy import (
    MetaData,
    Integer,
    BigInteger,
    Float,
    String,
    Boolean,
    DateTime,
    JSON,
    TEXT,
    UniqueConstraint,
    TIME
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker
)
import datetime
from datetime import timedelta
from utils.config import DSN
from utils.logging.logger import logger

# from utils.texts import MY_TIMEZONE

meta = MetaData()
Base = declarative_base(metadata=meta)

engine = create_async_engine(DSN)
async_session = async_sessionmaker(engine)


class Supplementation(Base):
    """
    Класс встроенных добавок
    Параметры:

    - title - название
    - description - описание
    - slug -  короткое название
    - link - ссылка на сайт + по возможности промокод в ()
    - image_link - ссылка на изображение из s3
    - likes - количество лайков
    - dislikes - количество дизлайков
    """
    __tablename__ = "supplementation"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(50), unique=True)
    description: Mapped[str] = mapped_column(TEXT)
    slug: Mapped[str] = mapped_column(String(50))
    link: Mapped[list] = mapped_column(ARRAY(String))
    image_link: Mapped[str] = mapped_column(String(200), default='None')
    likes: Mapped[int] = mapped_column(Integer, default=0)
    dislikes: Mapped[int] = mapped_column(Integer, default=0)


class SupplementationRateVote(Base):
    """Класс рейтинга встроенных добавок

    Args:
        Base (_type_): _description_
    """
    __tablename__ = "supplementation_rate_vote"
    id: Mapped[int] = mapped_column(primary_key=True)
    supplementation_group: Mapped[str] = mapped_column(String(50))
    voted_id: Mapped[int] = mapped_column(BigInteger)
    voted_name: Mapped[str] = mapped_column(String)
    rate: Mapped[int] = mapped_column(Integer) # 1 or -1


class UserCustomSupplementation(Base):
    __tablename__ = "users_supplementation"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    supplementation_hash: Mapped[str] = mapped_column(String)
    name: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String, default=None)
    dose: Mapped[float] = mapped_column(Float)
    time: Mapped[str] = mapped_column(TIME)
    count: Mapped[float] = mapped_column(Float)
    CONSTANT_COUNT: Mapped[float] = mapped_column(Float)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class UserAcceptRecording(Base):
    __tablename__ = "user_accept_recording"
    id: Mapped[int] = mapped_column(primary_key=True)
    record_hash: Mapped[str] = mapped_column(String)
    supplementation_names: Mapped[list] = mapped_column(ARRAY(String))
    user_id: Mapped[int] = mapped_column(BigInteger)
    supplementation_dict: Mapped[dict] = mapped_column(JSON)
    record_time: Mapped[str] = mapped_column(String)
    open_time: Mapped[str] = mapped_column(DateTime(timezone=True))
    message_id: Mapped[int] = mapped_column(BigInteger)
    accept: Mapped[bool] = mapped_column(Boolean, default=None)


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


class UserCourse(Base):
    __tablename__ = "user_course"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    username: Mapped[str] = mapped_column(String)
    full_name: Mapped[str] = mapped_column(String)
    course_name: Mapped[str] = mapped_column(String)
    start_time: Mapped[str] = mapped_column(DateTime(timezone=True))
    end_time: Mapped[str] = mapped_column(DateTime(timezone=True))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class UserQuiz(Base):
    __tablename__ = "user_quiz"
    id: Mapped[int] = mapped_column(primary_key=True)
    quiz_hash: Mapped[str] = mapped_column(String, unique=True)
    correct_id: Mapped[int] = mapped_column(Integer)
    user_id: Mapped[int] = mapped_column(BigInteger)
    username: Mapped[str] = mapped_column(String)
    correct: Mapped[int] = mapped_column(Boolean, default=None)
    open_time: Mapped[str] = mapped_column(DateTime(timezone=True))
    message_id: Mapped[int] = mapped_column(BigInteger)


class Stack(Base):
    __tablename__ = 'stack'
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(TEXT)
    supplementation_names: Mapped[list] = mapped_column(ARRAY(String))
    link: Mapped[str] = mapped_column(String)
    
    
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


class UserAchievement(Base):
    __tablename__ = "user_achievement"
    id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    achievement: Mapped[str] = mapped_column(String)
    level: Mapped[int] = mapped_column(Integer)
    __table_args__ = (
        UniqueConstraint('achievement', 'level', 'user_id', name='uq_achievement_level_user_id'),
    )


class UserAchievementHistory(Base):
    __tablename__ = "user_achievement_history"
    id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    achievement_set_to: Mapped[str] = mapped_column(String)
    level_to: Mapped[int] = mapped_column(Integer)
    set_time: Mapped[str] = mapped_column(DateTime(timezone=True))
    __table_args__ = (
        UniqueConstraint('achievement_set_to', 'level_to', 'user_id', name='uq_achievement_set_to_level_to_user_id'),
    )


class News(Base):
    __tablename__ = "news"
    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(TEXT)
    posted: Mapped[bool] = mapped_column(Boolean, default=False)


async def init_db():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(meta.create_all)
            await logger.info('✅ БД созданы')
    except Exception as e:
        if "already exists" in str(e):
            await logger.info('✅ БД уже существуют')
        else:
            await logger.critical(f'Databases crashed: {e}')


async def time_after_month(_time):
    one_month = timedelta(days=30)
    _time_after_month = _time + one_month
    return _time_after_month

