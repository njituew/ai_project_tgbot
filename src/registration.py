from src.utils import create_table, calculate_bmi
import pandas as pd
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


# Путь к файлу Excel
EXCEL_FILE = "data/users.xlsx"


# Убедимся, что файл Excel существует или создадим его
create_table(EXCEL_FILE)


def check_registered(user_id: str) -> str | None:
    df = pd.read_excel(EXCEL_FILE)  #, engine="openpyxl"
    user = df[df["ID"] == user_id]
    if not user.empty:
        return user.iloc[0]["Name"]
    return None


# Состояния при регистрации
class RegistrationStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_age = State()
    waiting_for_height = State()
    waiting_for_weight = State()


async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Супер! Напишите, пожалуйста, сколько вам полных лет.")
    await state.set_state(RegistrationStates.waiting_for_age)


async def process_age(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, укажите возраст числом.")
        return

    await state.update_data(age=int(message.text))
    await message.answer("Отлично! Укажите ваш рост в сантиметрах.")
    await state.set_state(RegistrationStates.waiting_for_height)


async def process_height(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, укажите рост числом.")
        return

    await state.update_data(height=int(message.text))
    await message.answer("Хорошо! Теперь введите ваш вес в килограммах.")
    await state.set_state(RegistrationStates.waiting_for_weight)


async def process_weight(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, укажите вес числом.")
        return

    await state.update_data(weight=int(message.text))
    user_data = await state.get_data()

    # Сохранение данных в Excel
    df = pd.read_excel(EXCEL_FILE)
    new_data = pd.DataFrame([{
        "ID": message.from_user.id,
        "Age": user_data["age"],
        "Name": user_data["name"],
        "Height": user_data["height"],
        "Weight": user_data["weight"],
        "BMI": str(calculate_bmi(int(user_data["height"]), int(user_data["weight"])))
    }])
    df = pd.concat([df, new_data], ignore_index=True)
    df.to_excel(EXCEL_FILE, index=False)

    await message.answer("Спасибо за регистрацию! Ваши данные сохранены.")
    await state.clear()
