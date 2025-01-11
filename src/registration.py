import os
import pandas as pd
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# Путь к файлу Excel
EXCEL_FILE = "data/users.xlsx"

# Убедимся, что файл Excel существует или создадим его
if not os.path.exists(EXCEL_FILE):
    os.makedirs(os.path.dirname(EXCEL_FILE), exist_ok=True)
    df = pd.DataFrame(columns=["ID", "Name", "Height", "Weight"])
    df.to_excel(EXCEL_FILE, index=False, engine="openpyxl")

def check_user_registered(user_id):
    df = pd.read_excel(EXCEL_FILE, engine="openpyxl")
    user = df[df["ID"] == user_id]
    if not user.empty:
        return user.iloc[0]["Name"]
    return None

# Определение состояния для регистрации
class Registration(StatesGroup):
    waiting_for_name = State()
    waiting_for_height = State()
    waiting_for_weight = State()

async def cmd_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_name = check_user_registered(user_id)
    if user_name:
        await message.answer(f"С возвращением, {user_name}!")
    else:
        await message.answer("Добро пожаловать! Давайте начнем регистрацию. Как вас зовут?")
        await state.set_state(Registration.waiting_for_name)

async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Отлично! Укажите ваш рост в сантиметрах.")
    await state.set_state(Registration.waiting_for_height)

async def process_height(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, укажите рост числом.")
        return

    await state.update_data(height=int(message.text))
    await message.answer("Хорошо! Теперь введите ваш вес в килограммах.")
    await state.set_state(Registration.waiting_for_weight)

async def process_weight(message: types.Message, state: FSMContext):
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
