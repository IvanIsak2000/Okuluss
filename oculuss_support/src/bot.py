import asyncio
from aiogram import Bot, Dispatcher
from aiogram import types
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from utils.config import BOT_KEY


from utils.logging.logger import logger
from utils.db.models import init_db
from utils.access.access_monitoring import user_access_is_active
from middlewares.user_ban import CheckUserWasBannedMiddleware

bot = Bot(token=BOT_KEY)
dp = Dispatcher()


async def main(bot: Bot, dp: Dispatcher):
    try:
        await init_db()
        from utils.logging.send_alert import send_alert
        from handlers import main_handler
        from handlers import _callbacks
        from handlers import buy_callbacks
        from handlers import send_review

        dp.include_routers(
            main_handler.router,
            _callbacks.router,
            buy_callbacks.router,
            send_review.router)
        dp.message.middleware(CheckUserWasBannedMiddleware())
        
        commands = [
            types.BotCommand(
                command="/menu", description="Меню"),
            # types.BotCommand(
            #     command="/access", description="Управление доступом"),
            # types.BotCommand(  
            #     command='/feedback', description='Обратная связь')
        ]
        
        await bot.set_my_commands(commands=commands)
        logger.info('✅ Бот запущен')
        await send_alert(alert_text='✅ Бот запущен', level='info')
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    except Exception as e:
        await send_alert(str(e), level='error')
    finally:
        await send_alert('❌ Бот отключён', level='info')
        logger.info('Bot closed')
    

async def additional_tasks(bot: Bot):
    scheduler = AsyncIOScheduler()
    # scheduler.add_job(user_access_is_active, 'interval', seconds=600, args=[bot])
    # scheduler.add_job(user_access_is_active, 'interval', minutes=10, args=[bot])
    scheduler.add_job(user_access_is_active, 'cron', day='*', hour=12, minute=0, args=[bot])
    scheduler.add_job(user_access_is_active, 'cron', day='*', hour=0, minute=0, args=[bot])
    scheduler.start()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    tasks = [
        loop.create_task(main(bot=bot, dp=dp)),
        loop.create_task(additional_tasks(bot=bot))
    ]
    loop.run_until_complete(asyncio.gather(*tasks))
