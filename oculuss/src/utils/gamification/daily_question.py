"""
Будет присылать каждому пользователю рандомный тест на знание БАДов
"""
import aiogram
from aiogram import types, F, Router
from secrets import choice

from utils.db.user import get_access_users

class Poll():
    def __init__(self, bot: aiogram.Bot, dp: aiogram.Dispatcher):
        self.bot = bot
        self.dp = dp

    async def select_random_poll(self) -> dict:
        questions = [
            {
                'question': 'Тормозной нейромедиатор',
                'options': ['GABA', 'GAMMA E', 'Таурин'],
                'correct_option': 0
            },
            {
                'question': 'Мощную антиоксидантная защита',
                'options': ['L-ОптиЦинк', 'Витамин D', 'GAMMA E'],
                'correct_option': 2
            }   
            ] 
        return choice(questions)         
    async def send_poll_for_everyone(self):
        poll_list = []

        for i in await get_access_users():
            
            q: dict = await self.select_random_poll()
            poll = await self.bot.send_poll(
                chat_id=i.user_id,
                question=q['question'],
                options=q['options'],
                correct_option_id=q['correct_option'],
                type='quiz',
                is_anonymous=False)
            poll_list.append(int(poll.poll.id))
            print(poll_list)

            @self.dp.poll_answer(F.poll_id.in_(poll_list))
            async def handle_poll_answer(poll_answer: types.PollAnswer):
                # print(poll_answer)
                print(f"Пользователь {poll_answer.user.id} ответил на опрос: {poll_answer.option_ids}")