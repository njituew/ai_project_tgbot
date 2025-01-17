from aiogram import types
from src.registration import EXCEL_FILE
import pandas as pd


def get_info(user_id: str) -> dict:
    df = pd.read_excel(EXCEL_FILE)
    df["ID"] = df["ID"].astype(str).str.strip()
    user_id = str(user_id).strip()

    # Фильтруем строку по user_id
    user_data = df[df["ID"] == user_id]

    # Убираем колонку ID, преобразуем в словарь
    return user_data.drop(columns=["ID"]).iloc[0].to_dict()


async def show_profile_info(message: types.Message):
    user_id = message.from_user.id
    
    user_info = get_info(user_id)
    
    await message.answer(
        "Ваш профиль:\n\n"
        f"Имя: {user_info['Name']}\n"
        f"Пол: {user_info['Gender']}\n"
        f"Возраст: {user_info['Age']}\n"
        f"Рост: {user_info['Height']}\n"
        f"Вес: {user_info['Weight']}\n"
        f"Индекс массы тела: {user_info['BMI']}"
    )