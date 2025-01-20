from src.utils import create_table
import pandas as pd
from src.ai_generation import generate_statistics_request
from aiogram.types import Message


EXCEL_FILE_STATISTICS = "data/statistics.xlsx"

create_table(EXCEL_FILE_STATISTICS, ["ID", "answers", "score"])


def update_statistics_data(user_id: int, score: int):
    df = pd.read_excel(EXCEL_FILE_STATISTICS)
    user_index = df[df["ID"] == user_id].index

    if user_index.empty:
        raise ValueError("Пользователь не найден.")

    df.loc[user_index, "answers"] += 1
    df.loc[user_index, "score"] += score

    df.to_excel(EXCEL_FILE_STATISTICS, index=False)


def add_ID_to_statistics(user_id: int):
    df = pd.read_excel(EXCEL_FILE_STATISTICS)
    new_row = pd.DataFrame([{"ID": user_id, "answers": 0, "score": 0}])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_excel(EXCEL_FILE_STATISTICS, index=False)


async def generate_statistics(message: Message):
    df = pd.read_excel(EXCEL_FILE_STATISTICS)

    user_id = message.from_user.id
    user_data = df[df["ID"] == user_id]

    if user_data.empty:
        raise ValueError("Пользователь не найден.")

    data = {"completed_surveys_count": user_data["answers"], "total_score": user_data["score"]}

    await message.answer(await generate_statistics_request(data, user_id))
