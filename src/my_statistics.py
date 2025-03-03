import pandas as pd
import time
import asyncio

from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from src.utils import create_table
from src.ai_generation import generate_statistics_request
from src.workout_survey import clean_answers_set, EXCEL_FILE_STATISTICS
from src.utils import update_message_with_quotes

scheduler = AsyncIOScheduler()
localtime_offset = time.localtime().tm_gmtoff // 3600

create_table(EXCEL_FILE_STATISTICS, ["ID", "answers", "score"])


async def daily_updating_of_set():
    clean_answers_set()


class StatisticsState(StatesGroup):
    creating_statistics = State()


scheduler.add_job(
        daily_updating_of_set,
        CronTrigger(hour=(21+localtime_offset) % 24, minute=0)
)


def add_ID_to_statistics(user_id: int):
    df = pd.read_excel(EXCEL_FILE_STATISTICS)
    new_row = pd.DataFrame([{"ID": user_id, "answers": 0, "score": 0}])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_excel(EXCEL_FILE_STATISTICS, index=False)


async def generate_statistics(message: Message, state: FSMContext):
    df = pd.read_excel(EXCEL_FILE_STATISTICS)
    await state.set_state(StatisticsState.creating_statistics)
    sent_message = await message.answer("Расчет статистики... ⚙️")

    stop_event = asyncio.Event()
    quote_task = asyncio.create_task(update_message_with_quotes(sent_message, stop_event, "Расчет статистики..."))

    user_id = message.from_user.id
    user_data = df[df["ID"] == user_id]

    if user_data.empty:
        raise ValueError("Пользователь не найден.")

    data = {"completed_surveys_count": user_data["answers"].values[0], "total_score": user_data["score"].values[0]}
    
    answer = await generate_statistics_request(data, user_id)

    stop_event.set()
    await quote_task

    await sent_message.delete()
    await message.answer(answer)

    await state.clear()


async def on_startup_survey_after_training():
    scheduler.start()