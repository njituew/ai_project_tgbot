from src.utils import create_table, calculate_bmi
import pandas as pd
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import State, StatesGroup


# Путь к файлу Excel
EXCEL_FILE = "data/users.xlsx"


# Создание таблицы
create_table(EXCEL_FILE, ["ID", "Name", "Gender", "Age", "Height", "Weight", "BMI"])


def check_registered(user_id: str) -> str | None:
    df = pd.read_excel(EXCEL_FILE)  #, engine="openpyxl"
    user = df[df["ID"] == user_id]
    if not user.empty:
        return user.iloc[0]["Name"]
    return None


# Состояния при регистрации
class RegistrationStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_gender = State()
    waiting_for_age = State()
    waiting_for_height = State()
    waiting_for_weight = State()


def create_new_training_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Мужской ♂️", callback_data="gender_male"),
         InlineKeyboardButton(text="Женский ♀️", callback_data="gender_female")],
    ])


async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(
        f"Рады познакомиться, {message.text}! Пожалуйста, укажите ваш пол",
        reply_markup=create_new_training_keyboard())
    await state.set_state(RegistrationStates.waiting_for_gender)


async def process_gender(callback_query: types.CallbackQuery, state: FSMContext):
    gender_mapping = {
        "gender_male": "Мужской",
        "gender_female": "Женский",
    }
    await state.update_data(gender=gender_mapping[callback_query.data])
    await callback_query.message.edit_text("Супер! Напишите, пожалуйста, сколько вам полных лет.")
    await state.set_state(RegistrationStates.waiting_for_age)


async def process_age(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, укажите возраст числом.")
        return
    elif int(message.text) < 1 or int(message.text) > 150:
        await message.answer("Пожалуйста, укажите свой настоящий возраст.")
        return

    await state.update_data(age=int(message.text))
    await message.answer("Отлично! Укажите ваш рост в сантиметрах.")
    await state.set_state(RegistrationStates.waiting_for_height)


async def process_height(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, укажите рост числом.")
        return
    elif int(message.text) < 100 or int(message.text) > 300:
        await message.answer("Пожалуйста, укажите свой настоящий рост.")
        return
    
    await state.update_data(height=int(message.text))
    await message.answer("Хорошо! Теперь введите ваш вес в килограммах.")
    await state.set_state(RegistrationStates.waiting_for_weight)


async def process_weight(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, укажите вес числом.")
        return
    elif int(message.text) < 1 or int(message.text) > 600:
        await message.answer("Пожалуйста, укажите свой настоящий вес.")
        return

    await state.update_data(weight=int(message.text))
    user_data = await state.get_data()

    # Сохранение данных в Excel
    df = pd.read_excel(EXCEL_FILE)
    new_data = pd.DataFrame([{
        "ID": message.from_user.id,
        "Name": user_data["name"],
        "Gender": user_data["gender"],
        "Age": user_data["age"],
        "Height": user_data["height"],
        "Weight": user_data["weight"],
        "BMI": str(calculate_bmi(int(user_data["height"]), int(user_data["weight"])))
    }])
    df = pd.concat([df, new_data], ignore_index=True)
    df.to_excel(EXCEL_FILE, index=False)

    await message.answer(
        """Спасибо за регистрацию! Ваши данные сохранены.\nЗадайте мне вопрос, связанный со спортом, или создайте свой индивидуальный план тренировок.\n\n/menu - открыть меню бота"""
    )
    await state.clear()