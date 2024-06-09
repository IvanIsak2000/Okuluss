import requests
from utils.config import BOT_KEY

from utils.logging.logger import logger
from utils.db.models import get_main_moderator_id


async def send_alert(alert_text: str, level: str) -> None:
    logger.info(f'Главный модер: {await get_main_moderator_id()}')
    url = f'https://api.telegram.org/bot{BOT_KEY}/sendMessage'
    params = {
        'chat_id': await get_main_moderator_id(),
        'text': f'ALERT FROM BOT:\n{alert_text}'
    }
    response = requests.post(url, params=params)
    
    if response.status_code == 200:
        if level == 'info':
            logger.info(f'Сообщение ({alert_text}) отправлено')
        if level == 'error':
            logger.error(f'Сообщение ({alert_text}) отправлено')
    else:
        logger.critical(f'Отправка сообщения ({alert_text}) прервана')
