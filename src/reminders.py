from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.base import JobLookupError
from src.workout_survey import check_user_in_answers_set
import pandas as pd
import datetime
import time


# Пути к таблицам
EXCEL_FILE_TRAINING = "data/trainings.xlsx"
EXCEL_FILE_DIET = "data/diets.xlsx"

scheduler = AsyncIOScheduler()
notifications_enabled_users = set()

# Время отправки уведомлений
localtime_offset = time.localtime().tm_gmtoff // 3600
hours = (5+localtime_offset, 15+localtime_offset)


def check_user_in_reminders(user_id: int) -> bool:
    return user_id in notifications_enabled_users


def plan_for_today(user_id: int):
    # Создаём сообщение
    trainings_text = training_for_today(user_id)
    content = ""

    if pd.notna(trainings_text):
        content = "🏃‍♂️ Сегодня у вас запланирована тренировка:\n\n"
        content += trainings_text

    else:
        content = "Сегодня у вас не запланирована тренировка 🥱"
    
    content += "\n\n🍽 Рекомендации по питанию:\n\n"
    content += diet_for_today(user_id)
    
    return content


def diet_for_today(user_id: int):
    diets_df = pd.read_excel(EXCEL_FILE_DIET)

    diets_info = diets_df[diets_df["ID"] == user_id]

    diets_text = diets_info.iloc[0].get(datetime.datetime.today().strftime("%A").lower())

    return diets_text


def training_for_today(user_id: int):
    # Чтение файла
    trainings_df = pd.read_excel(EXCEL_FILE_TRAINING)

    # Строки с нужным ID
    trainings_info = trainings_df[trainings_df["ID"] == user_id]

    # План на сегодня
    trainings_text = trainings_info.iloc[0].get(datetime.datetime.today().strftime("%A").lower())

    return trainings_text


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
                [InlineKeyboardButton(text="Создать тренировку 🏋️‍♂️", callback_data="reminders_new_training")]
            ])
        )

    else:
        keyboard = create_reminders_keyboard()
        state_text = ""
        if check_user_in_reminders(user_id):
            state_text = "Статус ваших напоминаний:\nВключены ✅"
        else:
            state_text = "Статус ваших напоминаний:\nОтключены ❌"
        await message.answer(state_text + "\n\nВыберите действие:", reply_markup=keyboard)


# Функция для отправки сообщения пользователю
async def send_notification(bot: Bot, user_id: int, time_of_message: int):
    if time_of_message == hours[0]:
        await bot.send_message(chat_id=user_id, text=plan_for_today(user_id))

    else:
        trainings_text = training_for_today(user_id)

        if pd.notna(trainings_text) and check_user_in_answers_set(user_id):
            content = ("Вы уже прошли опрос после тренировки 🌟"
                       "\n\nНабирайтесь сил для следующего занятия и не забывайте про правильное питание!"
                       "\n\n🍽 Рекомендации по питанию:\n\n")
            content += diet_for_today(user_id)
            await bot.send_message(chat_id=user_id, text=content)

        elif pd.notna(trainings_text) and not check_user_in_answers_set(user_id):
            content = ("Вы ещё не прошли опрос после тренировки. Может хотите сделать это прямо сейчас?\n\n"
                       "❗️ Не забывайте фиксировать свою активность каждый день — так бот сможет помочь вам следить за достижениями")
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Пройти опрос 💬", callback_data="go_to_workout_survey")]])
            await bot.send_message(chat_id=user_id, text=content, reply_markup=keyboard)

        else:
            content = ("Тренировки сегодня нет, но это не повод забывать о правильном питании!"
                       "\n\n🍽 Рекомендации по питанию:\n\n")
            content += diet_for_today(user_id)
            await bot.send_message(chat_id=user_id, text=content)


async def enable_notifications(callback_query: types.CallbackQuery, bot: Bot):
    user_id = callback_query.from_user.id

    for hour in hours:
        # Создание задачи на основе времени
        scheduler.add_job(
            send_notification,
            CronTrigger(hour=hour, minute=0),
            args=[bot, user_id, hour],
            id=f"notification_{user_id}_{hour}",  # Уникальный ID задачи
            replace_existing=True                 # Заменить задачу, если ID совпадает
        )
    
    await callback_query.message.edit_text("Напоминания включены ✅\nТеперь они будут приходить вам каждый день в 08:00 и 18:00.")

    if not check_user_in_reminders(user_id):
        notifications_enabled_users.add(user_id)


async def disable_notifications(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    remove_notifications(user_id)

    await callback_query.message.edit_text("Напоминания отключены ❌")


def remove_notifications(user_id: int):
    for hour in hours:
        try:
            # Удаление задачи на основе времени
            scheduler.remove_job(f"notification_{user_id}_{hour}")
        except JobLookupError:
            pass
    
    if check_user_in_reminders(user_id):
        notifications_enabled_users.discard(user_id)


async def on_startup_reminders():
    scheduler.start()
