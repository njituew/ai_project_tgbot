from src.utils import create_trainings_table, create_diets_table, remove_user
import pandas as pd

from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram import types

from src.ai_generation import generate_schedule


# Путь к файлу Excel
EXCEL_FILE_TRAINING = "data/trainings.xlsx"
EXCEL_FILE_DIET = "data/diets.xlsx"


# Убедимся, что файл Excel существует или создадим его
create_trainings_table(EXCEL_FILE_TRAINING)
create_diets_table(EXCEL_FILE_DIET)


def check_training(user_id: str) -> bool:
    df = pd.read_excel(EXCEL_FILE_TRAINING)  #, engine="openpyxl"
    user = df[df["ID"] == user_id]
    if not user.empty:
        return True
    return False


# Состояния при опросе
class TrainingSurvey(StatesGroup):
    new_training = State()
    goal = State()  # Состояние для цели тренировок
    level = State()  # Состояние для уровня сложности
    location = State()  # Состояние для места тренировок


def create_new_training_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Создать новую тренировку 🆕", callback_data="yes")],
        [InlineKeyboardButton(text="Отмена ❌", callback_data="cancel")],
    ])


def create_goal_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Набор массы 💪", callback_data="goal_mass")],
        [InlineKeyboardButton(text="Похудение 🏃", callback_data="goal_loss")],
        [InlineKeyboardButton(text="Поддержание формы 🤸", callback_data="goal_maintenance")]
    ])


def create_level_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Новичок 🥉", callback_data="level_beginner")],
        [InlineKeyboardButton(text="Средний 🥈", callback_data="level_intermediate")],
        [InlineKeyboardButton(text="Профессионал 🥇", callback_data="level_pro")]
    ])


def create_location_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Дом 🏠", callback_data="location_home")],
        [InlineKeyboardButton(text="Тренажерный зал 🏋️", callback_data="location_gym")]
    ])


async def start_survey(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if check_training(user_id):
        await message.answer(
            "У вас уже есть тренировка. Создать новую?",
            reply_markup=create_new_training_keyboard()
        )
        await state.set_state(TrainingSurvey.new_training)
    else:
        await message.answer("Какова цель тренировок?", reply_markup=create_goal_keyboard())
        await state.set_state(TrainingSurvey.goal)


async def new_training(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == "yes":
        user_id = callback_query.from_user.id
        remove_user(EXCEL_FILE_TRAINING, user_id)
        remove_user(EXCEL_FILE_DIET, user_id)
        
        await callback_query.message.edit_text(
            "Какова цель тренировок?", reply_markup=create_goal_keyboard()
        )
        await state.set_state(TrainingSurvey.goal)
    else:
        await callback_query.message.edit_text("Создание тренировки отменено ❌")
        await state.clear()  # Завершаем FSM


async def set_goal(callback_query: types.CallbackQuery, state: FSMContext):
    goal_mapping = {
        "goal_mass": "Набор массы",
        "goal_loss": "Похудение",
        "goal_maintenance": "Поддержание формы"
    }
    selected_goal = goal_mapping[callback_query.data]
    await state.update_data(goal=selected_goal)
    await callback_query.message.edit_text(
        "Каков ваш уровень?", reply_markup=create_level_keyboard()
    )
    await state.set_state(TrainingSurvey.level)


async def set_level(callback_query: types.CallbackQuery, state: FSMContext):
    level_mapping = {
        "level_beginner": "Новичок",
        "level_intermediate": "Средний",
        "level_pro": "Профессионал"
    }
    selected_level = level_mapping[callback_query.data]
    await state.update_data(level=selected_level)
    await callback_query.message.edit_text(
        "Где будут проходить тренировки?", reply_markup=create_location_keyboard()
    )
    await state.set_state(TrainingSurvey.location)


async def set_location(callback_query: types.CallbackQuery, state: FSMContext):
    location_mapping = {
        "location_home": "Дом",
        "location_gym": "Тренировочный зал"
    }
    selected_location = location_mapping[callback_query.data]
    await state.update_data(location=selected_location)
    
    await callback_query.message.edit_text("Создание персонального плана тренировок... ⚙️")

    user_data = await state.get_data()
    training_json = generate_schedule(user_data)
    
    # Создание таблицы с тренировками
    df = pd.read_excel(EXCEL_FILE_TRAINING)
    training_data = pd.DataFrame([{
        "ID": callback_query.from_user.id,
        "monday": training_json["monday"]["workout"],
        "tuesday": training_json["tuesday"]["workout"],
        "wednesday": training_json["wednesday"]["workout"],
        "thursday": training_json["thursday"]["workout"],
        "friday": training_json["friday"]["workout"],
        "saturday": training_json["saturday"]["workout"],
        "sunday": training_json["sunday"]["workout"]
    }])
    df = pd.concat([df, training_data], ignore_index=True)
    df.to_excel(EXCEL_FILE_TRAINING, index=False)
    
    # Создание таблицы с диетой
    df = pd.read_excel(EXCEL_FILE_DIET)
    diet_data = pd.DataFrame([{
        "ID": callback_query.from_user.id,
        "monday": training_json["monday"]["diet"],
        "tuesday": training_json["tuesday"]["diet"],
        "wednesday": training_json["wednesday"]["diet"],
        "thursday": training_json["thursday"]["diet"],
        "friday": training_json["friday"]["diet"],
        "saturday": training_json["saturday"]["diet"],
        "sunday": training_json["sunday"]["diet"]
    }])
    df = pd.concat([df, diet_data], ignore_index=True)
    df.to_excel(EXCEL_FILE_DIET, index=False)
    
    await callback_query.message.answer("Ваша тренировка создана успешно! 👍")
    
    await state.clear()  # Завершаем FSM
    