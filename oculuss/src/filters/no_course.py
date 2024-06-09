from aiogram.filters import Filter
from aiogram import types
from utils.db.user import is_access_user
from utils.db.course import user_have_course


class HaveCourse(Filter):
    def __init__(self) -> None:
        pass

    async def __call__(self, message: types.Message) -> bool:
        return await user_have_course(message=message)


class HaveNotCourse(Filter):
    def __init__(self) -> None:
        pass
    
    async def __call__(self, message: types.Message) -> bool:
        return not await user_have_course(message=message)
