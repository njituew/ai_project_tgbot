import os
from dotenv import load_dotenv
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import CommandStart
import pandas as pd

# Загрузка переменных окружения из .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Проверка токена
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN отсутствует в файле .env")

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Определение состояния для регистрации
class Registration(StatesGroup):
    waiting_for_name = State()
    waiting_for_height = State()
    waiting_for_weight = State()

# Путь к файлу Excel
EXCEL_FILE = "data/users.xlsx"

# Убедимся, что файл Excel существует или создадим его
if not os.path.exists(EXCEL_FILE):
    os.makedirs(os.path.dirname(EXCEL_FILE), exist_ok=True)
    df = pd.DataFrame(columns=["ID", "Name", "Height", "Weight"])
    df.to_excel(EXCEL_FILE, index=False, engine="openpyxl")

# Команда /start
@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await message.answer("Добро пожаловать! Давайте начнем регистрацию. Как вас зовут?")
    await state.set_state(Registration.waiting_for_name)

# Обработка имени
@dp.message(Registration.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Отлично! Укажите ваш рост в сантиметрах.")
    await state.set_state(Registration.waiting_for_height)

# Обработка роста
@dp.message(Registration.waiting_for_height)
async def process_height(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, укажите рост числом.")
        return

    await state.update_data(height=int(message.text))
    await message.answer("Хорошо! Теперь введите ваш вес в килограммах.")
    await state.set_state(Registration.waiting_for_weight)

# Обработка веса
@dp.message(Registration.waiting_for_weight)
async def process_weight(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, укажите вес числом.")
        return

    await state.update_data(weight=int(message.text))
    user_data = await state.get_data()

    # Сохранение данных в Excel
    df = pd.read_excel(EXCEL_FILE, engine="openpyxl")
    new_data = pd.DataFrame([{
        "ID": message.from_user.id,
        "Name": user_data["name"],
        "Height": user_data["height"],
        "Weight": user_data["weight"]
    }])
    df = pd.concat([df, new_data], ignore_index=True)
    df.to_excel(EXCEL_FILE, index=False, engine="openpyxl")

    await message.answer("Спасибо за регистрацию! Ваши данные сохранены.")
    await state.clear()

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
