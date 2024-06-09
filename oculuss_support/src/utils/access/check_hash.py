import requests
from decimal import Decimal

from utils.logging.logger import logger
from utils.db.models import (
    add_utilized_hash,
    hash_was_used)

SERVER_ERROR = {
    'status': False,
    'error_message': '🔧 Сервер не отвечает, пожалуйста, попробуйте попозже'
}

ERR_HASH_WAS_USED = {
    'status': False,
    'error_message': '❌ Такой хэш уже был использован!'
}

ERR_HASH_WAS_NOT_FIND = {
    'status': False,
    'error_message': '❌ Хэш не найден, проверьте правильность хэша!'
}

SUCCESS = {
    'status': True,
    'error_message': ''
}


class CheckHash():
    """Класс проверки транзакции по `tronscan.org` API и выдает dict, в котором status==True\n
    Параметры:\n
    - user_id: int - id пользователя
    - hash: str - хэш, отправленный пользователем
    """
    def __init__(self) -> None:
        pass

    async def user_hash_existed(self) -> dict[bool, str]:
        """Функция проверки что такая транзакция по хэшу была"""
        try:
            text_uint = float(
                self.response.json()['trc20TransferInfo'][0]['amount_str'])
            logger.info(f"Сумма транзакции: {text_uint} от пользователя {self.user_id}")
            if text_uint >= 3000000:
                return SUCCESS
            else:
                return {
                    'status': False,
                    'error_message': f"Сумма транзакции не правильна!"
                }
        except KeyError:
            return ERR_HASH_WAS_NOT_FIND
        except Exception as e:
            logger.critical(e)
            return {
                'status': False,
                'error_message': str(e)
            }

    async def check_hash(
            self,
            user_id: int,
            username: str,
            hash: str) -> dict[bool, str]:
        """Главная функция класса"""

        self.user_id = user_id
        self.hash = hash
        logger.info(
            f'Начало проверки транзакции: user={self.user_id}, hash={self.hash}...')
        url = f'https://apilist.tronscanapi.com/api/transaction-info?hash={self.hash}'
        self.response = requests.get(url)

        if not await hash_was_used(hash=self.hash):
            if self.response.status_code == 200:
                return await self.user_hash_existed()
            else:
                return SERVER_ERROR
        else:
            return ERR_HASH_WAS_USED
