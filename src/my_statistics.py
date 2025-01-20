from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from src.utils import create_table
from src.ai_generation import generate_statistics_request
from src.workout_survey import clean_answers_set, EXCEL_FILE_STATISTICS
import pandas as pd
import time


scheduler = AsyncIOScheduler()
localtime_offset = time.localtime().tm_gmtoff // 3600

create_table(EXCEL_FILE_STATISTICS, ["ID", "answers", "score"])


async def daily_updating_of_set():
    clean_answers_set()


scheduler.add_job(
        daily_updating_of_set,
        CronTrigger(hour=(21+localtime_offset) % 24, minute=0)
    )


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


async def on_startup_survey_after_training():
    scheduler.start()