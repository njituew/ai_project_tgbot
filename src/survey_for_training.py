import pandas as pd

from src.utils import create_table, remove_user
from src.reminders import remove_notifications
from src.ai_generation import generate_schedule

from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram import types


# Пути к таблицам
EXCEL_FILE_TRAINING = "data/trainings.xlsx"
EXCEL_FILE_DIET = "data/diets.xlsx"


# Созданиец таблиц
colums = ["ID", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
create_table(EXCEL_FILE_TRAINING, colums)   # тренировки
create_table(EXCEL_FILE_DIET, colums)       # диеты


def check_training(user_id: str) -> bool:
    df = pd.read_excel(EXCEL_FILE_TRAINING)
    user = df[df["ID"] == user_id]
    return not user.empty


class TrainingStates(StatesGroup):
    waiting_for_wishes = State()


def create_new_training_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Создать новую тренировку 🆕", callback_data="survey_training_new")],
        [InlineKeyboardButton(text="Отмена ❌", callback_data="survey_training_new_cancel")],
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


async def start_survey(message: types.Message): #, state: FSMContext):
    user_id = message.from_user.id
    if check_training(user_id):
        await message.answer(
            "У вас уже есть тренировка. Создать новую?",
            reply_markup=create_new_training_keyboard()
        )
    else:
        await message.answer("Какова цель тренировок?", reply_markup=create_goal_keyboard())


async def new_training(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    
    # Если мы пришли из my_plan.py
    if callback_query.data == "my_plan_new":
        await callback_query.message.edit_text("Ваш предыдущий индивидуалный план удалён.")
        remove_user(EXCEL_FILE_TRAINING, user_id)
        remove_user(EXCEL_FILE_DIET, user_id)
        await callback_query.message.answer(
            "Какова цель тренировок?", reply_markup=create_goal_keyboard()
        )
        
    # Если мы из "Создать тренировку" и нажали "ДА" или пришли из напоминаний
    elif callback_query.data == "survey_training_new" or callback_query.data == "reminders_new_training":
        remove_user(EXCEL_FILE_TRAINING, user_id)
        remove_user(EXCEL_FILE_DIET, user_id)
        
        await callback_query.message.edit_text(
            "Какова цель тренировок?", reply_markup=create_goal_keyboard()
        )
    
    # Если мы из "Создать тренировку" и нажали "НЕТ"
    else:   # survey_training_new_cancel
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


async def set_location(callback_query: types.CallbackQuery, state: FSMContext):
    location_mapping = {
        "location_home": "Дом",
        "location_gym": "Тренировочный зал"
    }
    selected_location = location_mapping[callback_query.data]
    await state.update_data(location=selected_location)
    await callback_query.message.edit_text(
        f"Напишите, пожалуйста, ваши пожелания к тренировкам и питанию, "
        f"или другую дополнительную информацию, которую нам стоит учесть"
    )
    await state.set_state(TrainingStates.waiting_for_wishes)


async def set_wishes(message: types.Message, state: FSMContext):
    await state.update_data(wishes=message.text)
    await message.answer("Создание персонального плана тренировок... ⚙️")

    user_data = await state.get_data()
    
    # Получение информации о пользователе
    user_id = message.from_user.id
    df = pd.read_excel("data/users.xlsx")
    user_info = df[df["ID"] == user_id][["Gender", "Age", "Height", "Weight", "BMI"]].iloc[0].to_dict()
    
    # Генерация плана тренировок
    training_json = generate_schedule(user_data, user_info)
    
    # Создание таблицы с тренировками
    df = pd.read_excel(EXCEL_FILE_TRAINING)
    training_data = pd.DataFrame([{
        "ID": message.from_user.id,
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
        "ID": message.from_user.id,
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
    
    await message.answer(
        f"Ваша тренировка создана успешно! 👍\n\n"
        f"/my_plan - посмотреть план тренировок\n"
        f"/reminder - управление напоминаниями"
    )
    
    await state.clear()  # Завершаем FSM


async def remove_training(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    remove_user(EXCEL_FILE_TRAINING, user_id)
    remove_user(EXCEL_FILE_DIET, user_id)
    remove_notifications(user_id)
    await callback_query.message.edit_text("Ваш индивидуалный план удалён.")
