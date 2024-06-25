import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot, Dispatcher
from aiogram import types
import redis

from utils.config import BOT_KEY
from utils.logging.logger import logger

from middlewares.user_ban import CheckUserWasBannedMiddleware
from middlewares.events_mv import MessageLoggingMiddleware
from middlewares.access_mw import CheckAccessMiddleware
from utils.monitoring import Monitor
from utils.gamification.daily_question import Poll
from utils.gamification.achievement.achievements_manager import AchievementManager
from utils.gamification.feeling.feeling_monitoring import Feeling

from utils.news.news_monitoring import NewsMonitoring



bot = Bot(token=BOT_KEY)
dp = Dispatcher()


async def bot_task(bot: bot, dp: Dispatcher):
    try:
        from utils.db.models import init_db
        await init_db()
        
        from handlers import (
            main_handler, 
            other_callbacks, 
            send_review,
            new_supplementation, 
            supplementation_rate, 
            custom_supplementation, 
            build_in_supplementation, 
            stack, 
            quiz_handler,
            tasks
        )

        await logger.info('☑️ Запуск бота...', send_alert=True)

        dp.include_routers(
            main_handler.router,
            other_callbacks.router,
            send_review.router,
            new_supplementation.router,
            # courses.router,
            supplementation_rate.router,
            custom_supplementation.router,
            build_in_supplementation.router,
            stack.router,
            quiz_handler.router,
            tasks.router,
        )

        dp.message.middleware(CheckUserWasBannedMiddleware())
        dp.message.middleware(MessageLoggingMiddleware())
        dp.message.middleware(CheckAccessMiddleware())
        
        await logger.info('✅ Бот запущен', send_alert=True)

        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, polling_timeout=11)
    except KeyboardInterrupt:
        await logger.info(message='Bot manually stopped', send_alert=True)
    finally:
        await logger.info(message='🏁 Bot stopped', send_alert=True)


async def additional_tasks(bot, dp):
    scheduler = AsyncIOScheduler()

    monitor = Monitor(bot=bot, dp=dp)
    scheduler.add_job(monitor.user_monitoring, 'cron', hour='*', minute=0)
    # scheduler.add_job(monitor.user_monitoring, 'interval', seconds=10)

    achievement_manager = AchievementManager(bot=bot, dp=dp)
    scheduler.add_job(achievement_manager.check_achievements, 'cron', hour='*', minute=5)
    scheduler.add_job(achievement_manager.check_achievements, 'cron', hour='*', minute=35)
   
    news_monitoring = NewsMonitoring(bot=bot, dp=dp)
    scheduler.add_job(news_monitoring.news_monitoring, 'cron', hour='*', minute=3)

    feeling_obj = Feeling(bot=bot, dp=dp)
    scheduler.add_job(feeling_obj.start_feeling_monitoring, 'cron', hour=7, minute=3)
    # scheduler.add_job(feeling_obj.start_feeling_monitoring, 'interval', seconds=10)


    scheduler.start()


async def main(bot: bot, dp: Dispatcher):
    task1 = asyncio.create_task(bot_task(bot=bot, dp=dp))
    task2 = asyncio.create_task(additional_tasks(bot=bot, dp=dp))
    await asyncio.gather(task1, task2)
    

if __name__ == "__main__":
    try:
        asyncio.run(main(bot=bot, dp=dp))
    except asyncio.exceptions.CancelledError:
        pass
