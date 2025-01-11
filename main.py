import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from src.registration import *
from src.utils import get_token

'''
    Загрузка токена бота из файла .env
    В файле .env:
    BOT_TOKEN = ...
'''
TOKEN = get_token()

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

async def cmd_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_name = check_user_registered(user_id)
    if user_name:
        await message.answer(f"С возвращением, {user_name}!")
    else:
        await message.answer("Добро пожаловать! Давайте начнем регистрацию. Как вас зовут?")
        await state.set_state(Registration.waiting_for_name)

dp.message.register(cmd_start, CommandStart())
dp.message.register(process_name, Registration.waiting_for_name)
dp.message.register(process_height, Registration.waiting_for_height)
dp.message.register(process_weight, Registration.waiting_for_weight)

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    print("Bot is running")
    asyncio.run(main())
