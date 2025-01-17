from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import pandas as pd
from src.survey_for_training import check_training, EXCEL_FILE_TRAINING, EXCEL_FILE_DIET, create_new_training_keyboard


def create_my_training_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Создать новую тренировку 🆕", callback_data="my_plan_new")],
        [InlineKeyboardButton(text="Удалить свою тренировку 🗑️", callback_data="my_plan_remove")],
    ])


def get_plan(user_id: str):
    # Преобразуем user_id в строку и удаляем лишние пробелы
    user_id = str(user_id).strip()

    # Загружаем таблицы
    trainings_df = pd.read_excel(EXCEL_FILE_TRAINING)
    diets_df = pd.read_excel(EXCEL_FILE_DIET)

    # Приводим колонку ID к строковому типу и удаляем пробелы
    trainings_df["ID"] = trainings_df["ID"].astype(str).str.strip()
    diets_df["ID"] = diets_df["ID"].astype(str).str.strip()

    # Получаем строки для указанного пользователя
    training_plan = trainings_df[trainings_df["ID"] == user_id]
    diet_plan = diets_df[diets_df["ID"] == user_id]

    # Инициализируем результат
    plan_text = ""

    # Дни недели
    days_of_week = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    day_names = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]

    # Форматируем тренировочный план
    plan_text += "📋 План тренировок:\n\n"
    for day, day_name in zip(days_of_week, day_names):
        exercises = training_plan.iloc[0].get(day)
        if pd.notna(exercises):
            plan_text += f"{day_name}:\n{exercises}\n\n"

    # Форматируем диетический план
    plan_text += "🍽️ Диета:\n\n"
    for day, day_name in zip(days_of_week, day_names):
        meals = diet_plan.iloc[0].get(day)
        if pd.notna(meals):
            plan_text += f"{day_name}:\n{meals}\n\n"

    return plan_text.strip()


async def show_plan(message: types.Message):
    user_id = message.from_user.id
    
    if check_training(user_id):
        plan = get_plan(user_id)
        await message.answer(
            f"Ваш индивидуальный план:\n\n{plan}",
            reply_markup=create_my_training_keyboard())
        
    else:
        await message.answer(
            "У вас нет плана тренировок. Хотите его создать?",
            reply_markup=create_new_training_keyboard()
        )
