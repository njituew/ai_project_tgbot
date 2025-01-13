import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
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

# Команда /menu
async def cmd_menu(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Создать тренировку 🏋️‍♂️")],
            [KeyboardButton(text="Упражнения 📚")],
            [KeyboardButton(text="Моя статистика 📈")]
        ],
        resize_keyboard=True
    )
    await message.answer("Меню открыто.", reply_markup=keyboard)

# Обработчики для кнопок клавиатуры
async def handle_button_click(message: types.Message):
    text = message.text
    if text in ("Создать тренировку", "Упражнения", "Моя статистика"):
        await message.answer(f"{text}")
    else:
        await message.answer("Неизвестная команда.")

# Регистрация ручек
dp.message.register(cmd_start, CommandStart())  # команда /start
dp.message.register(cmd_menu, Command("menu"))  # команда /menu
dp.message.register(handle_button_click)
dp.message.register(process_name, Registration.waiting_for_name)
dp.message.register(process_age, Registration.waiting_for_age)
dp.message.register(process_height, Registration.waiting_for_height)
dp.message.register(process_weight, Registration.waiting_for_weight)

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    print("Bot is running")
    asyncio.run(main())
