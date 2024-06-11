import aiogram
from aiogram import types
from hashlib import blake2b
from pydantic import parse_obj_as
from datetime import datetime
import random
import asyncio


from utils.logging.logger import logger
from utils.db.user import (
    get_access_users, 
    is_access_user, 
    is_banned_user, 
    update_user_experience
)
from utils.db.custom_supplementation import (
    get_user_custom_supplementation, 
    remove_ended_user_supplementation,
    get_user_custom_supplementation_by_hash,
    get_user_custom_supplementation_by_name,
    minus_accept_count
)
from kb.supplementation_keyboard import keyboard_for_accepting_supplements
from utils.logging.logger import logger
from utils.db.accept_record import (
    add_open_record_of_taking, 
    update_accept_record,
    get_record_info_by_hash
)
from utils.texts import MY_TIMEZONE
import kb.supplementation_keyboard


class Sender():
    """Generate a hash record and send new accept"""

    def __init__(self, bot: aiogram.Bot):
        self.bot = bot

    async def generate_record_hash(self) -> str:
        record_hash: str = blake2b(digest_size=10)
        record_hash.update(str(random.randint(0, 10000)).encode('utf-8'))
        return record_hash.hexdigest() 

    async def send_hour_taking(
            self,
            target,
            current_hour: str,
            user_supplementation: list) -> bool:
        """
        Сначала создаёт запись для в бд с пустым accept(принял), 
        потом отправлет юзер сообщение с клавиатурой, в которой встроен hash

        Возвращает True если успешно отправлено, иначе False
        """

        try:
            record_hash: str = await self.generate_record_hash()
            
            names = []
            for i in user_supplementation:
                names.append(i.name)

            text = '''👁️ Время принять: \n\n'''
            msg = await self.bot.send_message(
                chat_id=target.user_id,
                text=text+'\n'.join([f'{i.name} {i.dose}' for i in user_supplementation if i.is_active])+'\n\nОчков опыта +1🌀',
                reply_markup=await keyboard_for_accepting_supplements(
                    record_hash=record_hash)
                )

            await add_open_record_of_taking(
                record_hash=record_hash,
                user_id=int(target.user_id),
                supplementation_names=names,
                supplementation_dict={
                    'data': str(user_supplementation)
                },
                open_time=datetime.now(),
                message_id=msg.message_id,
                record_time=current_hour
            )
            return True
                                
        except Exception as e:
            if 'bot was blocked by the user' in str(e):
                logger.error(f' {target.user_id} заблокировал бота')
                return False
                                                
            await logger.critical(message=str(e))
            return False

    async def user_supplementation_is_low(
        self,
        target,
        supplementation_hash: str
    ):
        """Отправка пользователя уведомления что БАД скоро закончится"""
        supplementation = await get_user_custom_supplementation_by_hash(
            user_id=target.user_id,
            supplementation_hash=supplementation_hash
        )
        await self.bot.send_message(
            chat_id=target.user_id,
            text=f'❗Твоего БАДа {supplementation.name} хватит ещё на {int(supplementation.count / supplementation.dose)} порций/ии, закупи заранее'
        )

    async def user_supplementation_is_end(
        self,
        target,
        supplementation_hash: str
    ):
        """Send one message to user than your supplementation is end
        """
        supplementation = await get_user_custom_supplementation_by_hash(
                user_id=target.user_id,
                supplementation_hash=supplementation_hash
        )

        await self.bot.send_message(
            chat_id=target.user_id,
            text=f'🚫 Ваш БАД {supplementation.name} закончился!'
        )

        await remove_ended_user_supplementation(
            user_id=target.user_id,
            supplementation_hash=supplementation_hash
        )


class Monitor():
    def __init__(self, bot: aiogram.Bot, dp: aiogram.Dispatcher) -> None:
        self.bot = bot
        self.dp = dp


    async def time_is_available(self, open_time: str):
        print(f'open_time: {open_time}')    


    async def time_was_passed(self, callback: types.CallbackQuery):
        await self.bot.delete_message(
            chat_id=callback.message.chat.id,
        )

        await self.bot.send_message(
            chat_id=callback.message.chat.id,
            text='Клавиатура недоступна!')
                

    async def user_monitoring(self):
        """Следит за приемами пользовательских БАДов"""
        await logger.info("Напоминатель запущен...")

        targets: list = await get_access_users()
        prepare_supplementation: list = []
        n: int = 0
        sender = Sender(bot=self.bot)

        for self.target in targets:
            await asyncio.sleep(0.1)
            if not await is_banned_user(user_id=self.target.user_id):
                if await is_access_user(user_id=self.target.user_id):
                    user_supplementation_data = await get_user_custom_supplementation(
                        user_id=self.target.user_id
                    )
                    for i in user_supplementation_data:
                        if i.is_active:
                            now_hour = datetime.now().astimezone(tz=MY_TIMEZONE).strftime("%H")
                            if now_hour == i.time.split(":")[0]:
                                count = i.count
                                dose = i.dose
                                if count < dose:
                                    await sender.user_supplementation_is_end(
                                        target=self.target,
                                        supplementation_hash=i.supplementation_hash
                                    )
                                elif count < dose * 3:
                                    await sender.user_supplementation_is_low(
                                        target=self.target,
                                        supplementation_hash=i.supplementation_hash)
                                    prepare_supplementation.append(i)
                                else:
                                    prepare_supplementation.append(i)

                    if prepare_supplementation != []:
                        result = await sender.send_hour_taking(
                            target=self.target,
                            current_hour=now_hour,
                            user_supplementation=prepare_supplementation
                        )
                        if result:
                            n += 1
                        else:
                            pass

                        prepare_supplementation.clear()


                    @self.dp.callback_query(
                        lambda d: d.data.startswith('record_of_accept'))
                    async def accept_all_supplements(
                            callback: types.CallbackQuery) -> None:
                        # try:
                        await logger.info(f'Добавки приняты, hash: {callback.data.split(":")[1]}')

                        await callback.answer(
                            "✅ Добавки приняты",
                            show_alert=False
                        )
                        await update_accept_record(
                            record_hash=callback.data.split(':')[1],
                            user_id=callback.from_user.id,
                            accept=True
                        )
                        await update_user_experience(
                            user_id=callback.from_user.id,
                            count=1
                        )

                        await callback.message.delete()

                        await minus_accept_count(
                            user_id=callback.from_user.id,
                            record_hash=callback.data.split(':')[1]
                        )


                    @self.dp.callback_query(
                        lambda d: d.data.startswith('record_of_pass:'))
                    async def pass_all_supplements(
                            callback: types.CallbackQuery) -> None:
                        try:
                            await logger.info(f'Добавки пропущены, hash: {callback.data.split(":")[1]}')
                            await callback.answer(
                                "➡ Приём пропущен",
                                show_alert=False
                            )

                            await update_accept_record(
                                record_hash=callback.data.split(':')[1],
                                user_id=callback.from_user.id,
                                accept=False
                            )
                            await callback.message.delete()
                        except Exception as e:
                            if 'message to delete not found' in str(e):
                                await logger.error(
                                    f'Ошибка удаления сообщения, возможно пользователь нажал две кнопки')
                            raise Exception(e)                                          

        await logger.info(f"Напоминатель закончен. Результат: количество отправленных приёмов = {n}/{len(targets)}")

