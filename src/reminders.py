from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.base import JobLookupError
import pandas as pd
import datetime
from src.survey_for_training import EXCEL_FILE_TRAINING, EXCEL_FILE_DIET


scheduler = AsyncIOScheduler()
hours = (8, 18, 11)


def plan_for_today(user_id: int):
    # Чтение файла
    trainings_df = pd.read_excel(EXCEL_FILE_TRAINING)
    diets_df = pd.read_excel(EXCEL_FILE_DIET)

    # Строки с нужным ID
    trainings_info = trainings_df[trainings_df["ID"] == user_id]
    diets_info = diets_df[diets_df["ID"] == user_id]

    # План на сегодня
    trainings_text = trainings_info.iloc[0].get(datetime.datetime.today().strftime("%A").lower())
    diets_text = diets_info.iloc[0].get(datetime.datetime.today().strftime("%A").lower())

    # Создаём сообщение
    content = ""
    if pd.notna(trainings_text):
        content = "🏃‍♂️ Сегодня у вас запланирована тренировка:\n\n"
        content += trainings_text
    else:
        content = "Сегодня у вас не запланирована тренировка 🥱"
    
    content += "\n\n🍽 Рекомендации по питанию:\n\n"
    content += diets_text
    
    return content


# Создание клавиатуры для выбора действия
def create_reminders_keyboard():
    buttons = [
        [InlineKeyboardButton(text="Включить ✅", callback_data="turn_on_reminder")],
        [InlineKeyboardButton(text="Отключить ❌", callback_data="turn_off_reminder")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def show_reminders_menu(message: types.Message):
    user_id = message.from_user.id
    diets_df = pd.read_excel(EXCEL_FILE_DIET)

    if diets_df[diets_df["ID"] == user_id].empty:
        await message.answer(
            "Нельзя включить напоминания, так как на данный момент у вас нет плана тренировок.\n\n"
            "Создайте свой персональный план и добивайтесь успехов вместе с нашим ботом! 🏆",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Создать тренировку 🏋️‍♂️", callback_data="new_training")]
            ])
        )
    else:
        keyboard = create_reminders_keyboard()
        await message.answer("Выберите действие для напоминаний:", reply_markup=keyboard)


# Функция для отправки сообщения пользователю
async def send_notification(bot: Bot, user_id: int):
    await bot.send_message(chat_id=user_id, text=plan_for_today(user_id))


async def enable_notifications(callback_query: types.CallbackQuery, bot: Bot):
    user_id = callback_query.from_user.id

    for hour in hours:
        # Создание задачи на основе времени
        scheduler.add_job(
            send_notification,
            CronTrigger(hour=hour, minute=45),
            args=[bot, user_id],
            id=f"notification_{user_id}_{hour}",  # Уникальный ID задачи
            replace_existing=True                 # Заменить задачу, если ID совпадает
        )
    
    await callback_query.message.edit_text("Напоминания включены ✅\nТеперь они будут приходить вам каждый день в 08:00 и 18:00.")


async def disable_notifications(callback_query: types.CallbackQuery, bot: Bot):
    user_id = callback_query.from_user.id

    for hour in hours:
        try:
            # Удаление задачи на основе времени
            scheduler.remove_job(f"notification_{user_id}_{hour}")
        except JobLookupError:
            pass

    await callback_query.message.edit_text("Напоминания отключены ❌")

async def on_startup():
    scheduler.start()
