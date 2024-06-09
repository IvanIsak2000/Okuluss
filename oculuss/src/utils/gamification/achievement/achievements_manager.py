import aiogram
import time
import datetime
import asyncio

from utils.db.models import *
from utils.db.user import *
from utils.gamification.achievement.achievements import achievements
from utils.db.achievements import *

class AchievementManager():
    def __init__(self, bot: aiogram.Bot, dp: aiogram.Dispatcher):
        self.bot = bot
        self.dp = dp
 

    async def check_achievements(self):
        await logger.info(f'Проверяем все достижения')

        users = await get_access_users()
        user_data = await get_user_data_for_achievement()
        checked_users = 0
        all_start = datetime.datetime.now()

        for i, j in zip(users, user_data):
            await asyncio.sleep(0.1)
            if i.user_id == j.user_id:
                accept_times = j.accept_record
                if accept_times:
                    if accept_times >= 50:
                        await set_new_achievement(
                            bot=self.bot,
                            user_id=j.user_id,
                            achievement='Целеустремлённый',
                            level_to=3)
                    if accept_times >= 25:
                        await set_new_achievement(
                            bot=self.bot,
                            user_id=j.user_id,
                            achievement='Целеустремлённый',
                            level_to=2)
                    if accept_times >= 5:
                        await set_new_achievement(
                            bot=self.bot,
                            user_id=j.user_id,
                            achievement='Целеустремлённый',
                            level_to=1)
                                                                    

                quiz = j.correct_quiz
                if quiz:

                    if quiz >= 1:
                        await set_new_achievement(
                            bot=self.bot,
                            user_id=j.user_id,
                            achievement='Эрудит',
                            level_to=1
                        )
                    
                    if quiz >= 5:
                        await set_new_achievement(
                            bot=self.bot,
                            user_id=j.user_id,
                            achievement='Эрудит',
                            level_to=2
                        )
                    if quiz >= 15:
                        await set_new_achievement(
                            bot=self.bot,
                            user_id=j.user_id,
                            achievement='Эрудит',
                            level_to=3
                        )

                    if quiz >= 30:
                        await set_new_achievement(
                            bot=self.bot,
                            user_id=j.user_id,
                            achievement='Эрудит',
                            level_to=4
                        )
                    if quiz >= 60:
                        await set_new_achievement(
                            bot=self.bot,
                            user_id=j.user_id,
                            achievement='Эрудит',
                            level_to=5
                        )
                    
                    if quiz >= 180:
                        await set_new_achievement(
                            bot=self.bot,
                            user_id=j.user_id,
                            achievement='Эрудит',
                            level_to=6
                        )
                                                                            
                experience = j.experience
                if experience:

                    if experience >= 5:
                        await set_new_achievement(
                            bot=self.bot,
                            user_id=j.user_id,
                            achievement='Чемпион',
                            level_to=1
                        )
                        
                    if experience >= 20:
                        await set_new_achievement(
                            bot=self.bot,
                            user_id=j.user_id,
                            achievement='Чемпион',
                            level_to=2
                        ) 

                    if experience >= 200:
                        await set_new_achievement(
                            bot=self.bot,
                            user_id=j.user_id,
                            achievement='Чемпион',
                            level_to=3
                        )

                    if experience >= 500:
                        await set_new_achievement(
                            bot=self.bot,
                            user_id=j.user_id,
                            achievement='Чемпион',
                            level_to=4
                        )

                    checked_users += 1
            _end = datetime.datetime.now()
        all_end = datetime.datetime.now()
        await logger.info(f'✅ Достижения проверены за {all_end-all_start} {(checked_users)}/{len(users)}')
                     
