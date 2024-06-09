from logtail import LogtailHandler
import logging
import requests
from utils.config import LOG_TOKEN
from utils.config import BOT_KEY
# from utils.db.settings import get_main_moderator_id


class MyLogger():
    def __init__(self) -> None:
        handler = LogtailHandler(source_token=LOG_TOKEN)
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        logger.handlers = []
        logger.addHandler(handler)
        self.logger = logger

    async def send_alert_to_main_moderator(self, text: str) -> None:
        url = f'https://api.telegram.org/bot{BOT_KEY}/sendMessage'
        params = {
            'chat_id': 5261974343,
            'text': f'СООБЩЕНИЕ ОТ БОТА:\n{text}'}
        requests.post(url, params=params)

    async def info(self, message: str, send_alert: bool = False, extra: dict = None) -> None:
        if send_alert:
            self.logger.info(msg=message, extra=extra)
            await self.send_alert_to_main_moderator(
                text=message)
        else:
            self.logger.info(message)

    async def error(self, message: str) -> None:
        self.logger.error(message)
        await self.send_alert_to_main_moderator(
            text=message
        )
        # self.logger.error(message)
        # await self.send_alert_to_main_moderator(
        #     text=message)

    async def critical(self, message: str, extra: dict = None) -> None:
        self.logger.critical(message, extra=extra)
        await self.send_alert_to_main_moderator(
            text=f'{message}\nEXtra:{extra}')


logger = MyLogger()
