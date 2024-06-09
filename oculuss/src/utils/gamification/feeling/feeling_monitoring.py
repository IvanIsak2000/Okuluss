import aiogram
from aiogram import types, F, Router
from secrets import choice
import asyncio

from utils.db.user import get_access_users
from kb.feeling_keyboard import make_feeling_keyboard

class Feeling():
    def __init__(self, bot: aiogram.Bot, dp: aiogram.Dispatcher):
        self.bot = bot
        self.dp = dp
    async def get_random_text_to_feeling(self):
        text = [
            'Доброе утро 🌻\nХочу узнать как твоё самочувствие после БАДов?',
            'Good Morning 🌞\nРасскажи как себя чувствуешь?',
            '🔆 Привет\nНасколько изменилось твоё состояние после вчерашних приёмов?'
        ]
        return choice(text)
                

    async def start_feeling_monitoring(self):
        # users = await get_access_users()
        # добавить проверку только если у пользвоателя есть завершенный прием бада вчера
        users = [5261974343]
        for user in users:
            await asyncio.sleep(0.1)
            await self.bot.send_message(
                chat_id=user,
                text=await self.get_random_text_to_feeling(),
                reply_markup=await make_feeling_keyboard()
            )


            @self.dp.callback_query(
                lambda d: d.data.startswith('feeling_rate:'))
            async def callback_feeling_rate(callback: types.CallbackQuery):
                feeling_number = callback.data.split(':')[1]
                print(f'feeling_number: {feeling_number}')
                await self.bot.delete_message(
                    chat_id=callback.message.chat.id,
                    message_id=callback.message.message_id
                )
                await callback.answer(
                    text='✅ Принял',
                    show_alert=True
                    
                )