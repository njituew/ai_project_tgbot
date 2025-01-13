import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from src.registration import *
from src.utils import get_token
from src.default_commands import cmd_menu, cmd_start, handle_button_click

'''
    Загрузка токена бота из файла .env
    В файле .env:
    BOT_TOKEN = ...
'''
TOKEN = get_token()

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Регистрация ручек
dp.message.register(cmd_start, CommandStart())  # команда /start
dp.message.register(cmd_menu, Command("menu"))  # команда /menu
dp.message.register(process_name, RegistrationStates.waiting_for_name)
dp.message.register(process_age, RegistrationStates.waiting_for_age)
dp.message.register(process_height, RegistrationStates.waiting_for_height)
dp.message.register(process_weight, RegistrationStates.waiting_for_weight)
dp.message.register(handle_button_click)

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    print("Bot is running")
    asyncio.run(main())
